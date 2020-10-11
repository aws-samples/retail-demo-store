# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
import boto3
import os
import requests  # Needed for Segment Events REST APIs
import dateutil.parser as dp
import logging

from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

connections_endpoint_url = "https://api.segment.io/v1"
connections_source_api_key = os.environ['connections_source_write_key']

def api_post(url, key, payload):
    myResponse = requests.post(url,auth=(key, ''), json=payload)
    if(myResponse.ok):
        jData = json.loads(myResponse.content)
        return jData
    else:
        myResponse.raise_for_status()

def set_user_traits(user_id, traits):
    # Sends an identify call to Personas to update a user's traits
    formatted_url = "{:s}/identify".format(connections_endpoint_url)
    message = { "traits": traits, "userId": user_id, "type": "identify" }
    try:
        response = api_post(formatted_url, connections_source_api_key, message)
    except HTTPError as error:
        status = error.response.status_code
        if status >= 400 and status < 500:
            logger.error('Segment: 400 error, more than likely you sent an invalid request.')
        elif status >= 500:
            logger.error('Segment: There was a server error on the Segment side.')

def lambda_handler(event, context):
    if not 'personalize_tracking_id' in os.environ:
        raise Exception('personalize_tracking_id not configured as environment variable')
    if not 'personalize_campaign_arn' in os.environ:
        raise Exception('personalize_campaign_arn not configured as environment variable')

    logger.info("Segment Event: " + json.dumps(event))  # Remove this if using in production.

    # Allow Personalize region to be overriden via environment variable. Optional.
    runtime_params = { 'service_name': 'personalize-runtime' }
    if 'region_name' in os.environ:
        runtime_params['region_name'] = os.environ['region_name']

    personalize_runtime = boto3.client(**runtime_params)
    personalize_events = boto3.client(service_name='personalize-events')

    # Segment will invoke your function once per event type you have configured
    # in the Personalize destination in Segment.

    try:
        if ('anonymousId' in event and
            'properties' in event and
            'sku' in event['properties']):

            logger.info("Calling Personalize.PutEvents()")

            # Function parameters for put_events call.
            params = {
                'trackingId': os.environ['personalize_tracking_id'],
                'sessionId': event['anonymousId']
            }

            # If a user is signed in, we'll get a userId. Otherwise for anonymous 
            # sessions, we will not have a userId. We still want to call put_events
            # in both cases. Once the user identifies themsevles for the session, 
            # subsequent events will have the userId for the same session and 
            # Personalize will be able to connect prior anonymous to that user.
            if event.get('userId'):
                params['userId'] = event['userId']

            # You will want to modify this part to match the event props
            # that come from your events - Personalize needs the event identifier
            # that was used to train the model. In this case, we're using the 
            # product's SKU passed through Segment to represent the eventId.
            properties = { 'itemId': event['properties']['sku'] }

            # Build the event that we're sending to Personalize.  Note that Personalize
            #  expects a specific event format
            personalize_event = {
                'eventId': event['messageId'],
                'sentAt': int(dp.parse(event['timestamp']).strftime('%s')),
                'eventType': event['event'],
                'properties': json.dumps(properties)
            }

            params['eventList'] = [ personalize_event ]

            logger.debug('put_events parameters: {}'.format(json.dumps(params, indent = 2)))
            # Call put_events
            response = personalize_events.put_events(**params)

"""             if event.get('userId'):
                logger.info("Updating recommendations on user profile in Segment Personas")

                # Get recommendations for the user.
                params = { 'campaignArn': os.environ['personalize_campaign_arn'], 'userId': event.get('userId') }

                response = personalize_runtime.get_recommendations(**params)

                recommended_items = [d['itemId'] for d in response['itemList'] if 'itemId' in d]

                logger.info(recommended_items)

                # Set the updated recommendations on the user's profile - note that
                # this user trait can be anything you want
                set_user_traits(event.get('userId'), { 'recommended_products' : recommended_items })
            else:
                logger.info('Event from Segment is for anonymous user so skipping setting recommendations on profile')
 """
        else:
            logger.warn("Segment event does not contain required fields (anonymousId and sku)")
    except ValueError as ve:
        logger.error("Invalid JSON format received, check your event sources.")
    except KeyError as ke:
        logger.error("Invalid configuration for Personalize, most likely.")
    except ClientError as ce:
        logger.error("ClientError - most likely a boto3 issue.")
        logger.error(ce.response['Error']['Code'])
        logger.error(ce.response['Error']['Message'])