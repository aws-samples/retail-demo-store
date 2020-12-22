import boto3
import requests

import threading
import uuid
import os
import json
import logging
from datetime import datetime
from collections import defaultdict

GEOFENCE_PINPOINT_EVENTTYPE = 'LocationApproachLocalShop'

DISABLE_SEND_EMAIL = os.environ.get('DISABLE_SEND_EMAIL', "").lower() in ["yes", "true", "1"]
DISABLE_SEND_SMS = os.environ.get('DISABLE_SEND_SMS', "").lower() in ["yes", "true", "1"]

NOTIFICATION_ENDPOINT = os.environ.get('NotificationEndpointUrl').replace('wss://', 'https://')
WEBSOCKET_DYNAMO_TABLE_NAME = os.environ.get('WebsocketDynamoTableName')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

logger.info(f"DISABLE_SEND_EMAIL: {DISABLE_SEND_EMAIL}")
logger.info(f"DISABLE_SEND_SMS: {DISABLE_SEND_SMS}")

apigateway = boto3.client('apigatewaymanagementapi', endpoint_url=NOTIFICATION_ENDPOINT)
cognito_idp = boto3.client('cognito-idp')
dynamodb = boto3.client('dynamodb')
pinpoint = boto3.client('pinpoint')
servicediscovery = boto3.client('servicediscovery')

logger.info(f'Pinpoint region is {pinpoint.meta.region_name}')


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


def pinpoint_add_sms_endpoint_to_user(shopper_user_id, phone_number, source_channel_type='EMAIL', restrict_number=None):
    """
    If a user already exists in Pinpoint with certain "User Attributes", those attributes will be carried over to any
    other enpdoint we create for that user. In many applications therefore you just create a new endpoint and
    identify the user. However, "Attributes" are endpoint-specific, as are "Metrics". Therefore, we will attempt to
    carry these attributes and metrics (e.g. HasCart) over to the new phone endpoint from any email endpoints that
    have already been created in this application (at present these are set up by AmplifyAnalytics which has a
    limit of one endpoint per session).
    Args:
        shopper_user_id: Shopper User ID which Pinpoint uses internally.
        phone_number: E.g. '+90555555555'
        source_channel_type: E.g. 'EMAIL' - where to grab endpoint details from to propagate to SMS.
        restrict_number (int): Do not carry over more than this number of endpoints.

    Returns:
        Side effects in Pinpoint. No return.
    """
    pinpoint_app_id = os.environ['PinpointAppId']

    try:
        endpoints = pinpoint.get_user_endpoints(UserId=shopper_user_id, ApplicationId=pinpoint_app_id)

        # If the caller has requested that we sync to only certain endpoints (e.g. email)
        # We also only sync active endpoints
        endpoints = [endpoint_item for endpoint_item in endpoints['EndpointsResponse']['Item'] if
                     'ChannelType' in endpoint_item and endpoint_item['ChannelType'] == source_channel_type and
                     endpoint_item['EndpointStatus'].upper() == 'ACTIVE']

        if len(endpoints) > 1:
            logger.warning(f"More than one endpoint with email channel for shopper {shopper_user_id} - normally"
                           f" we'd expect just one. What we got: {json.dumps(endpoints)}")
        elif len(endpoints) == 0:
            logger.error(f"No {source_channel_type} endpoints for for shopper {shopper_user_id}."
                         f" Unable to carry attributes over to SMS endpoint.")
            return

        sms_endpoint_id = endpoints[0]['Id'] + "_sms"
    except pinpoint.exceptions.NotFoundException:
        logger.error(f"User {shopper_user_id} has no endpoints set. Unable to carry attributes over to SMS endpoint.")
        return

    if restrict_number is not None:
        if len(endpoints) > 1:
            logger.info(f"Removing {len(endpoints)-restrict_number} endpoints.")
            endpoints = endpoints[:restrict_number]

    # Grab all attributes and metrics from existing endpoints and get them ready to pop into the new endpoint
    attributes = {}
    metrics = {}
    for email_endpoint in endpoints:
        for attribute, value in email_endpoint["Attributes"].items():
            attributes[attribute] = value

        for metric, value in email_endpoint["Metrics"].items():
            metrics[metric] = value

    logger.info(
        f"Adding SMS endpoint to user {shopper_user_id} with phone {phone_number}"
        f" and additional attributes {attributes} and metrics {metrics}")
    pinpoint.update_endpoint(
        ApplicationId=pinpoint_app_id,
        EndpointId=sms_endpoint_id,
        EndpointRequest={
            'Address': phone_number,
            'ChannelType': 'SMS',
            "User": {"UserId": shopper_user_id},
            "Attributes": attributes,
            "Metrics": metrics
        }
    )


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


def pinpoint_add_current_cart_details_to_user(shopper_user_id, username, carts_service, products_service):
    """
    Fill Pinpoint User Attributes (against the user not endpoint) with information about 3 products that still
    exist in user carts.
    Args:
        shopper_user_id: E.g. "5999"  or "2e8fe504-c3e8-46e2-9e38-52bd1c7303fc" depending if profile user
                         user created from session login
        username: E.g. "user5999" or "cognitousername" depending if profile user
                        user created from session login
        carts_service: E.g. 'http://dmn-w-LoadB-1SM4DM9UFSIPZ-2136670231.us-east-1.elb.amazonaws.com'
        products_service: E.g. 'http://dmn-w-LoadB-1SM4DM9UFSIPZ-2136670231.us-east-1.elb.amazonaws.com'

    Returns:
        Nothing, but pinpoint user attributes updated.
    """

    # Get information we need to put
    carts = get_cart_products_with_details(username, carts_service, products_service)
    cart_products = []
    for cart in carts:
        if cart['items'] is not None:
            cart_products = cart_products + cart['items']

    new_user_attributes = {'CartProductImages': [product['details']['image_url'] for product in cart_products][:3],
                           'CartProductURLs': [product['details']['url'] for product in cart_products][:3],
                           'CartProductNames': [product['details']['name'] for product in cart_products][:3]}

    # Ensure we always have exactly 3
    new_user_attributes = {key: items + ['']*(3-len(items)) for key,items in new_user_attributes.items()}

    if len(carts) > 0:

        # OK let us fill this information.
        if sum(len(cart['items']) for cart in carts if cart['items'] is not None) > 0:

            pinpoint_app_id = os.environ['PinpointAppId']
            try:
                endpoints = pinpoint.get_user_endpoints(UserId=shopper_user_id, ApplicationId=pinpoint_app_id)
                endpoints = [endpoint_item for endpoint_item in endpoints['EndpointsResponse']['Item']]
                endpoint = endpoints[0]  # when adding user attributes only one endpoint is needed - they propagate
                pinpoint.update_endpoint(
                    ApplicationId=pinpoint_app_id,
                    EndpointId=endpoint['Id'],
                    EndpointRequest={
                        "User": {'UserId': shopper_user_id,
                                 'UserAttributes': new_user_attributes},
                    }
                )
                logger.info(f"Inserted into user {shopper_user_id} endpoint {endpoint['Id']}: {new_user_attributes}")
            except pinpoint.exceptions.NotFoundException:
                logger.warning(f"No endpoints found for user {shopper_user_id} - not adding cart details")
        else:
            logger.warning(f"User {shopper_user_id} has carts but no items: {carts}.")
    else:
        logger.info(f"User {shopper_user_id} has no carts.")


def send_email(to_email, subject, html_content, text_content):
    """
    Send a default email to the address. Pull pinpoint app ID and from address from env.
    More information about this service:
    https://docs.aws.amazon.com/pinpoint/latest/developerguide/send-messages-email.html
    Character set is UTF-8.
    Args:
        to_email: Email to send to
        subject: Subject of email
        html_content: HTML version of email content
        text_content: Plain text version of email content

    Returns:

    """

    if DISABLE_SEND_EMAIL:
        logger.warning('Send of email disabled')
        return

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
    Send a default SMS to the address. Pull pinpoint app ID and from address from env.
    More information about this service:
    https://docs.aws.amazon.com/pinpoint/latest/developerguide/send-messages-email.html
    Args:
        to_number (str): Phone number to send to.
        content: Message to send.

    Returns:

    """

    if DISABLE_SEND_SMS:
        logger.warning('Send of SMS disabled')
        return

    pinpoint_app_id = os.environ['PinpointAppId']
    response = pinpoint.send_messages(
        ApplicationId=pinpoint_app_id,
        MessageRequest={
            'Addresses': {
                to_number: {
                    'ChannelType': 'SMS'
                }
            },
            'MessageConfiguration': {
                'SMSMessage': {
                    'MessageType': 'TRANSACTIONAL',
                    'Body': content,
                    'SenderId': 'AWSRETAIL'
                }
            }
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


def get_cart_products_with_details(username, carts_service, products_service):
    """
    For the shopper with this ID grab her non-empty shopping carts and add more
    info about the products on the order with the products service.
    NOTE: there are some issues with the UI that means that shopping cart seen in UI might not match that
    recorded against the user.
    Args:
        username: E.g. "user5999" or "cognitousername" depending if profile user
                  user created from session login
        carts_service: E.g. 'http://dmn-w-LoadB-1SM4DM9UFSIPZ-2136670231.us-east-1.elb.amazonaws.com'
        products_service: E.g. 'http://dmn-w-LoadB-1SM4DM9UFSIPZ-2136670231.us-east-1.elb.amazonaws.com'

    Returns:
        A dictionary parsed from the json returned from the orders service - a list of dicts where each dict
        is an order. The order contains an "items" key also with a list of all the items. We augment this
        with info from the products service so we can get orders[:]["items"][:]["details"]["name"] for example.
    """

    # we can optionally retrive this from the user service if we want non-profile users:
    url = f'{carts_service}/carts/all'  # OK for demo else push up to carts repo

    logging.info(f'Hitting {url}')
    response = requests.get(url)
    carts = response.json()

    carts = [cart for cart in carts if cart['username'] == username]

    logger.info(f'Carts for user {username} is: {carts}')

    add_product_details_to_product_list(carts, products_service)

    logger.info(f'Carts for user {username} after adding details is: {carts}')

    return carts


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


def send_pickup_email(to_email, all_orders):
    """
    Take info about a waiting order and send it to customer saying ready for pickup as email
    Args:
        to_email: Where to send the email to
        orders: Orders as obtained from get_orders_with_details()
    Returns:
        Nothing but sends an email.
    """
    order_types = set(order['channel'] for order in all_orders)
    logger.info(f"Email: Order types: {','.join(order_types)}")
    for order_type in order_types:
        orders = [order for order in all_orders if order['channel'].lower()==order_type.lower()]
        if len(orders)==0: continue
        order_ids = ', '.join(['#'+str(order['id']) for order in orders])

        # Specify content:
        subject = "Come pick up your order nearby!"
        heading = "You can pick up your order nearby!"
        subheading = "Your order has been paid for with Amazon Pay."

        if order_type == 'alexa':
            intro_text = f"""
            Welcome, 
            Staff will be at the pump to deliver your order(s) ({order_ids}):"""
        else:
            intro_text = """
            Welcome, 
            We are waiting for you at Level 3, Door 2 of your Local Retail Demo Store, and Steve from our team will be greeting you with your following order(s): """
        html_intro_text = intro_text.replace('\n', '</p><p>')

        # Build the order list in text and HTML at the same time.
        html_orders = "<ul>"
        text_orders = ""
        for order in orders:
            ordername = f"Order #<b>{order['id']}</b>"
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

        logger.info(f"Email: Sending message with order type {order_type} and orders {order_ids} to {to_email}")
        logger.debug(f"Contents of email to {to_email} html: \n{html}")
        logger.debug(f"Contents of email to {to_email} text: \n{text}")
        send_email(to_email, subject, html, text)


def send_pickup_sms(to_number, all_orders, add_order_details=False):
    """
    Take info about a waiting order and send it to customer saying ready for pickup as email
    Args:
        to_number: Where to send the SMS to
        orders: Orders as obtained from get_orders_with_details()
        add_order_details: if True, add order IDs to message.
    Returns:
        Nothing but sends an SMS.
    """
    order_types = set(order['channel'] for order in all_orders)
    logger.info(f"SMS: Order types: {','.join(order_types)}")
    for order_type in order_types:
        orders = [order for order in all_orders if order['channel'].lower()==order_type.lower()]
        if len(orders)==0: continue
        order_ids = ', '.join(['#'+str(order['id']) for order in orders])

        if not add_order_details:
            if order_type == 'alexa':
                msg = "Staff will be at the pump to deliver your order."
            else:
                if len(orders) > 1:
                    msg = "Your orders are ready for pickup from your local AWS Retail Demo store, level 3, door 2."
                else:
                    msg = "Your order is ready for pickup from your local AWS Retail Demo Store, level 3, door 2."
        else:
            if order_type == 'alexa':
                msg = f"Staff will be at the pump to deliver your order ({order_ids})."
            else:

                msg = ""
                if len(orders) > 1:
                    msg += "The orders you placed with ids"
                else:
                    msg += "The order you placed with id"

                msg += order_ids

                if len(orders) > 1:
                    msg += " are "
                else:
                    msg += " is "

                msg += "ready for pickup from your local AWS retail demo store."

        logger.info(f"Contents of SMS text: {msg} to {to_number}")
        send_sms(to_number, msg)


def remove_connections(user_id, connection_ids):
    dynamo_key = {'userId': {'S': user_id}}
    dynamo_update_expression = {':c': {'SS': connection_ids}}
    logger.info(f"Deleting connection IDs {connection_ids} for user {user_id}")

    dynamodb.update_item(
        TableName=WEBSOCKET_DYNAMO_TABLE_NAME,
        Key=dynamo_key,
        UpdateExpression='DELETE connectionIds :c',
        ExpressionAttributeValues=dynamo_update_expression
    )
    logger.info(f"Gone connections deleted")


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
                    apigateway.post_to_connection(Data=data, ConnectionId=connection_id)
                except apigateway.exceptions.GoneException:
                    logger.info(f'Connection ID {connection_id} is gone, will remove.')
                    gone_connections.append(connection_id)
            if gone_connections:
                remove_connections(user_id, gone_connections)
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


def notify_waiting_orders(to_email, phone_number, orders):
    """
    User has some orders waiting so send an email and SMS to this effect.
    Args:
        to_email: Send email here
        phone_number: Send SMS here
        orders: Output of get_orders_with_details

    Returns:
        None.
        Sends email and SMS as side effect.
    """
    send_pickup_email(to_email, orders)
    if phone_number is not None:
        send_pickup_sms(phone_number, orders)


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
    user_attributes = {att['Name']: att['Value'] for att in response['UserAttributes']}
    to_email = user_attributes['email']
    phone_number = user_attributes.get('phone_number', None)
    if phone_number is None:
        logger.warning(f"User {cognito_user_id} has no phone number - SMS will not work till they add one from the UI.")

    try:
        first_name = user_attributes['custom:profile_first_name']
    except KeyError:
        first_name = 'Madam/Sir'
        logger.warning(f'No first name for user {cognito_user_id} - defaulting to "{first_name}"')

    try:
        last_name = user_attributes['custom:profile_last_name']
    except KeyError:
        last_name = ''
        logger.warning(f'No last name for user {cognito_user_id} - defaulting to "{last_name}"')

    try:
        shopper_user_id = user_attributes['custom:profile_user_id']
    except KeyError:
        logger.error(f'No profile (shopper) ID for {cognito_user_id} - quitting event handling.')
        return

    try:
        demo_journey = user_attributes['custom:demo_journey']
        logger.info(f'User has demo_journey attribute: {demo_journey}')
    except KeyError:
        demo_journey = 'PURCHASE'
        logger.warning(f'No demo journey configured for user {cognito_user_id} - defaulting to PURCHASE')

    # Grab the service URLs.
    orders_service = get_orders_service()
    carts_service = get_carts_service()
    products_service = get_products_service()
    users_service = get_users_service()
    username = userid_to_username(shopper_user_id, users_service)

    if demo_journey == 'PURCHASE':

        # In case we want to show users details of items in their cart, we add them as Pinpoint User Attributes
        pinpoint_add_current_cart_details_to_user(shopper_user_id, username, carts_service, products_service)

        # Update pinpoint to have an SMS endpoint for the user
        # carrying attributes over from any email endpoint that may have been created
        # by AmplifyAnalytics client side (AmplifyAnalytics maintains one endpoint at a time).
        # This way, any campaigns for SMS will work also same as email.
        if phone_number is not None:
            pinpoint_add_sms_endpoint_to_user(shopper_user_id, phone_number, source_channel_type='EMAIL')

        # If there are any Pinpoint campaigns waiting for Location events of type parametrised
        # by GEOFENCE_PINPOINT_EVENTTYPE (see defined at top)
        # They should get triggered for all endpoints for this user:
        pinpoint_fire_location_approached_event(shopper_user_id, event['detail']['SampleTime'])
        send_purchase_browser_notification(cognito_user_id)

    elif demo_journey == 'COLLECTION':

        # Get a list of waiting orders.
        orders = get_orders_with_details(username, orders_service, products_service)
        send_pickup_browser_notification(cognito_user_id, orders)

        if len(orders) > 0:
            logger.info(f'User {shopper_user_id}/{username} has waiting orders')
            logger.info(f"Going to send a message to {to_email} and {phone_number} "
                        f"for user {first_name} {last_name} ({shopper_user_id}/{username})")
            notify_waiting_orders(to_email, phone_number, orders)


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
