# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import os
import json
import logging
import requests
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

pinpoint = boto3.client('pinpoint')
personalize_runtime = boto3.client('personalize-runtime')

def lambda_handler(event, context):
    ''' Called by Amazon Pinpoint campaign to retrieve recommendations from
    the Recommendations service

    This function 
    uses the Retail Demo Store's Recommendations service to retrieve recommendations for each endpoint.
    ''' 

    logger.debug(event)

    recommendations_service_host = os.environ.get('recommendations_service_host')
    if not recommendations_service_host:
        raise ValueError("Missing required environment value for 'recommendations_service_host'")
    
    logger.debug('Recommendations service host: ' + recommendations_service_host)
    
    new_endpoints = dict()

    endpoints = event.get('Endpoints')
    if endpoints:
        for key in endpoints:
            logger.debug('Processing Pinpoint endpoint: ' + key)
            
            endpoint = endpoints.get(key)

            # A workaround: - if the address is not visible here it also does not find its way to Pinpoint
            # allow sending.
            if 'Address' not in endpoint:
                logger.warning("Address not in endpoint supplied - so we must fill it in ourselves.")
                pinpoint_app_id = event['ApplicationId']
                full_endpoint = pinpoint.get_endpoint(ApplicationId=pinpoint_app_id,
                                                      EndpointId=key)
                endpoint['Address'] = full_endpoint['EndpointResponse']['Address']

            user_id = endpoint['User']['UserId']
            recommendations_request = f'http://{recommendations_service_host}/recommendations?userID={user_id}&numResults=4&fullyQualifyImageUrls=1'
            response = requests.get(recommendations_request)

            if response.ok:
                recommended_items = response.json()
                logger.debug(recommended_items)

                if recommended_items:
                    recommendations = {
                        'Name': [''] * len(recommended_items),
                        'URL': [''] * len(recommended_items),
                        'Category': [''] * len(recommended_items),
                        'Style': [''] * len(recommended_items),
                        'Description': [''] * len(recommended_items),
                        'Price': [''] * len(recommended_items),
                        'ImageURL': [''] * len(recommended_items)
                    }

                    for idx, item in enumerate(recommended_items):
                        product = recommended_items[idx]['product']
                        recommendations['Name'][idx] = product['name']
                        recommendations['URL'][idx] = product['url']
                        recommendations['Category'][idx] = product['category']
                        recommendations['Style'][idx] = product['style']
                        recommendations['Description'][idx] = product['description']
                        recommendations['Price'][idx] = '$ {}'.format(product['price'])
                        recommendations['ImageURL'][idx] = product['image']

                    endpoint['Recommendations'] = recommendations
                    new_endpoints[key] = endpoint
                else:
                    logger.error('Endpoint {} does not have any Recommendations'.format(key))
            else:
                logger.error(response)                                      
    else:
        logger.error('Event is missing Endpoints document')

    logger.debug("Returning endpoints: " + json.dumps(new_endpoints))
    return new_endpoints
