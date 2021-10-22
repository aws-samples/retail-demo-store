# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

"""
Lambda function designed to be called when the Pinpoint Incoming Messages SNS Topic 
receives confirmation message from user to opt in for text alerts.

This function will update the end point and opt in the user to receive one time text
alerts using Amazon Pinpoint.

This function will be executed every time any user wishes to opt in for text messages.
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

def updateEndpointOptIn(originationNumber, timestamp, applicationId):
    endpointId = originationNumber[1:]
    update_endpoint_response = pinpoint.update_endpoint(
        ApplicationId = applicationId,
        EndpointId = endpointId,
        EndpointRequest = {
            'Address': originationNumber[1:],
            'ChannelType':'SMS',
            'OptOut': 'NONE',
            'Attributes': {
                'OptInTimestamp': [timestamp]
            }
        }
    )

    return update_endpoint_response['MessageBody']

def lambda_handler(event, context):
    logger.debug('## ENVIRONMENT VARIABLES')
    logger.debug(os.environ)
    logger.debug('## EVENT')
    logger.debug(event)

    pinpoint_app_id = os.environ['pinpoint_app_id']

    timestamp =  event['Records'][0]['Sns']['Timestamp']
    message = json.loads(event['Records'][0]['Sns']['Message'])
    originationNumber = message['originationNumber']
    response = message['messageBody'].lower()
    endpointId = originationNumber[1:]

    # opt in the customer to receive text alerts if they responded with 'y' to the confirmation SMS
    if 'y' == response:
        logger.info('Updating SMS endpoint for user.')
        response = updateEndpointOptIn(originationNumber, timestamp, pinpoint_app_id)
        print(response)
        # get endpoint info
        endpoint_response = pinpoint.get_endpoint(
            ApplicationId = pinpoint_app_id,
            EndpointId = endpointId
        )
        endpoint_info = endpoint_response['EndpointResponse']
        # record an event to trigger the SMS campaign
        event_response = pinpoint.put_events(
            ApplicationId = pinpoint_app_id,
            EventsRequest = {
                'BatchItem': {
                    endpointId : {
                        'Endpoint': {
                            'Address': originationNumber[1:],
                            'Attributes': endpoint_info['Attributes'],
                            'ChannelType': 'SMS',
                            'Demographic': endpoint_info['Demographic'],
                            'EffectiveDate': endpoint_info['EffectiveDate'],
                            'EndpointStatus': endpoint_info['EndpointStatus'],
                            'Location': endpoint_info['Location'],
                            'OptOut': endpoint_info['OptOut'],
                            'RequestId': endpoint_info['RequestId'],
                            'User': endpoint_info['User']
                        },
                        'Events': {
                            'smsevent':{
                                'EventType': 'UserVerifiedSMS',
                                'Timestamp': timestamp
                            }
                        }
                    }
                }
            }
        )
        logger.info('event recorded')
        print(event_response)
