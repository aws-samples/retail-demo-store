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
from collections import defaultdict

GEOFENCE_PINPOINT_EVENTTYPE = 'WaypointApproachLocalShop'

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ssm = boto3.client('ssm')
sts = boto3.client('sts')
pinpoint = boto3.client('pinpoint')
cw_events = boto3.client('events')

welcome_template_name = 'RetailDemoStore-Welcome'
abandoned_cart_template_name = 'RetailDemoStore-AbandonedCart'
recommendations_template_name = 'RetailDemoStore-Recommendations'

recommender_name = 'retaildemostore-recommender'
offers_recommender_name = 'retaildemooffers-recommender'

waypoint_abandoned_cart_template_name = 'RetailDemoStore-WaypointAbandonedCart'
waypoint_offers_recommendations_template_name = 'RetailDemoStore-WaypointOfferRecommendations'


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
        Email template config. Returns even if already exists.
    """
    try:
        response = pinpoint.get_email_template(TemplateName=template_name)
        logger.info(f'Email message template {template_name }already exists')
        return response['EmailTemplateResponse']
    except pinpoint.exceptions.NotFoundException:
        logger.info(f'Template {template_name} does not exist; creating')

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

        response = pinpoint.create_email_template(
            EmailTemplateRequest=request,
            TemplateName=template_name
        )

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
    try:
        response = pinpoint.get_sms_template(TemplateName=template_name)
        logger.info(f'{template_name} SMS message template already exists')
        return response['SMSTemplateResponse']
    except pinpoint.exceptions.NotFoundException:
        logger.info(f'{template_name} SMS message template does not exist; creating')

        request = {
            'TemplateDescription': description,
            'Body': body,
            'DefaultSubstitutions': json.dumps({
                'User.UserAttributes.FirstName': 'there'
            })
        }

        if recommender_id is not None:
            request['RecommenderId'] = recommender_id

        response = pinpoint.create_sms_template(
            SMSTemplateRequest=request,
            TemplateName=template_name
        )

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


def create_recommendations_email_template(recommender_id):
    return create_email_template(recommendations_template_name, 'recommendations-email-template',
                                 subject='Retail Demo Store - Products Just for You',
                                 description='Personalized recommendations email template',
                                 recommender_id=recommender_id)


def create_waypoint_abandoned_cart_email_template():
    return create_email_template(waypoint_abandoned_cart_template_name, 'waypoint-abandoned-cart-email-template',
                                 subject='Your local store has the products you were looking at!',
                                 description='Abandoned cart email template - for waypoint',
                                 recommender_id=None)


def create_waypoint_offers_email_template(recommender_id):
    return create_email_template(waypoint_offers_recommendations_template_name, 'waypoint-offers-email-template',
                                 subject="You're close to Retail Demo Store! -"
                                         " visit our store today to redeem this offer",
                                 description='Personalized recommendations email template',
                                 recommender_id=recommender_id)


def create_waypoint_abandoned_cart_sms_template():
    return create_sms_template(waypoint_abandoned_cart_template_name,
                               body='Hi {{User.UserAttributes.FirstName}}! You have items in your shopping cart. '
                                    'Grab them now at your local AWS Retail Demo store!',
                               description='Abandoned cart SMS template', recommender_id=None)


def create_waypoint_offers_sms_template(recommender_id):
    return create_sms_template(waypoint_offers_recommendations_template_name,
                               body='Hi {{User.UserAttributes.FirstName}}! Pop into our store near you, use the code '
                                    '{{Recommendations.OfferCode.[0]}} for any purchase and get'
                                    '{{Recommendations.OfferDescription.[0]}}. We are looking forward to seeing you.',
                               description='Personalized recommendations SMS template', recommender_id=recommender_id)


def get_recommender_configuration(recommender_name):
    response = pinpoint.get_recommender_configurations()

    for item in response['ListRecommenderConfigurationsResponse']['Item']:
        if item['Name'] == recommender_name:
            return item

    return None


def create_recommender(pinpoint_personalize_role_arn, personalize_campaign_arn, lambda_function_arn):
    recommender_config = get_recommender_configuration(recommender_name)

    if not recommender_config:
        logger.info('Pinpoint/Personalize recommender does not exist; creating')

        response = pinpoint.create_recommender_configuration(
            CreateRecommenderConfiguration={
                'Attributes': {
                    'Recommendations.Name': 'Product Name',
                    'Recommendations.URL': 'Product Detail URL',
                    'Recommendations.Category': 'Product Category',
                    'Recommendations.Style': 'Product Style',
                    'Recommendations.Description': 'Product Description',
                    'Recommendations.Price': 'Product Price',
                    'Recommendations.ImageURL': 'Product Image URL'
                },
                'Description': 'Retail Demo Store Personalize recommender for Pinpoint',
                'Name': recommender_name,
                'RecommendationProviderIdType': 'PINPOINT_USER_ID',
                'RecommendationProviderRoleArn': pinpoint_personalize_role_arn,
                'RecommendationProviderUri': personalize_campaign_arn,
                'RecommendationTransformerUri': lambda_function_arn,
                'RecommendationsPerMessage': 4
            }
        )

        recommender_config = response['RecommenderConfigurationResponse']
    else:
        logger.info('Pinpoint/Personalize recommender already exists')

    return recommender_config['Id']


def create_offers_recommender(pinpoint_personalize_role_arn, personalize_campaign_arn, lambda_function_arn):
    recommender_config = get_recommender_configuration(offers_recommender_name)

    if not recommender_config:
        logger.info('Pinpoint/Personalize recommender for offers does not exist; creating')

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
    else:
        logger.info('Pinpoint/Personalize recommender for offers already exists')

    return recommender_config['Id']


def get_segment(application_id, segment_name):
    response = pinpoint.get_segments(ApplicationId=application_id)

    for item in response['SegmentsResponse']['Item']:
        if item['Name'] == segment_name:
            return item

    return None


def create_all_users_segment(application_id, channel_type='EMAIL'):
    """
    Create a segment from all users for the given channel type. Default channel type: email
    Args:
        application_id: Also Pinpoint project ID.
        channel_type: E.g. 'SMS' 'EMAIL' 'CUSTOM' - see Pinpoint docs

    Returns:
    Segment config. Returns even if already exists.
    """
    segment_name = f'All{channel_type}Users'
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
                                            'Values': [channel_type]
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


def create_users_with_cart_segment(application_id, all_email_users_segment_id, cart_dimension_type='INCLUSIVE',
                                   segment_name_suffix=''):
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
        logger.info(f'{segment_name} segment does not; creating')

        response = pinpoint.create_segment(
            ApplicationId = application_id,
            WriteSegmentRequest = {
                'Name': segment_name,
                'SegmentGroups': {
                    'Groups': [
                        {
                            'Dimensions': [
                                {
                                    'Attributes': {
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
                                    'Id': all_email_users_segment_id
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
                  email_from,
                  email_template_name,
                  sms_template_name):
    """
    Sets Pinpoint to send emails to users in a particular segment using email template RetailDemoStore-AbandonedCart
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
        if email_from is not None and email_template_name is not None:
            message_config["EmailMessage"] = {"FromAddress": email_from}
            template_config["EmailTemplate"] = {"Name": email_template_name}
        if (email_template_name and not email_from) or (not email_template_name and email_from):
            logger.error('Specify both or none of "email_from" and "email_template_name"')
        if sms_template_name is not None:
            template_config["SMSTemplate"] = {"Name": sms_template_name}

        response = pinpoint.create_campaign(
            ApplicationId=application_id,
            WriteCampaignRequest={
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
    logger.debug('## ENVIRONMENT VARIABLES')
    logger.debug(os.environ)
    logger.debug('## EVENT')
    logger.debug(event)

    region = os.environ['AWS_REGION']
    account_id = sts.get_caller_identity()['Account']
    pinpoint_app_id = os.environ['pinpoint_app_id']
    lambda_function_arn = os.environ['pinpoint_recommender_arn']
    offers_lambda_function_arn = os.environ['pinpoint_offers_recommender_arn']
    pinpoint_personalize_role_arn = os.environ['pinpoint_personalize_role_arn']
    email_from_address = os.environ['email_from_address']
    email_from_name = os.environ.get('email_from_name', 'AWS Retail Demo Store')

    response = ssm.get_parameter(Name='retaildemostore-product-recommendation-campaign-arn')
    personalize_campaign_arn = response['Parameter']['Value']

    response = ssm.get_parameter(Name='retaildemostore-personalized-offers-campaign-arn')
    offers_campaign_arn = response['Parameter']['Value']

    assert personalize_campaign_arn != 'NONE', 'Personalize Campaign ARN not initialized'

    logger.info('Personalize Campaign ARN: ' + personalize_campaign_arn)

    recommender_id = create_recommender(pinpoint_personalize_role_arn, personalize_campaign_arn, lambda_function_arn)
    logger.info('Pinpoint recommender configuration ID: ' + str(recommender_id))

    offers_recommender_id = create_offers_recommender(pinpoint_personalize_role_arn, offers_campaign_arn, offers_lambda_function_arn)
    logger.info('Pinpoint offers configuration ID: ' + str(recommender_id))

    # Create email templates
    create_welcome_email_template()
    create_abandoned_cart_email_template()
    create_recommendations_email_template(recommender_id)

    create_waypoint_offers_email_template(offers_recommender_id)
    create_waypoint_offers_sms_template(offers_recommender_id)
    create_waypoint_abandoned_cart_sms_template()
    create_waypoint_abandoned_cart_email_template()

    # Enable email for Pinpoint project
    email_from = email_from_address
    if email_from_name:
        email_from = '{}<{}>'.format(email_from_name, email_from_address)

    logger.info('Enabling email channel for Pinpoint project...')
    response = pinpoint.update_email_channel(
        ApplicationId=pinpoint_app_id,
        EmailChannelRequest={
            'Enabled': True,
            'FromAddress': email_from,
            'Identity': 'arn:aws:ses:{}:{}:identity/{}'.format(region, account_id, email_from_address)
        }
    )
    logger.debug(json.dumps(response, indent=2, default=str))

    # Enable SMS for Pinpoint project
    logger.info('Enabling SMS channel for Pinpoint project...')
    response = pinpoint.update_sms_channel(
        ApplicationId=pinpoint_app_id,
        SMSChannelRequest={
            'Enabled': True
        }
    )
    logger.debug(json.dumps(response, indent=2, default=str))

    segments = defaultdict(lambda: defaultdict(dict))

    for channel_type in ['EMAIL', 'SMS']:
        allusers_segment_config = create_all_users_segment(pinpoint_app_id, channel_type)
        logger.debug('All users segment config: ' + json.dumps(allusers_segment_config, indent=2, default=str))
        segments['AllUsers'][channel_type] = allusers_segment_config

        for cart_dimension_type in ['INCLUSIVE', 'EXCLUSIVE']:
            segment_config = create_users_with_cart_segment(pinpoint_app_id, allusers_segment_config['Id'],
                                                            cart_dimension_type=cart_dimension_type,
                                                            segment_name_suffix=channel_type)

            logger.debug('Cart segment config: ' + json.dumps(segment_config, indent=2, default=str))
            segments['Cart'][cart_dimension_type][channel_type] = segment_config

    # Create Welcome campaign (triggered on sign up)
    welcome_campaign_config = create_campaign(
        pinpoint_app_id, segments['AllUsers']['EMAIL']['Id'], segments['AllUsers']['EMAIL']['Version'],
        event_type="UserSignedUp", campaign_name='WelcomeEmail',
        email_from=email_from, email_template_name=welcome_template_name, sms_template_name=None)
    logger.debug('welcome_campaign_config:'+json.dumps(welcome_campaign_config, indent = 2, default = str))

    # Create Abandoned Cart campaign (triggered on session stop)
    abandoned_cart_campaign_config = create_campaign(
        pinpoint_app_id, segments['Cart']['INCLUSIVE']['EMAIL']['Id'], segments['Cart']['INCLUSIVE']['EMAIL']['Version'],
        event_type="_session.stop", campaign_name='AbandonedCartEmail',
        email_from=email_from, email_template_name=abandoned_cart_template_name, sms_template_name=None)
    logger.debug('abandoned_cart_campaign_config:'+json.dumps(abandoned_cart_campaign_config, indent = 2, default = str))

    # ##############

    # Create Abandoned Cart campaign with Waypoint geofence
    waypoint_abandoned_cart_campaign_config = create_campaign(
        pinpoint_app_id, segments['Cart']['INCLUSIVE']['EMAIL']['Id'], segments['Cart']['INCLUSIVE']['EMAIL']['Version'],
        event_type=GEOFENCE_PINPOINT_EVENTTYPE, campaign_name='WaypointAbandonedCartCampaign',
        email_from=email_from, email_template_name=waypoint_abandoned_cart_template_name, sms_template_name=None)
    logger.debug('waypoint_abandoned_cart_campaign_config:'+json.dumps(waypoint_abandoned_cart_campaign_config,
                                                                       indent=2, default=str))

    # When there is no cart waiting we want to send a recommendation
    waypoint_recommender_campaign_config = create_campaign(
        pinpoint_app_id, segments['AllUsers']['EMAIL']['Id'], segments['AllUsers']['EMAIL']['Version'],
        event_type=GEOFENCE_PINPOINT_EVENTTYPE, campaign_name='WaypointRecommendationsCampaign',
        email_from=email_from, email_template_name=waypoint_offers_recommendations_template_name, sms_template_name=None)
    logger.debug('waypoint_recommender_campaign_config:'+json.dumps(waypoint_recommender_campaign_config,
                                                                    indent=2, default = str))

    # Waypoint demo: When the user gets near our geofence (local store) and they have products in their cart
    # we tell them to come pick them up.
    waypoint_abandoned_cart_campaign_config_sms = create_campaign(
        pinpoint_app_id, segments['Cart']['INCLUSIVE']['SMS']['Id'], segments['Cart']['INCLUSIVE']['SMS']['Version'],
        event_type=GEOFENCE_PINPOINT_EVENTTYPE, campaign_name='WaypointAbandonedCartCampaignSMS',
        email_from=None, email_template_name=None, sms_template_name=waypoint_abandoned_cart_template_name)
    logger.debug('waypoint_abandoned_cart_campaign_config sms:'+json.dumps(waypoint_abandoned_cart_campaign_config_sms,
                                                                       indent=2, default=str))

    # Waypoint demo: When there is no cart waiting we want to send a recommendation of an offer instead
    waypoint_recommender_campaign_config_sms = create_campaign(
        pinpoint_app_id, segments['AllUsers']['SMS']['Id'],
        segments['AllUsers']['SMS']['Version'],
        event_type=GEOFENCE_PINPOINT_EVENTTYPE, campaign_name='WaypointRecommendationsCampaignSMS',
        email_from=None, email_template_name=None, sms_template_name=waypoint_offers_recommendations_template_name)
    logger.debug('waypoint_recommender_campaign_config sms:' + json.dumps(waypoint_recommender_campaign_config_sms,
                                                                      indent=2, default=str))

    return {
        'statusCode': 200,
        'body': json.dumps('Pinpoint workshop resources successfully provisioned!')
    }