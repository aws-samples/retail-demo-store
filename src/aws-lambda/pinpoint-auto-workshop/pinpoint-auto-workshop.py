# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

"""
Lambda function designed to be called when the Personalize campaign ARN is set as an
SSM parameter indicating that the campaign has been created (either by the automated
deployment process or the Personalize workshop bundled with the Retail Demo Store project).
A CloudWatch event is setup as part of the Retail Demo Store deployment that watches for
the SSM parameter to change and targets this function.

This function will automate the steps in the Messaging workshop for Pinpoint. It is
only deployed when the user indicates that they want the Pinpoint workshop automated.
Typically this is part of an automated Retail Demo Store deployment/refresh cycle.

This function will delete the CloudWatch rule that triggers it when the function ends
successfully. Therefore, under normal conditions, this function will be executed once.
"""

import json
import boto3
import logging
import os
from datetime import datetime, timedelta
from botocore.exceptions import ClientError
import time

GEOFENCE_PINPOINT_EVENTTYPE = 'LocationApproachLocalShop'

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ssm = boto3.client('ssm')
sts = boto3.client('sts')
pinpoint = boto3.client('pinpoint')
cw_events = boto3.client('events')

do_deploy_offers_campaign = os.environ['DeployPersonalizedOffersCampaign'].strip().lower() in ['yes', 'true', '1']

welcome_template_name = 'RetailDemoStore-Welcome'
abandoned_cart_template_name = 'RetailDemoStore-AbandonedCart'
recommendations_template_name = 'RetailDemoStore-Recommendations'
sms_recommendation_template_name = 'RetailDemoStore-SMSRecommendations'

offers_recommender_name = 'retaildemooffers-recommender'

location_abandoned_cart_template_name = 'RetailDemoStore-LocationAbandonedCart'
location_offers_recommendations_template_name = 'RetailDemoStore-LocationOfferRecommendations'


def create_email_template(template_name, template_fname_root, subject, description, recommender_id=None):
    """
    Grab email template from file, create Pinpoint template. Default substitute user first name as "there".
    Args:
        template_name: What to call this Pinpoint template
        template_fname_root: Where to look for both HTML and TXT templates inside pinpoint-templates/
        subject: Email subject
        description: For Pinpoint console.
        recommender_id: If supplied, attach Pinpoint "machine learning model" (wraps Personalize) to template.
        
    Returns:
        Email template config. Deletes earlier version if already exists.
    """
    logger.info(f"Creating email template: {template_name}")

    with open('pinpoint-templates/'+template_fname_root+'.html', 'r') as html_file:
        html_template = html_file.read()

    with open('pinpoint-templates/'+template_fname_root+'.txt', 'r') as text_file:
        text_template = text_file.read()

    request = {
        'Subject': subject,
        'TemplateDescription': description,
        'HtmlPart': html_template,
        'TextPart': text_template,
        'DefaultSubstitutions': json.dumps({
            'User.UserAttributes.FirstName': 'there'
        })
    }

    if recommender_id is not None:
        request['RecommenderId'] = recommender_id

    while True:
        try:
            response = pinpoint.create_email_template(
                EmailTemplateRequest=request,
                TemplateName=template_name
            )
            break
        except pinpoint.exceptions.BadRequestException:
            try:
                pinpoint.delete_email_template(TemplateName=template_name)
            except BaseException as error:
                logger.info('An exception occurred: {}'.format(error))
                pass
            backoff_seconds = 30
            logger.info(f"Waiting for old template to delete: {template_name} - waiting {backoff_seconds} seconds")
            time.sleep(backoff_seconds)

    return response['CreateTemplateMessageBody']


def create_sms_template(template_name, body, description, recommender_id=None):
    """
        Grab SMS template from file, create Pinpoint template. Default substitute user first name as "there".
    Args:
        template_name: What to call this Pinpoint template
        body: Message to send.
        description: For Pinpoint console.
        recommender_id: If supplied, attach Pinpoint "machine learning model" (wraps Personalize) to template.

    Returns:
        SMS template config. Returns even if already exists.

    """
    logger.info(f"Creating SMS template: {template_name}")

    request = {
        'TemplateDescription': description,
        'Body': body,
        'DefaultSubstitutions': json.dumps({
            'User.UserAttributes.FirstName': 'there'
        })
    }

    if recommender_id is not None:
        request['RecommenderId'] = recommender_id

    while True:
        try:
            response = pinpoint.create_sms_template(
                SMSTemplateRequest=request,
                TemplateName=template_name
            )
            break
        except pinpoint.exceptions.BadRequestException:
            try:
                pinpoint.delete_sms_template(TemplateName=template_name)
            except BaseException as error:
                logger.info('An exception occurred: {}'.format(error))
                pass
            backoff_seconds = 30
            logger.info(f"Waiting for old template to delete: {template_name} - waiting {backoff_seconds} seconds")
            time.sleep(backoff_seconds)

    return response['CreateTemplateMessageBody']


def create_welcome_email_template():
    return create_email_template(welcome_template_name, 'welcome-email-template',
                                 subject='Welcome to the Retail Demo Store',
                                 description='Welcome email sent to new customers',
                                 recommender_id=None)


def create_abandoned_cart_email_template():
    return create_email_template(abandoned_cart_template_name, 'abandoned-cart-email-template',
                                 subject='Retail Demo Store - Motivation to Complete Your Order',
                                 description='Abandoned cart email template',
                                 recommender_id=None)


def create_recommendations_email_template():
    return create_email_template(recommendations_template_name, 'recommendations-email-template',
                                 subject='Retail Demo Store - Products Just for You',
                                 description='Personalized recommendations email template',
                                 recommender_id=None)


def create_location_abandoned_cart_email_template():
    return create_email_template(location_abandoned_cart_template_name, 'location-abandoned-cart-email-template',
                                 subject='Your local store has the products you were looking at!',
                                 description='Abandoned cart email template - for location',
                                 recommender_id=None)


def create_location_offers_email_template(recommender_id):
    return create_email_template(location_offers_recommendations_template_name, 'location-offers-email-template',
                                 subject="You're close to Retail Demo Store! -"
                                         " visit our store today to redeem this offer",
                                 description='Personalized recommendations email template',
                                 recommender_id=recommender_id)


def create_location_abandoned_cart_sms_template():
    return create_sms_template(location_abandoned_cart_template_name,
                               body='Hi {{User.UserAttributes.FirstName}}! You have items in your shopping cart. '
                                    'Grab them now at your local AWS Retail Demo store!',
                               description='Abandoned cart SMS template', recommender_id=None)


def create_location_offers_sms_template(recommender_id):
    return create_sms_template(location_offers_recommendations_template_name,
                               body='Hi {{User.UserAttributes.FirstName}}! Pop into our store near you, use the code '
                                    '{{Recommendations.OfferCode.[0]}} for any purchase and get '
                                    '{{Recommendations.OfferDescription.[0]}}. We are looking forward to seeing you.',
                               description='Personalized recommendations SMS template', recommender_id=recommender_id)


def create_recommendation_sms_template():
    return create_sms_template(sms_recommendation_template_name,
                               body='Retail Demo Store \n'
                                    ' TOP PICK Just For you \n'
                                    ' Shop Now: {{Recommendations.URL.[0]}}',
                               description='Personalized recommendations SMS template',
                               recommender_id=None)


def get_recommender_configuration(recommender_name):
    response = pinpoint.get_recommender_configurations()

    for item in response['ListRecommenderConfigurationsResponse']['Item']:
        if item['Name'] == recommender_name:
            return item

    return None


def create_offers_recommender(pinpoint_personalize_role_arn, personalize_campaign_arn, lambda_function_arn):
    recommender_config = get_recommender_configuration(offers_recommender_name)

    if recommender_config:
        recommender_id = recommender_config['Id']
        logger.warning(f"Deleting previous recommender config for offers with id {recommender_id}")
        pinpoint.delete_recommender_configuration(RecommenderId=recommender_id)

    logger.info('Creating Pinpoint/Personalize recommender for offers')

    response = pinpoint.create_recommender_configuration(
        CreateRecommenderConfiguration={
            'Attributes': {
                # We may wish to push product recommendations
                'Recommendations.Name': 'Product Name',
                'Recommendations.URL': 'Product Detail URL',
                'Recommendations.Category': 'Product Category',
                'Recommendations.Style': 'Product Style',
                'Recommendations.Description': 'Product Description',
                'Recommendations.Price': 'Product Price',
                'Recommendations.ImageURL': 'Product Image URL',
                # We may also wish to push offer recommendations
                'Recommendations.OfferCode': 'Coupon offer code',
                'Recommendations.OfferDescription': 'Coupon offer description',
            },
            'Description': 'Retail Demo Store Personalize recommender for Pinpoint',
            'Name': offers_recommender_name,
            'RecommendationProviderIdType': 'PINPOINT_USER_ID',
            'RecommendationProviderRoleArn': pinpoint_personalize_role_arn,
            'RecommendationProviderUri': personalize_campaign_arn,
            'RecommendationTransformerUri': lambda_function_arn,
            'RecommendationsPerMessage': 1
        }
    )

    recommender_config = response['RecommenderConfigurationResponse']

    return recommender_config['Id']


def get_segment(application_id, segment_name):
    response = pinpoint.get_segments(ApplicationId=application_id)

    for item in response['SegmentsResponse']['Item']:
        if item['Name'] == segment_name:
            return item

    return None


def create_all_email_users_segment(application_id):
    """
    Create a segment from all users for the given channel type. Default channel type: email
    Args:
        application_id: Also Pinpoint project ID.
        channel_type: E.g. 'SMS' 'EMAIL' 'CUSTOM' - see Pinpoint docs

    Returns:
    Segment config. Returns even if already exists.
    """
    segment_name = 'AllEmailUsers'
    segment_config = get_segment(application_id, segment_name)

    if not segment_config:
        logger.info(f'{segment_name} segment does not exist; creating')

        response = pinpoint.create_segment(
            ApplicationId=application_id,
            WriteSegmentRequest={
                'Name': segment_name,
                'SegmentGroups': {
                    'Groups': [
                        {
                            'Dimensions': [
                                {
                                    'Demographic': {
                                        'Channel': {
                                            'DimensionType': 'INCLUSIVE',
                                            'Values': ['EMAIL']
                                        }
                                    }
                                }
                            ],
                            'SourceType': 'ANY',
                            'Type': 'ANY'
                        }
                    ],
                    'Include': 'ALL'
                }
            }
        )

        segment_config = response['SegmentResponse']
    else:
        logger.info(f'{segment_name} segment already exists')

    return segment_config


def create_users_with_cart_segment(application_id, source_segment,
                                   segment_name_suffix='', cart_dimension_type='INCLUSIVE'):
    """
    Create a Pinpoint segment using the HasShoppingCart endpoint attribute. The complement of this segment
    can be obtained by setting cart_dimension_type='EXCLUSIVE'.
    Args:
        application_id (str): Also called Pinpoint project ID.
        all_email_users_segment_id (str): Earlier created all users segment
        cart_dimension_type (str): INCLUSIVE: include users with cart EXCLUSIVE: users without cart
        segment_name_suffix (str): Add to segment name.
    Returns:
        Segment config. Returns even if already exists.
    """

    segment_name = 'Users' + ('With' if cart_dimension_type=='INCLUSIVE' else 'Without') + 'Cart' + segment_name_suffix

    segment_config = get_segment(application_id, segment_name)

    if not segment_config:
        logger.info(f'{segment_name} segment does not exist; creating')

        response = pinpoint.create_segment(
            ApplicationId = application_id,
            WriteSegmentRequest = {
                'Name': segment_name,
                'SegmentGroups': {
                    'Groups': [
                        {
                            'Dimensions': [
                                {
                                    'UserAttributes': {
                                        'HasShoppingCart': {
                                            'AttributeType': cart_dimension_type,
                                            'Values': [ 'true' ]
                                        }
                                      },
                                    'Behavior': {
                                        'Recency': {
                                            'Duration': 'DAY_30',
                                            'RecencyType': 'ACTIVE'
                                        }
                                    }
                                }
                            ],
                            'SourceSegments': [
                                {
                                    'Id': source_segment
                                }
                            ],
                            'SourceType': 'ANY',
                            'Type': 'ANY'
                        }
                    ],
                    'Include': 'ALL'
                }
            }
        )

        segment_config = response['SegmentResponse']
    else:
        logger.info(f'{segment_name} segment already exists')

    return segment_config


def create_users_with_verified_sms_segment(application_id):

    # Note that we do not need to filter on the OptOut property of an endpoint as that is not a generic
    # attribute but has a meaning to Pinpoint and Pinpoint will enforce the opt out.
    segment_name = 'AllSMSUsers'
    segment_config = get_segment(application_id, segment_name)

    if not segment_config:
        logger.info('AllSMSUsers segment does not; creating')

        response = pinpoint.create_segment(
            ApplicationId = application_id,
            WriteSegmentRequest = {
                'Name': segment_name,
                'SegmentGroups': {
                    'Groups': [
                        {
                            'Dimensions': [
                                {
                                    'Demographic': {
                                        'Channel': {
                                            'DimensionType': 'INCLUSIVE',
                                            'Values': [ 'SMS' ]
                                        }
                                    }
                                }
                            ],
                            'SourceType': 'ANY',
                            'Type': 'ANY'
                        }
                    ],
                    'Include': 'ALL'
                }
            }
        )

        segment_config = response['SegmentResponse']
    else:
        logger.info('AllSMSUsers segment already exists')

    return segment_config


def get_campaign(application_id, campaign_name):
    response = pinpoint.get_campaigns(ApplicationId=application_id)

    for item in response['CampaignsResponse']['Item']:
        if item['Name'] == campaign_name:
            return item

    return None


def create_campaign(application_id,
                  segment_id, segment_version,
                  event_type,
                  campaign_name,
                  email_from=None,
                  email_template_name=None,
                  sms_template_name=None,
                  campaign_hook_lambda_arn=None):
    """
    Sets Pinpoint to send messages to users in a particular segment using the provided template and channel
    when event of event_type happens
    Args:
        application_id (str): Also called project ID - pinpoint project
        segment_id (str): Segment for users to run campaign
        segment_version (str): The segment version
        event_type (str): Change this to change the trigger
        campaign_name (str): Name to give this campaign inside the Pinpoint project.
        email_from (Union[str,None]): Where email looks to be coming from in campaign emails. If None do not send email.
        email_template_name (Union[str,None]): The message template to send. If None do not send email.
        sms_template_name (Union[str,None]): The message template to send. If None do not send SMS.
        campaign_hook_lambda_arn (Union[str,None]): The lambda function to use as a campaign hook

    Returns:
        Campaign config.
    """
    campaign_config = get_campaign(application_id, campaign_name)

    if not campaign_config:
        logger.info(f'{campaign_name} campaign does not exist; creating')

        campaign_start = datetime.utcnow() + timedelta(minutes=16)
        campaign_end = campaign_start + timedelta(days=180)

        message_config = {}
        template_config = {}
        campaign_hook = {}
        if email_from is not None and email_template_name is not None:
            if len(email_from) > 0:
                message_config["EmailMessage"] = {"FromAddress": email_from}
                template_config["EmailTemplate"] = {"Name": email_template_name}
            else:
                logger.warning(f"Empty email - not creating campaign {campaign_name}")
                return None
        if (email_template_name and not email_from) or (not email_template_name and email_from):
            logger.error('Specify both or none of "email_from" and "email_template_name"')
        if sms_template_name is not None:
            template_config["SMSTemplate"] = {"Name": sms_template_name}
        if campaign_hook_lambda_arn:
            campaign_hook = {
                                'LambdaFunctionName': campaign_hook_lambda_arn,
                                'Mode': 'FILTER'
                            }

        response = pinpoint.create_campaign(
            ApplicationId=application_id,
            WriteCampaignRequest={
                'Hook': campaign_hook,
                'Name': campaign_name,
                "MessageConfiguration": message_config,
                "Schedule": {
                    "EventFilter": {
                        "Dimensions": {
                            "EventType": {
                                "DimensionType": "INCLUSIVE",
                                "Values": [
                                    event_type
                                ]
                            },
                        },
                        "FilterType": "ENDPOINT"
                    },
                    "Frequency": "EVENT",
                    "IsLocalTime": False,
                    "StartTime": campaign_start.isoformat(timespec='seconds'),
                    "EndTime": campaign_end.isoformat(timespec='seconds')
                },
                "SegmentId": segment_id,
                "SegmentVersion": segment_version,
                "tags": {},
                "TemplateConfiguration": template_config,
            }
        )

        campaign_config = response['CampaignResponse']
    else:
        logger.info(f'{campaign_name} campaign already exists')

    return campaign_config


def delete_event_rule(rule_name):
    ''' Deletes CloudWatch event rule used to trigger this lambda function '''
    try:
        response = cw_events.list_targets_by_rule(Rule = rule_name)

        if len(response['Targets']) > 0:
            logger.info('Removing event targets from rule {}'.format(rule_name))

            target_ids = []

            for target in response['Targets']:
                target_ids.append(target['Id'])

            response = cw_events.remove_targets(
                Rule = rule_name,
                Ids = target_ids
            )

        logger.info('Deleting event rule {}'.format(rule_name))
        cw_events.delete_rule(Name = rule_name)

    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'ResourceNotFoundException':
            logger.warn('CloudWatch event rule to delete not found')
        else:
            logger.error(e)

def lambda_handler(event, context):
    logger.info('## ENVIRONMENT VARIABLES')
    logger.info(os.environ)
    logger.info('## EVENT')
    logger.info(event)

    region = os.environ['AWS_REGION']
    account_id = sts.get_caller_identity()['Account']
    pinpoint_app_id = os.environ['pinpoint_app_id']
    lambda_function_arn = os.environ['pinpoint_recommender_arn']
    offers_lambda_function_arn = os.environ['pinpoint_offers_recommender_arn']
    pinpoint_personalize_role_arn = os.environ['pinpoint_personalize_role_arn']
    email_from_address = os.environ['email_from_address']
    email_from_name = os.environ.get('email_from_name', 'AWS Retail Demo Store')
    # Info on CloudWatch event rule used to repeatedely call this function.
    lambda_event_rule_name = os.environ['lambda_event_rule_name']

    # Create email templates
    create_welcome_email_template()
    create_abandoned_cart_email_template()
    create_recommendations_email_template()        

    # Enable email for Pinpoint project
    email_from = email_from_address
    if email_from_name:
        email_from = '{}<{}>'.format(email_from_name, email_from_address)

    logger.info('Enabling email channel for Pinpoint project')
    response = pinpoint.update_email_channel(
        ApplicationId = pinpoint_app_id,
        EmailChannelRequest={
            'Enabled': True,
            'FromAddress': email_from,
            'Identity': 'arn:aws:ses:{}:{}:identity/{}'.format(region, account_id, email_from_address)
        }
    )

    logger.debug(json.dumps(response, indent = 2, default = str))

    # Create AllEmailUsers segment
    segment_config = create_all_email_users_segment(pinpoint_app_id)
    logger.debug(json.dumps(segment_config, indent = 2, default = str))
    all_email_users_segment_id = segment_config['Id']
    all_email_users_segment_version = segment_config['Version']

    # Create UsersWithCartEmail segment
    segment_config = create_users_with_cart_segment(pinpoint_app_id, all_email_users_segment_id,
                                                    segment_name_suffix='Email')
    logger.debug('Email cart segment config: ' + json.dumps(segment_config, indent=2, default=str))
    email_users_with_cart_segment_id = segment_config['Id']
    email_users_with_cart_segment_version = segment_config['Version']

    # Create Welcome campaign (triggered on sign up)
    welcome_campaign_config = create_campaign(
        pinpoint_app_id, all_email_users_segment_id, all_email_users_segment_version,
        event_type="UserSignedUp", campaign_name='WelcomeEmail',
        email_from=email_from, email_template_name=welcome_template_name, sms_template_name=None)
    logger.debug('welcome_campaign_config:'+json.dumps(welcome_campaign_config,
                                                       indent=2, default=str))

    # Create Abandoned Cart campaign (triggered on session stop)
    abandoned_cart_campaign_config = create_campaign(
        pinpoint_app_id, email_users_with_cart_segment_id, email_users_with_cart_segment_version,
        event_type="_session.stop", campaign_name='AbandonedCartEmail',
        email_from=email_from, email_template_name=abandoned_cart_template_name, sms_template_name=None)
    logger.debug('abandoned_cart_campaign_config:'+json.dumps(abandoned_cart_campaign_config,
                                                       indent=2, default=str))

    # Now let us set up SMS segments and campaigns.

    # Are we set up to send SMS?
    response = ssm.get_parameter(Name='retaildemostore-pinpoint-sms-longcode')
    pinpoint_sms_long_code = response['Parameter']['Value']

    if(pinpoint_sms_long_code != 'NONE'):

        logger.info('Enabling SMS channel for Pinpoint project...')
        update_sms_channel_response = pinpoint.update_sms_channel(
            ApplicationId = pinpoint_app_id,
            SMSChannelRequest={
                'Enabled': True,
                'ShortCode': pinpoint_sms_long_code
            }
        )

    else:

        logger.info('Enabling SMS channel for Pinpoint project (no long code)...')
        update_sms_channel_response = pinpoint.update_sms_channel(
            ApplicationId=pinpoint_app_id,
            SMSChannelRequest={
                'Enabled': True
            }
        )

    logger.debug('SMS enable response: ' + json.dumps(update_sms_channel_response, indent = 2, default = str))

    logger.info('Creating SMS templates')
    create_recommendation_sms_template()        

    # create AllSMSUsers segment
    segment_config = create_users_with_verified_sms_segment(pinpoint_app_id)
    all_sms_users_segment_id = segment_config['Id']
    all_sms_users_segment_version = segment_config['Version']

    # Create UsersWithCartSMS segment
    segment_config = create_users_with_cart_segment(pinpoint_app_id, all_sms_users_segment_id,
                                                    segment_name_suffix='SMS')
    logger.debug('SMS cart segment config: ' + json.dumps(segment_config, indent=2, default=str))
    sms_users_with_cart_segment_id = segment_config['Id']
    sms_users_with_cart_segment_version = segment_config['Version']

    # Create SMS alerts Campaign
    sms_signup_recommendations_campaign_config_sms = create_campaign(
        pinpoint_app_id, all_sms_users_segment_id,
        all_sms_users_segment_version,
        event_type='UserVerifiedSMS', campaign_name='SMSAlerts',
        email_from=None, email_template_name=None,
        sms_template_name=sms_recommendation_template_name,
        campaign_hook_lambda_arn=lambda_function_arn)
    logger.debug(
        'sms_signup_recommendations_campaign_config_sms:' + json.dumps(sms_signup_recommendations_campaign_config_sms,
                                                                    indent=2, default=str))

    # If offers campaign and geofence are not deployed, there is no point deploying these campaigns as
    # geofence will not trigger.
    if do_deploy_offers_campaign:
        response = ssm.get_parameter(Name='/retaildemostore/personalize/personalized-offers-arn')
        offers_campaign_arn = response['Parameter']['Value']
        assert offers_campaign_arn != 'NONE', 'Personalize Offers Campaign ARN not initialized'
        logger.info('Personalize Offers Campaign ARN: ' + offers_campaign_arn)

        offers_recommender_id = create_offers_recommender(pinpoint_personalize_role_arn, offers_campaign_arn, offers_lambda_function_arn)
        logger.info('Pinpoint offers configuration ID: ' + str(offers_recommender_id))

        create_location_offers_email_template(offers_recommender_id)
        create_location_abandoned_cart_email_template()

        # Create Abandoned Cart campaign with Location geofence
        location_abandoned_cart_campaign_config = create_campaign(
            pinpoint_app_id, email_users_with_cart_segment_id, email_users_with_cart_segment_version,
            event_type=GEOFENCE_PINPOINT_EVENTTYPE, campaign_name='LocationAbandonedCartCampaign',
            email_from=email_from, email_template_name=location_abandoned_cart_template_name, sms_template_name=None)
        logger.debug('location_abandoned_cart_campaign_config:' + json.dumps(location_abandoned_cart_campaign_config,
                                                                             indent=2, default=str))
        # Send an offer when a user approaches your store.
        location_recommender_campaign_config = create_campaign(
            pinpoint_app_id, all_email_users_segment_id, all_email_users_segment_version,
            event_type=GEOFENCE_PINPOINT_EVENTTYPE, campaign_name='LocationRecommendationsCampaign',
            email_from=email_from, email_template_name=location_offers_recommendations_template_name, sms_template_name=None)
        logger.debug('location_recommender_campaign_config:'+json.dumps(location_recommender_campaign_config,
                                                                        indent=2, default=str))

        # Location demo: When the user gets near our geofence (local store) and they have products in their cart
        # we tell them to come pick them up.
        location_abandoned_cart_campaign_config_sms = create_campaign(
            pinpoint_app_id, sms_users_with_cart_segment_id,
            sms_users_with_cart_segment_version,
            event_type=GEOFENCE_PINPOINT_EVENTTYPE, campaign_name='LocationAbandonedCartCampaignSMS',
            email_from=None, email_template_name=None,
            sms_template_name=location_abandoned_cart_template_name)
        logger.debug(
            'location_abandoned_cart_campaign_config sms:' + json.dumps(location_abandoned_cart_campaign_config_sms,
                                                                        indent=2, default=str))

        # Location demo: When a user gets near a store we want to send a recommendation of an offer
        location_recommender_campaign_config_sms = create_campaign(
            pinpoint_app_id, all_sms_users_segment_id,
            all_sms_users_segment_version,
            event_type=GEOFENCE_PINPOINT_EVENTTYPE, campaign_name='LocationRecommendationsCampaignSMS',
            email_from=None, email_template_name=None, sms_template_name=location_offers_recommendations_template_name)
        logger.debug('location_recommender_campaign_config_sms:' + json.dumps(location_recommender_campaign_config_sms,
                                                                          indent=2, default=str))
        
        create_location_offers_sms_template(offers_recommender_id)
        create_location_abandoned_cart_sms_template()

        # No need for this lambda function to be called anymore so delete CW event rule that has been calling us.
        delete_event_rule(lambda_event_rule_name)

    return {
        'statusCode': 200,
        'body': json.dumps('Pinpoint workshop resources successfully provisioned!')
    }