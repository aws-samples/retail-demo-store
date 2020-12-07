# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import boto3
import json
import logging
import os
import requests
import threading
import ask_sdk_core.utils as ask_utils

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response
from ask_sdk_model.dialog import ElicitSlotDirective, DynamicEntitiesDirective, DelegateDirective
from ask_sdk_model.dialog_state import DialogState
from ask_sdk_model.er.dynamic import Entity, EntityValueAndSynonyms, EntityListItem, UpdateBehavior
from ask_sdk_model.slu.entityresolution import StatusCode

from dotenv import load_dotenv

from urllib.request import Request, urlopen


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

load_dotenv()

AWS_REGION = os.environ.get('AWS_REGION')

ORDER_SERVICE_URL = os.environ.get('ORDER_SERVICE_URL')
PRODUCT_SERVICE_URL = os.environ.get('PRODUCT_SERVICE_URL')
RECOMMENDATIONS_SERVICE_URL = os.environ.get('RECOMMENDATIONS_SERVICE_URL')
WAYPOINT_SERVICE_URL = os.environ.get('WAYPOINT_SERVICE_URL')

PINPOINT_APP_ID = os.environ.get('PINPOINT_APP_ID')
COGNITO_DOMAIN = os.environ.get('COGNITO_DOMAIN')
WAYPOINT_PLACE_INDEX_NAME = os.environ.get('WAYPOINT_PLACE_INDEX_NAME')

ASSUME_ROLE_ARN = os.environ.get('ASSUME_ROLE_ARN')

PRODUCT_CATEGORIES = ['food service', 'salty snacks', 'hot drinks', 'cold dispensed']

sts_client = boto3.client('sts')
assumed_role_object=sts_client.assume_role(
    RoleArn=ASSUME_ROLE_ARN,
    RoleSessionName="AssumeRoleSession"
)
credentials = assumed_role_object['Credentials']

pinpoint = boto3.client(
    'pinpoint', 
    aws_access_key_id=credentials['AccessKeyId'],
    aws_secret_access_key=credentials['SecretAccessKey'],
    aws_session_token=credentials['SessionToken'],
    region_name=AWS_REGION
)

location = boto3.client(
    'location',
    aws_access_key_id=credentials['AccessKeyId'],
    aws_secret_access_key=credentials['SecretAccessKey'],
    aws_session_token=credentials['SessionToken'],
    region_name=AWS_REGION
)


def get_cognito_user_details(handler_input):
    session_attr = handler_input.attributes_manager.session_attributes
    access_token = handler_input.request_envelope.context.system.user.access_token
    req = Request(f"{COGNITO_DOMAIN}/oauth2/userInfo")
    req.add_header('Authorization', f'Bearer {access_token}')
    user_details = json.loads(urlopen(req).read().decode('utf-8'))
    session_attr['CognitoUser'] = user_details
    return user_details


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


def send_order_confirm_email(handler_input, orders, add_images=True):
    """
    Take info about a waiting order and send it to customer saying ready for pickup as email
    Args:
        handler_input: Input to the Lambda handler. Used to access products in session state.
        to_email: Where to send the email to
        orders: Orders as obtained from get_orders_with_details()
    Returns:
        Nothing but sends an email.
    """

    session_attr = handler_input.attributes_manager.session_attributes

    user_email = get_cognito_user_details(handler_input)['email']

    order_ids = ', '.join(['#' + str(order['id']) for order in orders])

    # Specify content:
    subject = "Your order has been received!"
    heading = "Welcome,"
    subheading = f"Your order has been paid for with Amazon Pay."
    intro_text = f"""We will meet you at your pump with the following order ({order_ids}):"""
    html_intro_text = intro_text.replace('\n', '</p><p>')

    # Build the order list in text and HTML at the same time.
    html_orders = "<ul>"
    text_orders = ""
    for order in orders:
        ordername = f"Order #{order['id']}"
        html_orders += f"\n  <li>{ordername}:<ul>"
        text_orders += f'\n{ordername}:'
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
            html_orders += F'\n    <li><a href="{url}">{name}</a> - ${item["price"]}<br/><a href="{url}">{img_tag}</a></br></a></li>'
            text_orders += f'\n  - {name} - {item["price"]} {url}'
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
        <p><a href="{os.environ.get('WebURL','')}">Thank you for shopping!</a></p>
    </body>
    """

    # Build text message
    text = f"""
{heading}
{subheading}
{intro_text}
{text_orders}
Thank you for shopping!
{os.environ.get('WebURL','')}
    """

    logger.debug(f"Contents of email to {user_email} html: \n{html}")
    logger.debug(f"Contents of email to {user_email} text: \n{text}")
    send_email(user_email, subject, html, text)


def fetch_product_slot_directive(handler_input):
    products = []
    for category in PRODUCT_CATEGORIES:
        category_products = json.loads(urlopen(f'{PRODUCT_SERVICE_URL}/products/category/{category.replace(" ", "%20")}').read().decode('utf-8'))
        products += category_products

    session_attr = handler_input.attributes_manager.session_attributes
    if 'Products' not in session_attr:
        session_attr['Products'] = {}
        for product in products:
            session_attr['Products'][product['id']] = {'name': product['name'], 'price': product['price'], 'image': product['image'], 'url': product['url']}

    entity_list_values = []
    for product in products:
        value_and_synonyms = EntityValueAndSynonyms(value=product['name'], synonyms=product['aliases'])
        entity_list_values.append(Entity(id=product['id'], name=value_and_synonyms))

    return EntityListItem(name="Product", values=entity_list_values)


def get_matched_product_id(handler_input):
    """Retrieves the product ID when using the ProductName slot"""
    resolutions_per_authority = handler_input.request_envelope.request.intent.slots['ProductName'].resolutions.resolutions_per_authority
    for resolution in resolutions_per_authority:
        if resolution.status.code == StatusCode.ER_SUCCESS_MATCH:
            return resolution.values[0].value.id


def get_recommended_product(handler_input, product_id):
    """Retrieves the recommended ID when using the ProductName slot"""
    session_attr = handler_input.attributes_manager.session_attributes
    
    if 'RecommendedProducts' not in session_attr:
        session_attr['RecommendedProducts'] = {}

    if product_id not in session_attr['RecommendedProducts']:
        logger.info(f'{RECOMMENDATIONS_SERVICE_URL}/related?currentItemID={product_id}&numResults=5&feature=alexa&userID=1&filter=cstore')
        recommended_products = json.loads(urlopen(f'{RECOMMENDATIONS_SERVICE_URL}/related?currentItemID={product_id}&numResults=5&feature=alexa&userID=1&filter=cstore').read().decode('utf-8'))
        recommended_product = recommended_products[0]['product']
        session_attr['RecommendedProducts'][product_id] = {'id': recommended_product['id'], 'name': recommended_product['name'], 'price': recommended_product['price']}

    return session_attr['RecommendedProducts'][product_id]


def get_product_by_id(handler_input, product_id):
    session_attr = handler_input.attributes_manager.session_attributes
    return session_attr['Products'][product_id]


def submit_order(handler_input):
    session_attr = handler_input.attributes_manager.session_attributes
    
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
        "total": get_basket_total(handler_input),
        "delivery_type": 'COLLECTION',
        "username": username,
        "billing_address": {
            "first_name": first_name,
            "last_name": last_name
        },
        "channel": "alexa"
    }
    
    for item_id, basket_item in session_attr['Basket'].items():
        order_item = {
            'product_id': item_id,
            'quantity': basket_item['quantity'],
            'price': get_product_by_id(handler_input, item_id)['price']
        }
        order['items'].append(order_item)
    
    logger.info(f"Submitting order: {order}")
    req = Request(f'{ORDER_SERVICE_URL}/orders', method='POST', data=json.dumps(order).encode('utf-8'))
    order_response = json.loads(urlopen(req).read().decode('utf-8'))
    logger.info(f"Order response: {order_response}")
    
    return order_response


def get_customer_location():
    cstore_route = json.loads(urlopen(f'{WAYPOINT_SERVICE_URL}/cstore_route').read().decode('utf-8'))
    bias_position = cstore_route['features'][0]['geometry']['coordinates'][0]
    response = location.search_place_index_for_text(IndexName=WAYPOINT_PLACE_INDEX_NAME, Text="Exxon", BiasPosition=bias_position)
    address = response['Results'][0]['Place']
    spoken_address = address['AddressNumber'] + " " + address['Street']
    return spoken_address


def get_basket_total(handler_input):
    total = 0
    session_attr = handler_input.attributes_manager.session_attributes
    
    if 'Basket' not in session_attr:
        return total
        
    for item_id, basket_item in session_attr['Basket'].items():
        total += session_attr['Products'][item_id]['price'] * basket_item['quantity']
        
    return total


def add_product_to_basket(handler_input, prod_id):
    session_attr = handler_input.attributes_manager.session_attributes
    
    if 'Basket' not in session_attr:
        session_attr['Basket'] = {}
    
    if prod_id not in session_attr['Basket']:
        session_attr['Basket'][prod_id] = {'quantity': 1}
    else: 
        session_attr['Basket'][prod_id]['quantity'] += 1


def set_question_asked(handler_input, question=''):
    """
    Sets an identifier for the question asked to allow for the handling of yes/no questions outside of a DialogState. 
    This identifier is persisted in the Alexa session_attributes and should be removed upon handling the response to avoid
    unexpected consequences in the handling following questions. 
    
    The expected flow is as follows:
        - Yes/no question is asked
        - The identifier for that question is persisted to session_attributes
        - The yes/no question is answered and handled by the AMAZON.YesIntent/AMAZON.NoIntent
        - The combination of Yes/NoIntent and the previous quesiton asked can be used to determine how the response should be handled. 
    
    Parameters:
        - handler_input (dict): The handler_input dict used to call the intent handler. 
        - question (str):       The identifier for the question asked.
        
    Returns: 
        None
    """
    
    handler_input.attributes_manager.session_attributes['PreviousQuestion'] = question
    

def get_question_asked(handler_input):
    """
    Gets an identifier for the previous question asked to allow for the handling of yes/no questions outside of a DialogState. 
    This identifier is persisted in the Alexa session_attributes and should be removed upon handling the response to avoid
    unexpected consequences in the handling following questions. 
    
    Parameters:
        - handler_input (dict): The handler_input dict used to call the intent handler. 
        
    Returns: 
        String: The string identifier of the last question asked. 
    """
    
    return handler_input.attributes_manager.session_attributes['PreviousQuestion']


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("Calling LaunchRequestHandler")
        speak_output = "Welcome to the C-Store Demo. Ask where your nearest Exxon is to start an order there."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class FindStoreIntentHandler(AbstractRequestHandler):
    """Handler for Find Store Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("FindStoreIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("Calling FindStoreIntentHandler")

        # TODO: Get this response from Waypoint
        speak_output = "There is an Exxon 3 miles away at 1640 Elk St. Would you like to pre-order items to collect when you arrive?"
        set_question_asked(handler_input, 'START_PREORDER')
        product_slot_directive = DynamicEntitiesDirective(update_behavior=UpdateBehavior.REPLACE, types=[fetch_product_slot_directive(handler_input)])

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask("Would you like to pre-order items to collect when you arrive?")
                .add_directive(product_slot_directive)
                .response
        )


class OrderProductIntentHandler(AbstractRequestHandler):
    """Handler for Order Product Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (
            ask_utils.is_intent_name("OrderProductIntent")(handler_input) 
            and ask_utils.get_dialog_state(handler_input) == DialogState.STARTED
        )

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("Calling OrderProductIntentHandler")
        product_name = ask_utils.get_slot_value(handler_input, 'ProductName')
        
        product_id = get_matched_product_id(handler_input)
        recommended_product = get_recommended_product(handler_input, product_id)
        add_product_to_basket(handler_input, product_id)
        product = get_product_by_id(handler_input, product_id)
        
        speak_output = f"Sure. Ordering {product_name} for ${product['price']}. Would you like to add {recommended_product['name']} to your basket too?"
        recommended_product_directive = ElicitSlotDirective(slot_to_elicit='AddRecommendedProduct')

        return (
            handler_input.response_builder
                .speak(speak_output)
                .add_directive(recommended_product_directive)
                .response
        )


class AddRecommendedProductHandler(AbstractRequestHandler):
    """Handler for recommended product within OrderProduct dialog."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (
            ask_utils.is_intent_name("OrderProductIntent")(handler_input)
            and ask_utils.get_dialog_state(handler_input) == DialogState.IN_PROGRESS
        )

    def add_recommended_product(self, handler_input):
        product_id = get_matched_product_id(handler_input)
        recommended_product = get_recommended_product(handler_input, product_id)
        add_product_to_basket(handler_input, recommended_product['id'])
    
    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("Calling AddRecommendedProductHandler")
        
        # add_recommended_product will either be "0" (no) or "1" (yes)
        should_add_recommended_product = ask_utils.get_slot(handler_input, 'AddRecommendedProduct').resolutions.resolutions_per_authority[0].values[0].value.id
        if should_add_recommended_product == "1":
            self.add_recommended_product(handler_input)
            recommended_product = get_recommended_product(handler_input, get_matched_product_id(handler_input))
            speak_output = f"Adding {recommended_product['name']} for ${recommended_product['price']}!"
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


class CheckoutIntentHandler(AbstractRequestHandler):
    """Handler for the Checkout Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (
            ask_utils.is_intent_name("CheckoutIntent")(handler_input)
        )
        
    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("Calling CheckoutIntentHandler")
        
        order_response = submit_order(handler_input)
        send_order_confirm_email(handler_input, [order_response], False)
        
        speak_output = f"Thank you! ${get_basket_total(handler_input)} has been charged to your Amazon Pay account. Your order ID is {order_response['id']}. Use this ID to collect your order when you arrive."
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class ToCheckoutHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (
            ask_utils.is_intent_name("AMAZON.NoIntent")(handler_input) and get_question_asked(handler_input) == 'ORDER_MORE'
        )

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("Calling ToCheckoutHandler")
        
        checkout_delegate_directive = DelegateDirective(updated_intent={'name': 'CheckoutIntent'})
        
        speak_output = f"Your total is ${get_basket_total(handler_input)}."
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .add_directive(checkout_delegate_directive)
                .response
        )


class OrderProductHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (
            ask_utils.is_intent_name("AMAZON.YesIntent")(handler_input) 
            and (get_question_asked(handler_input) in ['START_PREORDER', 'ORDER_MORE'])
        )

    def handle(self, handler_input):
        logger.info("Calling OrderMoreHandler")
        
        set_question_asked(handler_input)

        order_product_delegate_directive = DelegateDirective(updated_intent={'name': 'OrderProductIntent'})
        
        return (
            handler_input.response_builder
                .add_directive(order_product_delegate_directive)
                .response
        )


class NoProductOrderHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (
            ask_utils.is_intent_name("AMAZON.NoIntent")(handler_input) 
            and (get_question_asked(handler_input) == 'START_PREORDER')
        )
        
    def handle(self, handler_input):
        logger.info("Calling NoProductOrderHandler")
        
        speak_output = "Have a safe trip!"
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
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
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
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
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
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
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
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
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
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
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()