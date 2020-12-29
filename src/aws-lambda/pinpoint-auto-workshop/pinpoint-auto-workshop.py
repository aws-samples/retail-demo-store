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
import botocore
import logging
import os
from datetime import datetime, timedelta
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ssm = boto3.client('ssm')
sts = boto3.client('sts')
pinpoint = boto3.client('pinpoint')
cw_events = boto3.client('events')

welcome_template_name = 'RetailDemoStore-Welcome'
abandoned_cart_template_name = 'RetailDemoStore-AbandonedCart'
recommendations_template_name = 'RetailDemoStore-Recommendations'
sms_recommendation_template_name = 'RetailDemoStore-SMSRecommendations'

recommender_name = 'retaildemostore-recommender'

def create_welcome_email_template():
    try:
        response = pinpoint.get_email_template(TemplateName=welcome_template_name)
        logger.info('Welcome email message template already exists')
        return response['EmailTemplateResponse']
    except pinpoint.exceptions.NotFoundException:
        logger.info('Welcome email message template does not exist; creating')

        with open('pinpoint-templates/welcome-email-template.html', 'r') as html_file:
            html_template = html_file.read()

        with open('pinpoint-templates/welcome-email-template.txt', 'r') as text_file:
            text_template = text_file.read()

        response = pinpoint.create_email_template(
            EmailTemplateRequest={
                'Subject': 'Welcome to the Retail Demo Store',
                'TemplateDescription': 'Welcome email sent to new customers',
                'HtmlPart': html_template,
                'TextPart': text_template,
                'DefaultSubstitutions': json.dumps({
                    'User.UserAttributes.FirstName': 'there'
                })
            },
            TemplateName=welcome_template_name
        )

        return response['CreateTemplateMessageBody']

def create_abandoned_cart_email_template():
    try:
        response = pinpoint.get_email_template(TemplateName=abandoned_cart_template_name)
        logger.info('Abandoned cart email message template already exists')
        return response['EmailTemplateResponse']
    except pinpoint.exceptions.NotFoundException:
        logger.info('Abandoned cart email message template does not exist; creating')

        with open('pinpoint-templates/abandoned-cart-email-template.html', 'r') as html_file:
            html_template = html_file.read()

        with open('pinpoint-templates/abandoned-cart-email-template.txt', 'r') as text_file:
            text_template = text_file.read()

        response = pinpoint.create_email_template(
            EmailTemplateRequest={
                'Subject': 'Retail Demo Store - Motivation to Complete Your Order',
                'TemplateDescription': 'Abandoned cart email template',
                'HtmlPart': html_template,
                'TextPart': text_template,
                'DefaultSubstitutions': json.dumps({
                    'User.UserAttributes.FirstName': 'there'
                })   
            },
            TemplateName=abandoned_cart_template_name
        )

        return response['CreateTemplateMessageBody']

def create_recommendations_email_template(recommender_id):
    try:
        response = pinpoint.get_email_template(TemplateName=recommendations_template_name)
        logger.info('Recommendations email message template already exists')
        return response['EmailTemplateResponse']
    except pinpoint.exceptions.NotFoundException:
        logger.info('Recommendations email message template does not exist; creating')

        with open('pinpoint-templates/recommendations-email-template.html', 'r') as html_file:
            html_template = html_file.read()

        with open('pinpoint-templates/recommendations-email-template.txt', 'r') as text_file:
            text_template = text_file.read()

        response = pinpoint.create_email_template(
            EmailTemplateRequest={
                'Subject': 'Retail Demo Store - Products Just for You',
                'TemplateDescription': 'Personalized recommendations email template',
                'RecommenderId': recommender_id,
                'HtmlPart': html_template,
                'TextPart': text_template,
                'DefaultSubstitutions': json.dumps({
                    'User.UserAttributes.FirstName': 'there'
                })
            },
            TemplateName=recommendations_template_name
        )

        return response['CreateTemplateMessageBody']

def create_recommendation_sms_template(recommender_id):
    try:
        response = pinpoint.get_sms_template(TemplateName=sms_recommendation_template_name)
        logger.info('Recommendations SMS template already exists')
        return response['SMSTemplateResponse']
    except pinpoint.exceptions.NotFoundException:
        logger.info('Recommendations SMS template does not exist; creating')

        response = pinpoint.create_sms_template(
            SMSTemplateRequest={
                'Body': 'Retail Demo Store \n TOP PICK Just For you \n Shop Now: {{Recommendations.URL.[0]}}',
                'TemplateDescription': 'Personalized recommendations SMS template',
                'RecommenderId': recommender_id,
                'DefaultSubstitutions': json.dumps({
                    'User.UserAttributes.FirstName': 'there'
                })
            },
            TemplateName=sms_recommendation_template_name
        )

        return response['CreateTemplateMessageBody']

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

def get_segment(application_id, segment_name):
    response = pinpoint.get_segments(ApplicationId=application_id)
    
    for item in response['SegmentsResponse']['Item']:
        if item['Name'] == segment_name:
            return item
        
    return None

def create_all_email_users_segment(application_id):
    segment_name = 'AllEmailUsers'
    segment_config = get_segment(application_id, segment_name)
    
    if not segment_config:
        logger.info('AllEmailUsers segment does not; creating')

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
                                            'Values': [ 'EMAIL' ]
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
        logger.info('AllEmailUsers segment already exists')
        
    return segment_config

def create_users_with_cart_segment(application_id, all_email_users_segment_id):
    segment_name = 'UsersWithCart'
    segment_config = get_segment(application_id, segment_name)
    
    if not segment_config:
        logger.info('UsersWithCart segment does not; creating')

        response = pinpoint.create_segment(
            ApplicationId = application_id,
            WriteSegmentRequest = {
                'Name': 'UsersWithCart',
                'SegmentGroups': {
                    'Groups': [
                        {
                            'Dimensions': [
                                {
                                    'Attributes': {
                                        'HasShoppingCart': {
                                            'AttributeType': 'INCLUSIVE',
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
        logger.info('UsersWithCart segment already exists')
        
    return segment_config

def create_users_with_verified_sms_segment(application_id):
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

def create_welcome_campaign(application_id, email_from, all_email_users_segment_id, all_email_users_segment_version):
    campaign_name = 'WelcomeEmail'
    campaign_config = get_campaign(application_id, campaign_name)
    
    if not campaign_config:
        logger.info('WelcomeEmail campaign does not exist; creating')

        campaign_start = datetime.now() + timedelta(minutes=20)
        campaign_end = campaign_start + timedelta(days=180)

        response = pinpoint.create_campaign(
            ApplicationId = application_id,
            WriteCampaignRequest = {
                'Name': campaign_name,
                "MessageConfiguration": {
                    "EmailMessage": {
                        "FromAddress": email_from
                    }
                },
                "Schedule": {
                    "EventFilter": {
                        "Dimensions": {
                            "EventType": {
                                "DimensionType": "INCLUSIVE",
                                "Values": [
                                    "UserSignedUp"
                                ]
                            },
                        },
                        "FilterType": "ENDPOINT"
                    },
                    "Frequency": "EVENT",
                    "IsLocalTime": False,
                    "StartTime": campaign_start.isoformat(timespec = 'seconds'),
                    "EndTime": campaign_end.isoformat(timespec = 'seconds')
                },
                "SegmentId": all_email_users_segment_id,
                "SegmentVersion": all_email_users_segment_version,
                "tags": {},
                "TemplateConfiguration": {
                    "EmailTemplate": {
                        "Name": "RetailDemoStore-Welcome"
                    }
                },
            }
        )
        
        campaign_config = response['CampaignResponse']
    else:
        logger.info('WelcomeEmail campaign already exists')
    
    return campaign_config

def create_abandoned_cart_campaign(application_id, email_from, users_with_cart_segment_id, users_with_cart_segment_version):
    campaign_name = 'AbandonedCartEmail'
    campaign_config = get_campaign(application_id, campaign_name)
    
    if not campaign_config:
        logger.info('AbandonedCartEmail campaign does not exist; creating')

        campaign_start = datetime.now() + timedelta(minutes=20)
        campaign_end = campaign_start + timedelta(days=180)
        
        response = pinpoint.create_campaign(
            ApplicationId = application_id,
            WriteCampaignRequest = {
                'Name': campaign_name,
                "MessageConfiguration": {
                    "EmailMessage": {
                        "FromAddress": email_from
                    }
                },
                "Schedule": {
                    "EventFilter": {
                        "Dimensions": {
                            "EventType": {
                                "DimensionType": "INCLUSIVE",
                                "Values": [
                                    "_session.stop"
                                ]
                            },
                        },
                        "FilterType": "ENDPOINT"
                    },
                    "Frequency": "EVENT",
                    "IsLocalTime": False,
                    "StartTime": campaign_start.isoformat(timespec = 'seconds'),
                    "EndTime": campaign_end.isoformat(timespec = 'seconds')
                },
                "SegmentId": users_with_cart_segment_id,
                "SegmentVersion": users_with_cart_segment_version,
                "tags": {},
                "TemplateConfiguration": {
                    "EmailTemplate": {
                        "Name": "RetailDemoStore-AbandonedCart"
                    }
                },
            }
        )
        
        campaign_config = response['CampaignResponse']
    else:
        logger.info('AbandonedCartEmail campaign already exists')
    
    return campaign_config

def create_sms_alerts_campaign(application_id, sms_long_code, all_sms_users_segment_id, all_sms_users_segment_version):
    campaign_name = 'SMSAlerts'
    campaign_config = get_campaign(application_id, campaign_name)
    if not campaign_config:
        logger.info('SMSAlerts campaign does not exist; creating')

        campaign_start = datetime.now() + timedelta(minutes=20)
        campaign_end = campaign_start + timedelta(days=180)
        
        response = pinpoint.create_campaign(
            ApplicationId = application_id,
            WriteCampaignRequest = {
                'Name': campaign_name,
                "MessageConfiguration": {
                    "SMSMessage": {
                        "MessageType": "TRANSACTIONAL"
                    }
                },
                "Schedule": {
                    "EventFilter": {
                        "Dimensions": {
                            "EventType": {
                                "DimensionType": "INCLUSIVE",
                                "Values": [
                                    "UserVerifiedSMS"
                                ]
                            },
                        },
                        "FilterType": "ENDPOINT"
                    },
                    "Frequency": "EVENT",
                    "IsLocalTime": False,
                    "StartTime": campaign_start.isoformat(timespec = 'seconds'),
                    "EndTime": campaign_end.isoformat(timespec = 'seconds')
                },
                "SegmentId": all_sms_users_segment_id,
                "SegmentVersion": all_sms_users_segment_version,
                "tags": {},
                "TemplateConfiguration": {
                    "SMSTemplate": {
                        "Name": sms_recommendation_template_name
                    }
                },
            }
        )
        
        campaign_config = response['CampaignResponse']
    else:
        logger.info('SMS alerts campaign already exists')
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
    pinpoint_personalize_role_arn = os.environ['pinpoint_personalize_role_arn']
    email_from_address = os.environ['email_from_address']
    email_from_name = os.environ.get('email_from_name', 'AWS Retail Demo Store')
    # Info on CloudWatch event rule used to repeatedely call this function.
    lambda_event_rule_name = os.environ['lambda_event_rule_name']

    response = ssm.get_parameter(Name='retaildemostore-product-recommendation-campaign-arn')
    personalize_campaign_arn = response['Parameter']['Value']

    assert personalize_campaign_arn != 'NONE', 'Personalize Campaign ARN not initialized'

    logger.info('Personalize Campaign ARN: ' + personalize_campaign_arn)

    recommender_id = create_recommender(pinpoint_personalize_role_arn, personalize_campaign_arn, lambda_function_arn)
    logger.info('Pinpoint recommender configuration ID: ' + recommender_id)

    # Create email templates
    create_welcome_email_template()
    create_abandoned_cart_email_template()
    create_recommendations_email_template(recommender_id)

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

    # Create UsersWithCart segment
    segment_config = create_users_with_cart_segment(pinpoint_app_id, all_email_users_segment_id)
    logger.debug(json.dumps(segment_config, indent = 2, default = str))
    users_with_cart_segment_id = segment_config['Id']
    users_with_cart_segment_version = segment_config['Version']

    # Create Welcome campaign
    campaign_config = create_welcome_campaign(pinpoint_app_id, email_from, all_email_users_segment_id, all_email_users_segment_version)
    logger.debug(json.dumps(campaign_config, indent = 2, default = str))

    # Create Abandoned Cart campaign
    campaign_config = create_abandoned_cart_campaign(pinpoint_app_id, email_from, users_with_cart_segment_id, users_with_cart_segment_version)
    logger.debug(json.dumps(campaign_config, indent = 2, default = str))

    response = ssm.get_parameter(Name='retaildemostore-pinpoint-sms-longcode')
    pinpoint_sms_long_code = response['Parameter']['Value']

    if(pinpoint_sms_long_code != 'NONE'):
        logger.info('Creating SMS recommendation template template')
        create_recommendation_sms_template(recommender_id)
        logger.info('Enabling SMS channel for Pinpoint project')
        update_sms_channel_response = pinpoint.update_sms_channel(
            ApplicationId = pinpoint_app_id,
            SMSChannelRequest={
                'Enabled': True,
                'ShortCode': pinpoint_sms_long_code
            }
        )
        logger.debug(json.dumps(update_sms_channel_response, indent = 2, default = str))
        # create AllSMSUsers segment
        segment_config = create_users_with_verified_sms_segment(pinpoint_app_id)
        all_sms_users_segment_id = segment_config['Id']
        all_sms_users_segment_version = segment_config['Version']

        # Create SMS alerts Campaign
        campaign_config = create_sms_alerts_campaign(pinpoint_app_id, pinpoint_sms_long_code, all_sms_users_segment_id, all_sms_users_segment_version)
        logger.debug(json.dumps(campaign_config, indent = 2, default = str))
    else:
        print('Pinpoint SMS long code value not set. Please set the value for Pinpoint SMS Long code in SSM Parameters. Refer to Messaging workshop to know more details.')
    # No need for this lambda function to be called anymore so delete CW event rule that has been calling us.
    delete_event_rule(lambda_event_rule_name)

    return {
        'statusCode': 200,
        'body': json.dumps('Pinpoint workshop resources successfully provisioned!')
    }