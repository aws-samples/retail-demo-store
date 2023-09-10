# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import boto3
import requests

import threading
import uuid
import os
import json
import logging
from datetime import datetime
from collections import defaultdict

# The event type we send to Pinpoint to initiate campaigns
GEOFENCE_PINPOINT_EVENTTYPE = 'LocationApproachLocalShop'

# Used for real-time notifications to browser
NOTIFICATION_ENDPOINT = os.environ.get('NotificationEndpointUrl').replace('wss://', 'https://')
WEBSOCKET_DYNAMO_TABLE_NAME = os.environ.get('WebsocketDynamoTableName')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS services setup
apigateway = boto3.client('apigatewaymanagementapi', endpoint_url=NOTIFICATION_ENDPOINT)
cognito_idp = boto3.client('cognito-idp')
dynamodb = boto3.client('dynamodb')
pinpoint = boto3.client('pinpoint')
servicediscovery = boto3.client('servicediscovery')
ssm = boto3.client('ssm')

logger.info(f'Pinpoint region is {pinpoint.meta.region_name}')


def get_long_code():
    response = ssm.get_parameter(Name='retaildemostore-pinpoint-sms-longcode')
    pinpoint_sms_long_code = response['Parameter']['Value']

    if pinpoint_sms_long_code == 'NONE':
        return None
    return pinpoint_sms_long_code


def userid_to_username(user_id, users_service):
    """
    Use the users service to map a User ID (which might be a shopper user or one based on a provisional session ID
    but later added on signup) to the username (which might be "userXXXX where XXXX was the shopper user ID
    or the cognito username)
    Args:
        user_id: E.g. '5999' for a shopper user or '2e8fe504-c3e8-46e2-9e38-52bd1c7303fc' for a user transferred
                 from a non-login session
        users_service: URL to pull user from (users service)

    Returns:
        The relevant username which is useful to look up stuff against e.g. the carts service
    """
    user_url = f'{users_service}/users/id/{user_id}'
    try:
        logging.info(f'Hitting {user_url} for user info to map user ID to username.')
        response = requests.get(user_url)
        user = response.json()
    except requests.exceptions.ConnectionError:
        logger.warning(f'Could not retrieve {user_url}')
        return 'user' + user_id
    username = user['username']
    logging.info(f"User ID {user_id} --> username {username}")
    return username


def get_user_opted_phone_number(shopper_user_id):
    """If a user has opted in to SMS we can grab their phone number.
    Note that the opt-in for these SMSs is for promotional messages.
    Since in our demo all promotional SMSs are sent through Pinpoint campaigns
    we generally do not need to get the phone number this way."""
    pinpoint_app_id = os.environ['PinpointAppId']

    try:
        endpoints = pinpoint.get_user_endpoints(UserId=shopper_user_id, ApplicationId=pinpoint_app_id)

    except pinpoint.exceptions.NotFoundException:
        logger.error(f"User {shopper_user_id} has no endpoints set. Unable to get phone number.")
        return None
    print('All user endpoints: ', json.dumps(endpoints, indent=4))
    endpoints = [endpoint_item for endpoint_item in endpoints['EndpointsResponse']['Item'] if
                 'ChannelType' in endpoint_item and endpoint_item['ChannelType'] == 'SMS' and
                 endpoint_item['EndpointStatus'].upper() == 'ACTIVE' and endpoint_item['OptOut'] == 'NONE']
    if len(endpoints) > 0:
        if len(endpoints) > 1:
            logger.warning(f'User has more than 1 SMS endpoint: {endpoints}')
        return endpoints[0]['Address']
    else:
        logger.error(f"User {shopper_user_id} has no SMS opted in endpoints set. Unable to get phone number.")
        return None


def pinpoint_fire_location_approached_event(shopper_user_id, event_timestamp_iso=None, restrict_to_endpoint_types=None,
                                            restrict_number=None):
    """
    We fire an event in Pinpoint with name parametrised by GEOFENCE_PINPOINT_EVENTTYPE for all endpoints
    associated with this user. This enables campaigns based on location events.
    Args:
        shopper_user_id (str): Shopper User ID which Pinpoint uses internally.
        event_timestamp_iso (Optional[str]): If null current timestamp is used otherwise stamps the event with this.
        restrict_to_endpoint_types (Optional[list]): If not None, the channel types to send events for.
        restrict_number (int): Do not fire for more than more than this number of endpoints
                               for each channel type/address.

    Returns:
        None.
    """
    pinpoint_app_id = os.environ['PinpointAppId']
    try:
        endpoints = pinpoint.get_user_endpoints(UserId=shopper_user_id, ApplicationId=pinpoint_app_id)
        endpoints = endpoints['EndpointsResponse']['Item']
        logger.info(f'Endpoints for {shopper_user_id} are {endpoints}')
    except pinpoint.exceptions.NotFoundException:
        logger.warning(f"No endoints found for user {shopper_user_id} - no location event fire")
        return

    if restrict_number is not None:
        # Sometimes your Analytics may put unnecessary endpoints in to Pinpoint - for example, one for each session
        # but with the same address - we ensure that each address only has one endpoint event fired.
        removed = []
        kept = defaultdict(list)
        for endpoint in endpoints:
            if 'ChannelType' in endpoint:
                channel_type = endpoint['ChannelType']
            else:
                channel_type = 'unk'
            if 'Address' in endpoint:
                addr = endpoint['Address']
            else:
                addr = 'unk'
            if endpoint['EndpointStatus'].upper() == 'ACTIVE' and len(kept[(channel_type, addr)]) < restrict_number:
                kept[(channel_type, addr)].append(endpoint)
            else:
                removed.append(endpoint)
                logger.info(f"Dropping endpoint with Id {endpoint['Id']}")
        if len(removed) > 0:
            logger.info(f"Dropped {len(removed)} endpoints.")
        endpoints = []
        for endpointlist in kept.values():
            endpoints += endpointlist

    endpoint_ids = [endpoint['Id'] for endpoint in endpoints
                    if restrict_to_endpoint_types is None or
                    ('ChannelType' in endpoint and endpoint['ChannelType'] in restrict_to_endpoint_types)]

    if event_timestamp_iso is None:
        timestamp = datetime.now().isoformat()
    else:
        timestamp = event_timestamp_iso

    sess_id = str(uuid.uuid4())

    events = {endpoint_id: {'Endpoint': {},  # We need to provide this but empty because not here to update endpoint
                            'Events': {endpoint_id:  # API docs state this is the endpoint ID too
                                       {'EventType': GEOFENCE_PINPOINT_EVENTTYPE,
                                        'Session': {'Id': sess_id, 'StartTimestamp': timestamp},  # required
                                        'Timestamp': timestamp}}}  # required
              for endpoint_id in endpoint_ids}

    if len(events) > 0:
        logger.info(f'Firing Pinpoint events: {events}')
        pinpoint.put_events(
            ApplicationId=pinpoint_app_id,
            EventsRequest={
                'BatchItem': events
            }
        )
    else:
        logger.warning(f'Did not fire any location events for user {shopper_user_id} in app {pinpoint_app_id}')


def send_email(to_email, subject, html_content, text_content):
    """
    Send a default email to the address using Pinpoint transactional messaging.
    Pull pinpoint app ID and from address from env.
    More information about this service:
    https://docs.aws.amazon.com/pinpoint/latest/developerguide/send-messages-email.html
    Character set is UTF-8.
    Args:
        to_email: Email to send to
        subject: Subject of email
        html_content: HTML version of email content
        text_content: Plain text version of email content

    Returns:
        None
    """
    pinpoint_app_id = os.environ['PinpointAppId']
    response = pinpoint.send_messages(
        ApplicationId=pinpoint_app_id,
        MessageRequest={
            'Addresses': {
                to_email: {
                    'ChannelType': 'EMAIL'
                }
            },
            'MessageConfiguration': {
                'EmailMessage': {
                    'SimpleEmail': {
                        'Subject': {
                            'Charset': "UTF-8",
                            'Data': subject
                        },
                        'HtmlPart': {
                            'Charset': "UTF-8",
                            'Data': html_content
                        },
                        'TextPart': {
                            'Charset': "UTF-8",
                            'Data': text_content
                        }
                    }
                }
            }
        }
    )
    logger.info(f'Message sent to {to_email} and response: {response}')


def send_sms(to_number, content):
    """
    Send a default SMS to the address using Pinpoint transactional messaging.
    Pull pinpoint app ID and from address from env.
    More information about this service:
    https://docs.aws.amazon.com/pinpoint/latest/developerguide/send-messages-email.html
    Args:
        to_number (str): Phone number to send to.
        content: Message to send.

    Returns:
        None
    """

    long_code = get_long_code()
    message_config = {
        'SMSMessage': {
            'MessageType': 'TRANSACTIONAL',
            'Body': content
        }
    }
    if long_code:
        logger.info(f"Using long code {long_code} to send SMS to {to_number}. Content starts with '{content[:10]}'")
        message_config['SMSMessage']['OriginationNumber'] = long_code

    pinpoint_app_id = os.environ['PinpointAppId']
    response = pinpoint.send_messages(
        ApplicationId=pinpoint_app_id,
        MessageRequest={
            'Addresses': {
                to_number: {
                    'ChannelType': 'SMS'
                }
            },
            'MessageConfiguration': message_config
        }
    )
    logger.info(f'Message sent to {to_number} and response: {response}')


def get_service(environ_key, get_local_ip=False, local_servicename=None):
    """
    Gets the service from relevant environment key but potentially can grab the internal IP from
    the service discovery as well.
    Args:
        environ_key: Check here for the service if either cannot find local IP or get_local_ip is False
        get_local_ip: If true, use first servicediscovery to find the service
        local_servicename: if using service discover, look for this service name.

    Returns:
        URL of the service. E.g.
            'http://dmn-w-LoadB-1SM4DM9UFSIPZ-2136670231.us-east-1.elb.amazonaws.com'
    """
    if get_local_ip:
        try:
            response = servicediscovery.discover_instances(
                NamespaceName='retaildemostore.local',
                ServiceName=local_servicename,
                MaxResults=1,
                HealthStatus='HEALTHY'
            )
            service_instance = response['Instances'][0]['Attributes']['AWS_INSTANCE_IPV4']
            response = requests.get('http://{service_instance}/')
            return 'http://' + service_instance
        except requests.exceptions.ConnectionError:
            # For local development
            logger.debug('Could not pick up Local IP for orders service. Looking at environment')

    service_instance = os.environ[environ_key]
    return service_instance


def get_users_service(get_local_ip=False):
    """
    Get the URL of the orders service
    Args:
        get_local_ip: If true obtains the internal IP using service discovery

    Returns:
        URL of the orders service.
    """
    return get_service('UsersServiceExternalUrl', get_local_ip, 'users')


def get_orders_service(get_local_ip=False):
    """
    Get the URL of the orders service
    Args:
        get_local_ip: If true obtains the internal IP using service discovery

    Returns:
        URL of the orders service.
    """
    return get_service('OrdersServiceExternalUrl', get_local_ip, 'orders')


def get_carts_service(get_local_ip=False):
    """
    Get the URL of the carts service
    Args:
        get_local_ip: If true obtains the internal IP using service discovery

    Returns:
        URL of the carts service.
    """
    return get_service('CartsServiceExternalUrl', get_local_ip, 'carts')


def get_products_service(get_local_ip=False):
    """
    Get the URL of the products service
    Args:
        get_local_ip: If true obtains the internal IP using service discovery

    Returns:
        URL of the products service.
    """
    return get_service('ProductsServiceExternalUrl', get_local_ip, 'products')


def add_product_details(products_service, product):
    """
    Use products service to add details to product record. Thread-safe because working in pure Python.
    Args:
        product: Product dictionary. Contains at least product_id. details key to be added with additional details.

    Returns:
        No return.
    """

    product_id = product['product_id']
    products_url = f'{products_service}/products/id/{product_id}'
    try:
        logging.info(f'Hitting {products_url} for product details to add to order.')
        response = requests.get(products_url)
        product['details'] = response.json()
        # Latest product service behaviour makes product service responsible for
        # adding in URL root - this may change in the future
        if product['details']['image'].lower().startswith('http://'):
            base = ''
        else:
            base = os.environ['WebURL'] + '/images/' + product['details']['category'] + '/'
        product['details']['image_url'] = base + product['details']['image']
    except requests.exceptions.ConnectionError:
        logger.warning(f'Could not retrieve {products_url}')


def add_product_details_to_product_list(orders, products_service):
    """
    Fill in product details on an order using the products service
    Args:
        orders: Order structure as returned from the orders service
        products_service: The URL to hit for product details

    Returns:
        Nothing but when returned, orders[:][ITEM_ID]['detail'] will contain product details
    """

    # Let's get these products in parallel so not to waste time waiting for them all.
    jobs = []
    for order in orders:
        if order['items'] is not None:
            for product in order['items']:
                thread = threading.Thread(target=add_product_details, args=(products_service, product))
                thread.start()
                jobs.append(thread)

    for thread in jobs:
        thread.join()


def get_orders_with_details(username, orders_service, products_service):
    """
    For the shopper with this ID grab her/his orders which are awaiting collection from the orders service and add more
    info about the products on the order with the products service
    Args:
        username: E.g. "user5999" or "cognitousername" depending if profile user
                  user created from session login
        orders_service: E.g. 'http://dmn-w-LoadB-1SM4DM9UFSIPZ-2136670231.us-east-1.elb.amazonaws.com'
        products_service: E.g. 'http://dmn-w-LoadB-1SM4DM9UFSIPZ-2136670231.us-east-1.elb.amazonaws.com'

    Returns:
        A dictionary parsed from the json returned from the orders service - a list of dicts where each dict
        is an order. The order contains an "items" key also with a list of all the items. We augment this
        with info from the products service so we can get orders[:]["items"][:]["details"]["name"] for example.
    """
    # we can optionally retrive this from the user service if we want non-profile users:

    orders_url = f'{orders_service}/orders/username/{username}'
    logging.info(f'Hitting {orders_url}')
    response = requests.get(orders_url)
    orders = response.json()
    awaiting_collection_orders = [order for order in orders if order['delivery_status'] != 'COMPLETE'
                                  and order['delivery_type'] == 'COLLECTION']

    add_product_details_to_product_list(awaiting_collection_orders, products_service)
    logger.info(f'Orders for user {username} is: {awaiting_collection_orders}')

    return awaiting_collection_orders


def send_pickup_email(to_email, orders):
    """
    Take info about a waiting order and send it to customer saying ready for pickup as email
    Args:
        to_email: Where to send the email to
        orders: Orders as obtained from get_orders_with_details()
    Returns:
        Nothing but sends an email.
    """
    logger.info(f"Going to send an email to {to_email}.")
    # Specify content:
    subject = "Come pick up your order nearby!"
    heading = "You can pick up your order nearby!"
    subheading = ""
    intro_text = """
    Welcome, 
    We are waiting for you at Level 3, Door 2 of your Local Retail Demo Store, and Steve from our team will be greeting you with your following order(s): """
    html_intro_text = intro_text.replace('\n', '</p><p>')

    # Build the order list in text and HTML at the same time.
    html_orders = "<ul>"
    text_orders = ""
    for order in orders:
        ordername = f"Order #{order['id']}"
        html_orders += f"\n  <li>{ordername}:<ul>"
        text_orders += f'\n{ordername}:'
        for item in order['items']:
            img_url = item["details"]["image_url"]
            url = item["details"]["url"]
            name = item["details"]["name"]
            html_orders += F'\n    <li><a href="{url}">{name}</a> - ${item["price"]}<br/><a href="{url}"><img src="{img_url}" width="100px"></a></br></a></li>'
            text_orders += f'\n  - {item["details"]["name"]}: {item["details"]["url"]}'
        html_orders += "\n  </ul></li>"
    html_orders += "\n</ul>"

    # Build HTML message
    html = f"""
    <head></head>
    <body>
        <h1>{heading}</h1>
        <h2>{subheading}</h2>
        <p>{html_intro_text}
        {html_orders}
        <p><a href="{os.environ['WebURL']}">Thank you for shopping!</a></p>
    </body>
    """

    # Build text message
    text = f"""
{heading}
{subheading}
{intro_text}
{text_orders}
Thank you for shopping!
{os.environ['WebURL']}
    """

    logger.debug(f"Contents of email to {to_email} html: \n{html}")
    logger.debug(f"Contents of email to {to_email} text: \n{text}")
    send_email(to_email, subject, html, text)


def send_pickup_sms(all_orders, add_order_details=False):
    """
    Take info about a waiting order and send it to customer saying ready for pickup as SMS
    Picks the phone number off orders themselves
    Args:
        orders: Orders as obtained from get_orders_with_details()
        add_order_details: if True, add order IDs to message.
    Returns:
        Nothing but sends an SMS.
    """
    logger.info("Collecting phone numbers to send SMSs")

    phone_to_orders = defaultdict(list)
    for order in all_orders:
        phone_to_orders[order['collection_phone']] += [order]

    for to_number, orders in phone_to_orders.items():

        logger.info(f"Going to send a text message to {to_number}")

        if not add_order_details:
            if len(orders) > 1:
                msg = "Your orders are ready for pickup from your local AWS Retail Demo store, level 3, door 2."
            else:
                msg = "Your order is ready for pickup from your local AWS Retail Demo Store, level 3, door 2."
        else:
            msg = ""
            if len(orders) > 1:
                msg += "The orders you placed with ids"
            else:
                msg += "The order you placed with id"

            msg += ",".join(" #" + order['id'] for order in orders)

            if len(orders) > 1:
                msg += " are "
            else:
                msg += " is "

            msg += "ready for pickup from your local AWS retail demo store."

        logger.info(f"Contents of SMS text: {msg} to {to_number}")
        try:
            send_sms(to_number, msg)
        except Exception as e:
            logger.error(f'Could not send to {to_number} message: {msg} - exception: {e}')


def remove_browser_notification_connections(user_id, connection_ids):
    dynamo_key = {'userId': {'S': user_id}}
    dynamo_update_expression = {':c': {'SS': connection_ids}}
    logger.info(f"Deleting connection IDs {connection_ids} for user {user_id}")

    dynamodb.update_item(
        TableName=WEBSOCKET_DYNAMO_TABLE_NAME,
        Key=dynamo_key,
        UpdateExpression='DELETE connectionIds :c',
        ExpressionAttributeValues=dynamo_update_expression
    )
    logger.info("Gone connections deleted")


def send_browser_notification(user_id, data):
    """
    Sends messages to all WebSocket connections associated with a Cognito user
    Args:
        user_id: Cognito username
        data: Data to be sent to connection (bytes-like)
    """
    dynamo_entry = dynamodb.get_item(
        TableName=WEBSOCKET_DYNAMO_TABLE_NAME,
        Key={
            'userId': {'S': user_id}
        }
    )

    if 'Item' in dynamo_entry:
        logger.info(f'Retrieved connection table entry: {dynamo_entry["Item"]}')
        gone_connections = []
        if 'connectionIds' in dynamo_entry['Item']:
            for connection_id in dynamo_entry['Item']['connectionIds']['SS']:
                try:
                    logger.info(f'Posting to connection ID: {connection_id}')
                    apigateway.post_to_connection(Data=data, ConnectionId=connection_id)
                except apigateway.exceptions.GoneException:
                    logger.info(f'Connection ID {connection_id} is gone, will remove.')
                    gone_connections.append(connection_id)
            if gone_connections:
                remove_browser_notification_connections(user_id, gone_connections)
    else:
        logger.info(f'No active WebSocket connections found for user {user_id}. No browser notifications sent.')


def send_pickup_browser_notification(user_id, orders):
    """
    Sends messages to all WebSocket connections associated with a Cognito user
    Args:
        user_id: Cognito username
        orders: Orders awaiting collection
    """
    logger.info(f'Sending collection notification to browsers for user {user_id}')
    send_browser_notification(user_id, f'{{"EventType": "COLLECTION", "Orders": {json.dumps(orders)}}}')


def send_purchase_browser_notification(user_id):
    """
    Sends messages to all WebSocket connections associated with a Cognito user
    Args:
        user_id: Cognito username
    """
    logger.info(f'Sending purchase notification to browsers for user {user_id}')
    send_browser_notification(user_id, '{"EventType": "PURCHASE"}')


def handle_geofence_enter(event):
    """
    Somebody has entered the geofence. We handle it.
    Args:
        event: See the lambda_handler docstring for the kind of structure we might expect. Examples are there.

    Returns:
        None.
    """
    location_device_id = event['detail']['DeviceId']
    # If there are multiple geofences, it is possible to learn which geofence by inspecting the event
    # at event['detail']['GeofenceID']
    # and event['detail']['GeofenceCollectionARN']
    # We currently assume that there is only one Geofence Collection associated with the tracker.

    # We can get the geofence collection description by using the GeofenceCollectionID to hit the
    # geofence service.

    # Here we trust the sending party to not be sending us the wrong user ID.
    cognito_user_id = location_device_id

    user_pool_id = os.environ['UserPoolId']  # Cognito user pool for retail demo store.

    response = cognito_idp.admin_get_user(
        UserPoolId=user_pool_id,
        Username=cognito_user_id
    )

    # Grab the user attributes as a dictionary and pull relevant ones.
    cognito_user_attributes = {att['Name']: att['Value'] for att in response['UserAttributes']}

    try:
        shopper_user_id = cognito_user_attributes['custom:profile_user_id']
    except KeyError:
        logger.error(f'No profile (shopper) ID for {cognito_user_id} - quitting event handling.')
        return

    try:
        demo_journey = cognito_user_attributes['custom:demo_journey']
        logger.info(f'User has demo_journey attribute: {demo_journey}')
    except KeyError:
        demo_journey = 'PURCHASE'
        logger.warning(f'No demo journey configured for user {cognito_user_id} - defaulting to {demo_journey}')

    # Grab the service URLs.
    orders_service = get_orders_service()
    products_service = get_products_service()
    users_service = get_users_service()

    if demo_journey == 'PURCHASE':

        # If there are any Pinpoint campaigns waiting for Location events of type parametrised
        # by GEOFENCE_PINPOINT_EVENTTYPE (see defined at top)
        # They should get triggered for all endpoints for this user:
        pinpoint_fire_location_approached_event(shopper_user_id, event['detail']['SampleTime'])
        # The implementation for browser push is custom (though Apple, iOS and Android push can be also done
        # with Pinpoint campaigns).
        send_purchase_browser_notification(cognito_user_id)

    elif demo_journey == 'COLLECTION':

        to_email = cognito_user_attributes['email']

        try:
            first_name = cognito_user_attributes['custom:profile_first_name']
        except KeyError:
            first_name = 'Madam/Sir'
            logger.warning(f'No first name for user {cognito_user_id} - defaulting to "{first_name}"')

        try:
            last_name = cognito_user_attributes['custom:profile_last_name']
        except KeyError:
            last_name = ''
            logger.warning(f'No last name for user {cognito_user_id} - defaulting to "{last_name}"')

        # Get a list of waiting orders.
        username = userid_to_username(shopper_user_id, users_service)
        orders = get_orders_with_details(username, orders_service, products_service)

        if len(orders) > 0:
            logger.info(f'User {shopper_user_id}/{username} (name {first_name} {last_name}) has waiting orders')
            send_pickup_email(to_email, orders)
            send_pickup_sms(orders)  # phone number is recorded against the order
            send_pickup_browser_notification(cognito_user_id, orders)
    else:
        logger.error(f'Not a known journey type {demo_journey} for user {shopper_user_id}')


def lambda_handler(event, context):
    """
    Lambda function to handle geofence enter exit events for retail demo store.

    Here is the structure of a Location enter event (an exit event also exists):

        {
            "version": "0",
            "id": "12345678-9abc-def0-1234-56789abcdef0",
            "detail-type": "Location Geofence Event",
            "source": "aws.geo",
            "account": "YOUR_ACCOUNT_ID",
            "time": "2020-11-23T14:30:33Z",
            "region": "us-east-1",
            "resources": [
                "arn:aws:geo:us-east-1:YOUR_ACCOUNT_ID:geofence-collection/COLLECTIONID",
                "arn:aws:geo:us-east-1:YOUR_ACCOUNT_ID:tracker/TRACKERID"
            ],
            "detail": {
                "EventType": "ENTER",
                "GeofenceId": "GEOFENCEID",
                "DeviceId": "FILL_THIS_IN: WE_USE_COGNITO_USER",
                "SampleTime": "2020-11-23T14:30:32.867Z",
                "Position": [-100,50]
            }
        }

    Args:
        event: See the example above
        context: Information such as the Python version,
                 logging group https://docs.aws.amazon.com/lambda/latest/dg/python-context.html .
                 Ignored here

    Returns:
        This function is called as events received from EventBridge.
        There is not much point in returning something. Fire and forget.
    """
    logger.info('ENVIRONMENT VARIABLES')
    logger.info(os.environ)
    logger.info('EVENT')
    logger.info(event)

    if float(event['version']) != 0:
        logger.warning(f"Getting event structure for Location event of non-known version: {event}")

    if event['detail-type'] == 'Location Geofence Event':
        if event['detail']['EventType'] != 'ENTER':
            logger.warning(f"Event detail type {event['detail-type']} EventType"
                           f" {event['detail']['EventType']} - not handled.")
            return
        handle_geofence_enter(event)

    else:
        logger.error(f"Unhandled event type {event['detail-type']}")
        return
