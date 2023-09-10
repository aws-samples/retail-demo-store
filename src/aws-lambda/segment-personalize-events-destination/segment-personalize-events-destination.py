# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
#
# segment-personalize-events-destination.py
#  
# This lambda contains sample code for sending real-time event data from Segment to Amazon Personalize
# for creating real-time event datasets.  This destination does not support inference.
#

import json
import boto3
import os
import dateutil.parser as dp
import logging
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize the Amazon Personalize events boto object
personalize_events = boto3.client('personalize-events')

if 'personalize_tracking_id' not in os.environ or os.environ['personalize_tracking_id'] == '':
    logger.error("Missing personalize_tracking_id environment variable in lambda configuration.")
    raise Exception('personalize_tracking_id not configured as environment variable')
else:
    personalize_tracking_id = os.environ['personalize_tracking_id'] 

def lambda_handler(event, context):    
    # In high volume applications, remove this code.
    logger.debug("Got event: " + json.dumps(event))

    # Segment will invoke your function once per event type you have configured
    # in the Personalize destination in Segment.
    try:
        if ('anonymousId' in event or 'userId' in event and 'properties' in event):
            # Make sure this event contains an itemId since this is required for the Retail Demo Store
            # dataset - you can also check for specific event names here if needed, and only pass the ones
            # that you want to use in the training dataset
            if ('productId' not in event['properties']):
                logger.debug("Got event with no productId, discarding.")
                return

            logger.debug("Calling putEvents()")
            # Function parameters for put_events call.
            params = {
                'trackingId': personalize_tracking_id,
                'sessionId': event['anonymousId']
            }

            # If a user is signed in, we'll get a userId. Otherwise for anonymous 
            # sessions, we will not have a userId. We still want to call put_events
            # in both cases. Once the user identifies themsevles for the session, 
            # subsequent events will have the userId for the same session and 
            # Personalize will be able to connect prior anonymous to that user.
            if event.get('userId'):
                params['userId'] = event['userId']

            # YOU WILL NEED TO MODIFY THIS PART TO MATCH THE EVENT PROPS
            # THAT COME FROM YOUR EVENTS
            # 
            # Personalize needs the event identifier
            # that was used to train the model. In this case, we're using the 
            # product's productId passed through Segment to represent the itemId.
            #
            properties = { 'itemId': event['properties']['productId'] }

            # Build the event that we're sending to Personalize.  Note that Personalize
            # expects a specific event format
            personalize_event = {
                'eventId': event['messageId'],
                'sentAt': int(dp.parse(event['timestamp']).strftime('%s')),
                'eventType': event['event'],
                'properties': json.dumps(properties)
            }

            params['eventList'] = [ personalize_event ]

            logger.debug('put_events parameters: {}'.format(json.dumps(params, indent = 2)))
            # Call put_events
            personalize_events.put_events(**params)
        else:
            logger.debug("Segment event does not contain required fields (anonymousId and sku)")
    except ValueError:
        logger.error("Invalid JSON format received, check your event sources.")
    except KeyError:
        logger.error("Invalid configuration for Personalize, most likely.")
    except ClientError as ce:
        logger.error("ClientError: ")
        logger.error(ce.response['Error']['Code'])
        logger.error(ce.response['Error']['Message'])
