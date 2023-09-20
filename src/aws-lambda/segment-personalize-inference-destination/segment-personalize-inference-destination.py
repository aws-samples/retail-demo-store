# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
#
# segment-personalize-inference-destination.py
#
# This lambda contains sample code that allows you to use Segment real-time events to perform inference
# against an Amazon Personalize Campaign.  This lambda is not suitable for training events.
#

import json
import os
import logging
import analytics  # Segment Python library
import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Check that the Segment env variables are set correctly
if 'segment_personas_write_key' not in os.environ or os.environ['segment_personas_write_key'] == '':
    raise Exception('segment_personas_write_key is null or not defined.')
else:
    analytics.write_key = os.environ['segment_personas_write_key']

if 'recommendations_service_url' not in os.environ or os.environ['recommendations_service_url'] == '':
    raise Exception('recommendations_service_url not configured as environment variable')
else:
    recommendations_service_url = os.environ['recommendations_service_url']

def lambda_handler(event, context):
    logger.debug("Segment event: " + json.dumps(event))  # Remove this if using in production.

    # Segment will invoke your function once per event type you have configured
    # in the Personalize destination in Segment.

    try:
        if ('userId' in event and event['name'] == 'Purchase'):
            user_id = event['userId']
            logger.debug('Looking up product recommendations for user ' + user_id)
            url = f'{recommendations_service_url}/recommendations?userID={user_id}&fullyQualifyImageUrls=1&numResults=4'
            response = requests.get(url)
            recommendations = None
            if response.ok:
                recommendations = response.json()
                logger.debug(recommendations)
                # Send the user recommendations to Segment
                analytics.identify(user_id, { 'personalized_recommendations': recommendations })
    except ValueError:
        logger.error("Invalid JSON format received, check your event sources.")
    except KeyError:
        logger.error("Invalid configuration for Personalize, most likely.")
