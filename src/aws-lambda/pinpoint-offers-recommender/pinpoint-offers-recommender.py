# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import os
import json
import logging

import boto3
import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)

pinpoint = boto3.client('pinpoint')


def get_offer_by_id(offer_id):
    offers_service_host, offers_service_port = os.environ.get('offers_service_host'), 80
    url = f'http://{offers_service_host}:{offers_service_port}/offers/{offer_id}'
    logger.debug(f"Asking for offer info from {url}")
    offers_response = requests.get(url)  # we let connection error propagate
    logger.debug(f"Got offer info: {offers_response}")
    if not offers_response.ok:
        logger.error(f"Offers service not giving us offers: {offers_response.reason}")
        return None
    offer = offers_response.json()['task']
    return offer


def lambda_handler(event, context):
    ''' Called by Amazon Pinpoint recommender to customize/enrich recommendations

    The Pinpoint recommender (aka machine learning model in Pinpoint UI) will call
    the specified Amazon Personalize campaign to get offer recommendations. Since
    the recommendations from Personalize only include offer IDs, Pinpoint calls this
    function to associate more rich/useful metadata on each item using the offers service.
    '''

    logger.info('ENVIRONMENT VARIABLES')
    logger.info(os.environ)
    logger.info('EVENT')
    logger.info(event)

    new_endpoints = dict()

    endpoints = event.get('Endpoints')
    if endpoints:
        logger.info('endpoints')
        for key in endpoints:
            logger.debug('Processing Pinpoint endpoint: ' + key)

            endpoint = endpoints.get(key)
            logger.info(f"Processing endpoint: {json.dumps(endpoint, indent=2)}")

            # A workaround: - if the address is not visible here it also does not find its way to Pinpoint to
            # allow sending.
            if 'Address' not in endpoint:
                logger.warning("Address not in endpoint supplied - so we must fill it in ourselves.")
                pinpoint_app_id = event['ApplicationId']
                full_endpoint = pinpoint.get_endpoint(ApplicationId=pinpoint_app_id,
                                                      EndpointId=key)
                endpoint['Address'] = full_endpoint['EndpointResponse']['Address']

            recommended_items = endpoint.get('RecommendationItems')

            if recommended_items:
                recommendations = {
                    'OfferCode': [''] * len(recommended_items),
                    'OfferDescription': [''] * len(recommended_items)
                }
                for idx, item_id in enumerate(recommended_items):
                    logger.debug('Looking up product information for item ' + item_id)
                    offer = get_offer_by_id(item_id)
                    if offer is not None:

                        logger.info(f"Got offer: {offer}")
                        recommendations['OfferCode'][idx] = offer['codes'][0]
                        recommendations['OfferDescription'][idx] = offer['description']

                    else:

                        recommendations['OfferCode'][idx] = 'UNKNOWNID'+item_id
                        recommendations['OfferDescription'][idx] = f'Unknown code with id {item_id}'
            else:
                logger.error('Endpoint {} does not have any RecommendationItems'.format(key))
                recommendations = {}

            endpoint['Recommendations'] = recommendations
            new_endpoints[key] = endpoint

    else:
        logger.error('Event is missing Endpoints document')

    logger.info("Returning endpoints: " + json.dumps(new_endpoints, indent=2))
    return new_endpoints
