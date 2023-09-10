# -*- coding: utf-8 -*-
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

# Back-end handler for the C-store demonstration in Retail Demo Store.
# Can make use of Cognito authenticated Retail Demo Store users
# for retrieving user details, putting orders and sending emails.

# Check the docstrings in the intents below for information on how each of them works
# For background see
#   https://developer.amazon.com/en-US/docs/alexa/custom-skills/understanding-custom-skills.html
#   https://developer.amazon.com/en-US/docs/alexa/custom-skills/host-a-custom-skill-as-an-aws-lambda-function.html

import ask_sdk_core.utils as ask_utils

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler

from ask_sdk_model.dialog import ElicitSlotDirective, DynamicEntitiesDirective, DelegateDirective
from ask_sdk_model.dialog_state import DialogState
from ask_sdk_model.er.dynamic import Entity, EntityValueAndSynonyms, EntityListItem, UpdateBehavior
from ask_sdk_model.slu.entityresolution import StatusCode


import boto3
import json
import logging
import os
from typing import Tuple
import random
from urllib.request import Request, urlopen
from botocore.exceptions import ClientError

from dotenv import load_dotenv

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

load_dotenv()

CARTS_SERVICE_URL = os.environ.get('CartsServiceExternalUrl')
ORDER_SERVICE_URL = os.environ.get('OrdersServiceExternalUrl')
PRODUCT_SERVICE_URL = os.environ.get('ProductsServiceExternalUrl')
RECOMMENDATIONS_SERVICE_URL = os.environ.get('RecommendationsServiceExternalUrl')
LOCATION_SERVICE_URL = os.environ.get('LocationServiceExternalUrl')

PINPOINT_APP_ID = os.environ.get('PinpointAppId')
COGNITO_DOMAIN = os.environ.get('COGNITO_DOMAIN')
LOCATION_PLACE_INDEX_NAME = os.environ.get('LocationResourceName')

PRODUCT_CATEGORIES = ['food service', 'salty snacks', 'hot dispensed', 'cold dispensed']

SANDBOX_CUSTOMER_EMAIL = os.environ.get('AlexaDefaultSandboxEmail', '').strip()

pinpoint = boto3.client('pinpoint')
location = boto3.client('location')


def get_nice_address(address):
    """
    Take address returned by Location Service and make it nice for speaking.
    Args:
        address: Address as returned by Location Service Place Index.

    Returns:
        str: Spoken address.
    """
    spoken_street = address['Street']
    if spoken_street.endswith('St'):
        spoken_street+= 'reet'
    if spoken_street.endswith('Av'):
        spoken_street += 'enue'

    spoken_number = address['AddressNumber']
    if len(spoken_number) >= 4:
        spoken_number = spoken_number[:2] + ' ' + spoken_number[2:]

    spoken_address = spoken_number + " " + spoken_street
    return spoken_address


def get_cognito_user_details(handler_input):
    """
    Get user information back from connected Cognito user.
    Uses the access token that Alexa manages for you to pull user information from Cognito.
    This needs you to have followed the instructions to setup Alexa to obtain and manage your Cognito access tokens.
    Note that the skill developer does not need to manage the tokens - this is handled by Alexa and Alexa obtains
    the access token from Cognito as user authorizes Cognito.
    This process is well-explained here:
    https://developer.amazon.com/en-US/blogs/alexa/alexa-skills-kit/2019/11/how-to-set-up-alexa-account-linking-with-amazon-cognito-user-pools-to-create-a-personalized-customer-experience

    Args:
        handler_input: The data structure as passed from Alexa to the skill.

    Returns:
        dict: User details, from Cognito if available, otherwise default with default email from
              CloudFormation.
    """

    session_attr = handler_input.attributes_manager.session_attributes
    if 'CognitoUser' in session_attr:
        return session_attr['CognitoUser']

    try:
        if COGNITO_DOMAIN is None:
            raise Exception("No Cognito domain supplied.")
        access_token = handler_input.request_envelope.context.system.user.access_token
        url = f"{COGNITO_DOMAIN}/oauth2/userInfo"
        logger.info(f"Obtaining user info from {url}")
        req = Request(url)
        req.add_header('Authorization', f'Bearer {access_token}')
        user_details = json.loads(urlopen(req).read().decode('utf-8'))
        logger.info(f"Got user info from Cognito: {user_details}")

        if 'custom:profile_user_id' not in user_details:
            logger.warning("Profile user has not been selected for Cognito user")
            raise Exception("Must use default user because simulation user not selected.")
        else:
            user_details['cognito_loaded'] = True

    except Exception as e:
        # Here, we allow for easy testing without having to do the authentication of Alexa with Cognito
        # This is important if you want to test Retail Demo Store on the web because only the mobile app
        # allows you to grab the authentication token from another provider
        # If there is a tester email set up with SANDBOX_CUSTOMER_EMAIL in .env
        # we use that for emails, otherwise you will unfortunately not
        # receive any emails.
        user_details = {
            'username': 'guest',
            'custom:profile_user_id': '0',
            'custom:profile_first_name': 'Testy',
            'custom:profile_last_name': 'McTest',
            'email': SANDBOX_CUSTOMER_EMAIL,
            'cognito_loaded': False
        }
        logger.info(f"Default user details retrieved: {user_details} - exception: {e}")

    session_attr['CognitoUser'] = user_details
    return user_details


def send_email(to_email: str, subject: str, html_content: str, text_content: str) -> None:
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
        None
    """

    email_enabled = is_pinpoint_email_channel_enabled()
    if (email_enabled):
        pinpoint_app_id = PINPOINT_APP_ID

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
    else:
        logger.info('Pinpoint Email Channel not setup, skipping sending email')

def is_pinpoint_email_channel_enabled() -> bool:
    """
    Determines whether an email channel has been setup in Pinpoint

    Returns:
        bool: True if email channel is setup in Pinpoint, else False
    """
    if not PINPOINT_APP_ID:
        logger.info('Pinpoint App ID not setup in Cloudformation Template')
        return False

    try:
        email_channel_response = pinpoint.get_email_channel(ApplicationId=PINPOINT_APP_ID)
    except ClientError as error:
        logger.info('Unable to find Email Channel configured for Pinpoint application: {}'.format(error))
        return False 

    email_channel_from_address = None
    email_channel_enabled = False
    if email_channel_response['EmailChannelResponse']:
        email_channel_from_address = email_channel_response['EmailChannelResponse']['FromAddress']
        email_channel_enabled = email_channel_response['EmailChannelResponse']['Enabled']

    return email_channel_from_address is not None and email_channel_enabled

def send_order_confirm_email(handler_input, orders, add_images=True):
    """
    Take info about a waiting order and send it to customer saying ready for pickup as email
    Args:
        handler_input: Input to the Lambda handler. Used to access products in session state.
        to_email: Where to send the email to
        orders: Orders as obtained from get_orders_with_details()
    Returns:
        None.
    """

    session_attr = handler_input.attributes_manager.session_attributes

    user_email = get_cognito_user_details(handler_input)['email']
    if not user_email:
        logger.info("No email address configured against order.  If Cognito has not been configured, set AlexaDefaultSandboxEmail environment variable")
        return
    
    logger.info(f"Constructing order confirmation email for: {user_email}")

    order_ids = ', '.join(['#' + str(order['id']) for order in orders])

    # Specify content:
    subject = "Your order has been received!"
    heading = "Welcome,"
    subheading = "Your order has been placed."
    intro_text = f"""We will meet you at your pump with the following order ({order_ids}):"""
    html_intro_text = intro_text.replace('\n', '</p><p>')

    # Build the order list in text and HTML at the same time.
    html_orders = "<ul>"
    text_orders = ""
    for order in orders:
        order_name = f"Order #{order['id']}"
        html_orders += f"\n  <li>{order_name}:<ul>"
        text_orders += f'\n{order_name}:'
        for item in order['items']:
            if 'details' in item:
                img_url = item["details"]["image_url"]
                url = item["details"]["url"]
                name = item["details"]["name"]
            else:
                product = session_attr['Products'][item['product_id']]
                img_url = product.get("image", "")
                url = product.get("url", "")
                name = product.get("name", "Retail Demo Store Product")
            if add_images and img_url and len(img_url) > 0:
                img_tag = f'<img src="{img_url}" width="100px">'
            else:
                img_tag = ''
            html_orders += F'\n    <li><a href="{url}">{name}</a> - ${item["price"]:0.2f}<br/><a href="{url}">{img_tag}</a></br></a></li>'
            text_orders += f'\n  - {name} - ${item["price"]:0.2f} {url}'
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
        <p><a href="{os.environ.get('WebURL', '')}">Thank you for shopping!</a></p>
    </body>
    """

    # Build text message
    text = f"""
{heading}
{subheading}
{intro_text}
{text_orders}
Thank you for shopping!
{os.environ.get('WebURL', '')}
    """

    logger.debug(f"Contents of email to {user_email} html: \n{html}")
    logger.debug(f"Contents of email to {user_email} text: \n{text}")
    send_email(user_email, subject, html, text)


def fetch_product_slot_directive(handler_input):
    """
    Create product slots for use in the interaction model by calling the products service.
    Obtains list of products in the defined categories (in PRODUCT_CATEGORIES)
    and creates and EntityListItem for sending to Alexa for listening for these products
    Args:
        handler_input: As passed into the Alexa skill Lambda handler.

    Returns:
        EntityListItem: the products, with names and aliases, and keyed by ID.
    """
    products = []
    for category in PRODUCT_CATEGORIES:
        category_products = json.loads(
            urlopen(f'{PRODUCT_SERVICE_URL}/products/category/{category.replace(" ", "%20")}').read().decode('utf-8'))
        products += category_products

    session_attr = handler_input.attributes_manager.session_attributes
    if 'Products' not in session_attr:
        session_attr['Products'] = {}
        for product in products:
            session_attr['Products'][product['id']] = {'name': product['name'], 'price': product['price'],
                                                       'image': product['image'], 'url': product['url'],
                                                       'id': product['id']}

    entity_list_values = []
    for product in products:
        aliases = product['aliases'] if 'aliases' in product else [product['name']]
        value_and_synonyms = EntityValueAndSynonyms(value=product['name'], synonyms=aliases)
        entity_list_values.append(Entity(id=product['id'], name=value_and_synonyms))

    logger.info(f"Products retrieved for skill: {','.join([product['name'] for product in products])}")

    return EntityListItem(name="Product", values=entity_list_values)


def get_matched_product_id(handler_input):
    """
    Retrieves the product ID when using the ProductName slot
    Args:
        handler_input: As passed into the Alexa skill Lambda handler.

    Returns:
        str: Product ID.
    """
    resolutions_per_authority = handler_input.request_envelope.request.intent.slots[
        'ProductName'].resolutions.resolutions_per_authority
    for resolution in resolutions_per_authority:
        if resolution.status.code == StatusCode.ER_SUCCESS_MATCH:
            return resolution.values[0].value.id


def get_recommended_product(handler_input, product_id):
    """
    Calls out to the recommendations service which is typically backed by Amazon Personalize.
    Gets a recommended product for the passed product_id.
    Saves the recommendation for the product in the session.

    Args:
        handler_input: As passed into the Alexa skill Lambda handler.
        product_id: As converted from user input.

    Returns:
        dict: With product 'id', 'name' and 'price'.
    """
    session_attr = handler_input.attributes_manager.session_attributes

    if 'RecommendedProducts' not in session_attr:
        session_attr['RecommendedProducts'] = {}

    if product_id not in session_attr['RecommendedProducts']:
        user_details = get_cognito_user_details(handler_input)
        user_id = user_details['custom:profile_user_id']
        url = (f'{RECOMMENDATIONS_SERVICE_URL}/related?currentItemID={product_id}&'
               f'numResults=5&feature=alexa&userID={user_id}&filter=cstore')
        logger.info(url)
        recommended_products = json.loads(urlopen(url).read().decode('utf-8'))
        if len(recommended_products) > 0:
            recommended_product = recommended_products[0]['product']
            session_attr['RecommendedProducts'][product_id] = {'id': recommended_product['id'],
                                                               'name': recommended_product['name'],
                                                               'price': recommended_product['price']}
        else:
            logger.error("Could not retrieve a recommendation.")
            all_product_ids = list(session_attr['Products'].keys())
            random_product_id = all_product_ids[random.randrange(0, len(all_product_ids))]
            random_product = session_attr['Products'][random_product_id]
            session_attr['RecommendedProducts'][product_id] = {'id': random_product_id,
                                                               'name': random_product['name'],
                                                               'price': random_product['price']}

    return session_attr['RecommendedProducts'][product_id]


def get_product_by_id(handler_input, product_id):
    """
    Returns product dict associated with product ID.
    Products have already been loaded into the session object.
    Args:
        handler_input: As passed into the Alexa skill Lambda handler.
        product_id: As converted from user input.

    Returns:
        dict: With product 'id', 'name' and 'price'.
    """
    session_attr = handler_input.attributes_manager.session_attributes
    return session_attr['Products'][product_id]


def submit_order(handler_input):
    """
    Grab the order from the cart and send it to orders service.
    Args:
        handler_input:  As passed into the Alexa skill Lambda handler.

    Returns:
        None
    """
    user_details = get_cognito_user_details(handler_input)
    if user_details['custom:profile_user_id'].isnumeric():
        username = f"user{user_details['custom:profile_user_id']}"
        first_name = user_details['custom:profile_first_name']
        last_name = user_details['custom:profile_last_name']
    else:
        username = user_details['username']
        first_name = user_details['username']
        last_name = ""

    order = {
        "items": [],
        "total": get_cart_total(handler_input),
        "delivery_type": 'COLLECTION',
        "username": username,
        "billing_address": {
            "first_name": first_name,
            "last_name": last_name
        },
        "channel": "alexa"
    }

    cart = get_cart(handler_input)
    order['items'] = cart['items']

    logger.info(f"Submitting order: {order}")
    req = Request(f'{ORDER_SERVICE_URL}/orders', method='POST', data=json.dumps(order).encode('utf-8'))
    order_response = json.loads(urlopen(req).read().decode('utf-8'))
    logger.info(f"Order response: {order_response}")

    return order_response


def distance_km(point1, point2):
    """
    Convert from degrees to km - approximate."
    Args:
        point1: Array-like with 2 members (lat/long).
        point2: Array-like with 2 members (lat/long).

    Returns:
        float: distance in kilometres
    """
    return ((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2) ** 0.5 * 111


def get_customer_location():
    """
    Get customer faked location (we could also read it from device via Alexa
    but we might be demo-ing from the web where location
    is not available - see
    https://developer.amazon.com/en-US/docs/alexa/custom-skills/location-services-for-alexa-skills.html
    ).
    Returns:
        list: Coordinates lat/long.
    """
    cstore_route = json.loads(urlopen(f'{LOCATION_SERVICE_URL}/cstore_route').read().decode('utf-8'))
    customer_position = cstore_route['features'][0]['geometry']['coordinates'][0]
    return customer_position


def location_search_cstore() -> Tuple[str, float]:
    """
    From customer location, search for nearest store.
    Returns:
        str: Spoken address of nearest store.
        float: distance to it in miles
    """
    customer_position = get_customer_location()

    # Do the search for nearby C Store
    try:
        response = location.search_place_index_for_text(IndexName=LOCATION_PLACE_INDEX_NAME,
                                                        Text="Convenience Store",
                                                        BiasPosition=customer_position)

        # Grab address and make it sound nice - could be a lot more sophisticated here
        address = response['Results'][0]['Place']
        spoken_address = get_nice_address(address)
        store_position = address['Geometry']['Point']

        # How far away is that?
        shop_dist_km = distance_km(store_position, customer_position)
        shop_dist_miles = 0.6214 * shop_dist_km

        address_dump = json.dumps(address, default=str)

        logger.info(f"Closest convenience store to {customer_position} is at {store_position}, "
                    f"with spoken address {spoken_address} and distance {shop_dist_km:0.0f}km"
                    f" ({shop_dist_miles:0.0f} miles). Full address data: {address_dump}")

    except Exception as e:

        logger.error('Cannot do place index search - perhaps your Location resources were not deployed?'
                     f'Message: {e} LOCATION_PLACE_INDEX_NAME: {LOCATION_PLACE_INDEX_NAME}')

        spoken_address = "640 Elk Street"
        shop_dist_miles = 3

    return spoken_address, shop_dist_miles


def get_cart(handler_input):
    """
    Retrieve cart from carts service or create a new one.
    Username will be from Cognito integration or "guest".
    Args:
        handler_input: As passed into the Alexa skill Lambda handler.

    Returns:
        dict: shopping cart, including id, username and items
    """

    session_attr = handler_input.attributes_manager.session_attributes
    user_details = get_cognito_user_details(handler_input)
    username = user_details['username']

    if 'CartId' not in session_attr:

        cart = {'username': username, 'items': []}

        req = Request(f'{CARTS_SERVICE_URL}/carts', method='POST', data=json.dumps(cart).encode('utf-8'))
        resp = urlopen(req).read().decode('utf-8')
        cart = json.loads(resp)
        logger.info(f"Cart created response: {cart}")

        session_attr['CartId'] = cart['id']

    else:

        req = Request(f'{CARTS_SERVICE_URL}/carts/{session_attr["CartId"]}', method='GET')
        resp = urlopen(req).read().decode('utf-8')
        cart = json.loads(resp)
        logger.info(f"Cart retrieved response: {cart}")

    return cart


def get_cart_total(handler_input):
    """
    We total up what is in our user's basket.
    Args:
        handler_input: As passed into the Alexa skill Lambda handler.

    Returns:
        float: price in currency
    """

    cart = get_cart(handler_input)
    total = sum(item['price'] * item['quantity'] for item in cart['items'])
    return total


def add_product_to_cart(handler_input, product):
    """
    Save a product in cart for user.
    A new cart will be created in the carts service if necessary.
    If cognito integration is not enabled, user will be "guest".
    Args:
        handler_input: As passed into the Alexa skill Lambda handler.
        product_id: As converted from user input.

    Returns:

    """
    cart = get_cart(handler_input)

    incremented_quantity = False
    for item in cart['items']:
        if item['product_id'] == product['id']:
            item['quantity'] += 1
            incremented_quantity = True
            break

    if not incremented_quantity:
        cart['items'].append({
          'product_id': product['id'],
          'quantity': 1,
          'price': product['price'],
          'product_name': product['name']
        })

    req = Request(f'{CARTS_SERVICE_URL}/carts/{cart["id"]}',
                  method='PUT',
                  data=json.dumps(cart).encode('utf-8'))
    resp = urlopen(req).read().decode('utf-8')
    cart = json.loads(resp)

    logger.debug(f"Cart updated: {cart}")


def set_question_asked(handler_input, question=''):
    """
    Sets an identifier for the question last asked to allow for the handling of yes/no questions outside a DialogState.
    This identifier is persisted in the Alexa session_attributes and should be removed upon handling the response
    to avoid unexpected consequences in the handling following questions.

    The expected flow is as follows:
        - Yes/no question is asked
        - The identifier for that question is persisted to session_attributes
        - The yes/no question is answered and handled by the AMAZON.YesIntent/AMAZON.NoIntent
        - The combination of Yes/NoIntent and the previous quesiton asked can be used to determine
          how the response should be handled.

    Parameters:
        - handler_input (dict): The handler_input dict used to call the intent handler.
        - question (str):       The identifier for the question asked.

    Returns:
        None
    """
    handler_input.attributes_manager.session_attributes['PreviousQuestion'] = question


def get_question_asked(handler_input):
    """
    Gets an identifier for the previous question asked to allow for the handling of yes/no questions outside of a
    DialogState. This identifier is persisted in the Alexa session_attributes and should be removed upon handling the
    response to avoid unexpected consequences in the handling following questions.

    Parameters:
        - handler_input (dict): The handler_input dict used to call the intent handler.

    Returns:
        String: The string identifier of the last question asked.
    """
    return handler_input.attributes_manager.session_attributes['PreviousQuestion']


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""

    def can_handle(self, handler_input):
        """
        Can this handler handle this intent?
        Args:
            handler_input (HandlerInput): The handler_input dict used to call the intent handler.
        Returns:
            bool
        """
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        """
        Handle this intent. Results are provided using response_builder.
        Args:
            handler_input (HandlerInput): The handler_input dict used to call the intent handler.
        Returns:
            Response
        """
        logger.info("Calling LaunchRequestHandler")
        speak_output = ("Welcome to the Retail Demo Store. Ask where is your "
                        "nearest convenience store to start an order there.")

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class FindStoreIntentHandler(AbstractRequestHandler):
    """Handler for Find Store Intent. Grab nearest Exxon using Amazon Location Service.
    Meanwhile, fill in the list of available products (e.g. these could depend on the store chosen)
    using `fetch_product_slot_directive()`"""

    def can_handle(self, handler_input):
        """
        Can this handler handle this intent?
        Args:
            handler_input (HandlerInput): The handler_input dict used to call the intent handler.
        Returns:
            bool
        """
        return ask_utils.is_intent_name("FindStoreIntent")(handler_input)

    def handle(self, handler_input):
        """
        Handle this intent. Results are provided using response_builder.
        Args:
            handler_input (HandlerInput): The handler_input dict used to call the intent handler.
        Returns:
            Response
        """
        logger.info("Calling FindStoreIntentHandler")

        # The address and distance will look like this:
        spoken_address, shop_dist_miles = location_search_cstore()
        if shop_dist_miles < 0.7:  # If considerably less than a mile away, we can give it in part-miles
            miles_formatted = f'{shop_dist_miles:0.1f}'.strip()
        else:
            miles_formatted = f'{shop_dist_miles:0.0f}'.strip()
        units_text = 'mile' if miles_formatted == '1' else 'miles'
        speak_output = f"There is a convenience store {miles_formatted} {units_text} away at {spoken_address}. " \
                       "Would you like to pre-order items to collect when you arrive?"
        set_question_asked(handler_input, 'START_PREORDER')
        product_slot_directive = DynamicEntitiesDirective(update_behavior=UpdateBehavior.REPLACE,
                                                          types=[fetch_product_slot_directive(handler_input)])

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask("Would you like to pre-order items to collect when you arrive?")
                .add_directive(product_slot_directive)
                .response
        )


class OrderProductIntentHandler(AbstractRequestHandler):
    """Handler for Order Product Intent. Fill in ordered product and recommended product, add ordered
    product to basket, tell the user we've done this and offer recommendation. Elicit the recommendation Yes/No
    response."""

    def can_handle(self, handler_input):
        """
        Can this handler handle this intent?
        Args:
            handler_input (HandlerInput): The handler_input dict used to call the intent handler.
        Returns:
            bool
        """
        return (
                ask_utils.is_intent_name("OrderProductIntent")(handler_input)
                and ask_utils.get_dialog_state(handler_input) == DialogState.STARTED
        )

    def handle(self, handler_input):
        """
        Handle this intent. Results are provided using response_builder.
        Args:
            handler_input (HandlerInput): The handler_input dict used to call the intent handler.
        Returns:
            Response
        """
        logger.info("Calling OrderProductIntentHandler")
        product_name = ask_utils.get_slot_value(handler_input, 'ProductName')

        product_id = get_matched_product_id(handler_input)
        recommended_product = get_recommended_product(handler_input, product_id)
        product = get_product_by_id(handler_input, product_id)
        add_product_to_cart(handler_input, product)


        speak_output = f"Sure. Ordering {product_name} for ${product['price']}. " \
                       f"Would you like to add {recommended_product['name']} to your basket too?"
        recommended_product_directive = ElicitSlotDirective(slot_to_elicit='AddRecommendedProduct')

        return (
            handler_input.response_builder
                .speak(speak_output)
                .add_directive(recommended_product_directive)
                .response
        )


class AddRecommendedProductHandler(AbstractRequestHandler):
    """Handler for recommended product within OrderProduct dialog.
    If the user wants the recommended product, add it to basket.
    If they say they don't want it, do not add it. Then loop by setting the question asked state var to ORDER_MORE"""

    def can_handle(self, handler_input):
        """
        Can this handler handle this intent?
        Args:
            handler_input (HandlerInput): The handler_input dict used to call the intent handler.
        Returns:
            bool
        """
        return (
                ask_utils.is_intent_name("OrderProductIntent")(handler_input)
                and ask_utils.get_dialog_state(handler_input) == DialogState.IN_PROGRESS
        )

    def handle(self, handler_input):
        """
        Handle this intent. Results are provided using response_builder.
        Args:
            handler_input (HandlerInput): The handler_input dict used to call the intent handler.
        Returns:
            Response
        """
        logger.info(
            f"Calling AddRecommendedProductHandler: {json.dumps(handler_input.request_envelope.to_dict(), default=str, indent=2)}")

        # add_recommended_product will either be "0" (no) or "1" (yes)
        should_add_recommended_product = \
        ask_utils.get_slot(handler_input, 'AddRecommendedProduct').resolutions.resolutions_per_authority[0].values[
            0].value.id
        if should_add_recommended_product == "1":
            recommended_product = get_recommended_product(handler_input, get_matched_product_id(handler_input))
            speak_output = f"Adding {recommended_product['name']} for ${recommended_product['price']}!"
            add_product_to_cart(handler_input, recommended_product)
        else:
            speak_output = "Sure."

        speak_output += " Would you like to order anything else?"
        set_question_asked(handler_input, 'ORDER_MORE')

        return (
            handler_input.response_builder
                .speak(speak_output)
                .set_should_end_session(False)
                .response
        )


class ToCheckoutHandler(AbstractRequestHandler):
    """User responds "No" to whether to order more.
    Delegate to the Checkout intent."""

    def can_handle(self, handler_input):
        """
        Can this handler handle this intent?
        Args:
            handler_input (HandlerInput): The handler_input dict used to call the intent handler.
        Returns:
            bool
        """
        return (
                ask_utils.is_intent_name("AMAZON.NoIntent")(handler_input) and get_question_asked(
            handler_input) == 'ORDER_MORE'
        )

    def handle(self, handler_input):
        """
        Handle this intent. Results are provided using response_builder.
        Args:
            handler_input (HandlerInput): The handler_input dict used to call the intent handler.
        Returns:
            Response
        """
        logger.info("Calling ToCheckoutHandler")

        checkout_delegate_directive = DelegateDirective(updated_intent={'name': 'CheckoutIntent'})

        return (
            handler_input.response_builder
                .add_directive(checkout_delegate_directive)
                .response
        )


class CheckoutIntentHandler(AbstractRequestHandler):
    """Handler for the Checkout Intent. This intent can be accessed at any time - e.g. you can
    shortcut a recommendation suggestion by just saying "checkout"."""

    def can_handle(self, handler_input):
        """
        Can this handler handle this intent?
        Args:
            handler_input (HandlerInput): The handler_input dict used to call the intent handler.
        Returns:
            bool
        """
        return (
            ask_utils.is_intent_name("CheckoutIntent")(handler_input)
        )

    def handle(self, handler_input):
        """
        Handle this intent. Results are provided using response_builder.
        Args:
            handler_input (HandlerInput): The handler_input dict used to call the intent handler.
        Returns:
            Response
        """
        logger.info(
            f"Calling CheckoutIntentHandler {json.dumps(handler_input.request_envelope.to_dict(), default=str, indent=2)}")

        basket_total = get_cart_total(handler_input)
        user_details = get_cognito_user_details(handler_input)

        speak_output = f"Your order total is ${basket_total}. "

        order_response = submit_order(handler_input)
        send_order_confirm_email(handler_input, [order_response], False)
        speak_output += "It will be ready when you arrive" 
        if user_details['cognito_loaded']:            
            name = user_details.get('custom:profile_first_name', '')
            speak_output += f"  {name}"                   
        
        speak_output += ". Hope to see you again soon."
        return (
            handler_input.response_builder
                .speak(speak_output)
                .set_should_end_session(True)
                .response
        )

class OrderProductHandler(AbstractRequestHandler):
    """We have asked "would you like to order something" so if the answer is yes, we delegate to the
    OrderProductIntent."""

    def can_handle(self, handler_input):
        """
        Can this handler handle this intent?
        Args:
            handler_input (HandlerInput): The handler_input dict used to call the intent handler.
        Returns:
            bool
        """
        return (
                ask_utils.is_intent_name("AMAZON.YesIntent")(handler_input)
                and (get_question_asked(handler_input) in ['START_PREORDER', 'ORDER_MORE'])
        )

    def handle(self, handler_input):
        """
        Handle this intent. Results are provided using response_builder.
        Args:
            handler_input (HandlerInput): The handler_input dict used to call the intent handler.
        Returns:
            Response
        """
        logger.info("Calling OrderMoreHandler")

        set_question_asked(handler_input)

        order_product_delegate_directive = DelegateDirective(updated_intent={'name': 'OrderProductIntent'})

        return (
            handler_input.response_builder
                .add_directive(order_product_delegate_directive)
                .response
        )


class NoProductOrderHandler(AbstractRequestHandler):
    """We have asked "would you like to order something" before any product has been selected,
     so if the answer is no, we bid farewell."""

    def can_handle(self, handler_input):
        """
        Can this handler handle this intent?
        Args:
            handler_input (HandlerInput): The handler_input dict used to call the intent handler.
        Returns:
            bool
        """
        return (
                ask_utils.is_intent_name("AMAZON.NoIntent")(handler_input)
                and (get_question_asked(handler_input) == 'START_PREORDER')
        )

    def handle(self, handler_input):
        """
        Handle this intent. Results are provided using response_builder.
        Args:
            handler_input (HandlerInput): The handler_input dict used to call the intent handler.
        Returns:
            Response
        """
        logger.info("Calling NoProductOrderHandler")

        speak_output = "Have a safe trip!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent. A standard intent."""

    def can_handle(self, handler_input):
        """
        Can this handler handle this intent?
        Args:
            handler_input (HandlerInput): The handler_input dict used to call the intent handler.
        Returns:
            bool
        """
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        """
        Handle this intent. Results are provided using response_builder.
        Args:
            handler_input (HandlerInput): The handler_input dict used to call the intent handler.
        Returns:
            Response
        """
        logger.info("Calling HelpIntentHandler")

        speak_output = "You can say hello to me! How can I help?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""

    def can_handle(self, handler_input):
        """
        Can this handler handle this intent?
        Args:
            handler_input (HandlerInput): The handler_input dict used to call the intent handler.
        Returns:
            bool
        """
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        """
        Handle this intent. Results are provided using response_builder.
        Args:
            handler_input (HandlerInput): The handler_input dict used to call the intent handler.
        Returns:
            Response
        """
        logger.info("Calling CancelOrStopIntentHandler")
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""

    def can_handle(self, handler_input):
        """
        Can this handler handle this intent?
        Args:
            handler_input (HandlerInput): The handler_input dict used to call the intent handler.
        Returns:
            bool
        """
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        """
        Handle this intent. Results are provided using response_builder.
        Args:
            handler_input (HandlerInput): The handler_input dict used to call the intent handler.
        Returns:
            Response
        """
        logger.info("Calling SessionEndedRequestHandler")

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """

    def can_handle(self, handler_input):
        """
        Can this handler handle this intent?
        Args:
            handler_input (HandlerInput): The handler_input dict used to call the intent handler.
        Returns:
            bool
        """
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        """
        Handle this intent. Results are provided using response_builder.
        Args:
            handler_input (HandlerInput): The handler_input dict used to call the intent handler.
        Returns:
            Response
        """
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """

    def can_handle(self, handler_input, exception):
        """
        Can this handler handle this intent?
        Args:
            handler_input (HandlerInput): The handler_input dict used to call the intent handler.
        Returns:
            bool
        """
        return True

    def handle(self, handler_input, exception):
        """
        Handle this intent. Results are provided using response_builder.
        Args:
            handler_input (HandlerInput): The handler_input dict used to call the intent handler.
        Returns:
            Response
        """
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(FindStoreIntentHandler())
sb.add_request_handler(OrderProductIntentHandler())
sb.add_request_handler(AddRecommendedProductHandler())
sb.add_request_handler(CheckoutIntentHandler())
sb.add_request_handler(OrderProductHandler())
sb.add_request_handler(NoProductOrderHandler())
sb.add_request_handler(ToCheckoutHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(
    IntentReflectorHandler())  # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
