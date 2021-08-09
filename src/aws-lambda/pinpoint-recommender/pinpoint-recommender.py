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

def lambda_handler(event, context):
    ''' Called by Amazon Pinpoint recommender to customize/enrich recommendations

    The Pinpoint recommender (aka machine learning model in Pinpoint UI) will call 
    the specified Amazon Personalize campaign to get product recommendations. Since 
    the recommendations from Personalize only include item IDs, Pinpoint calls this 
    function to associate more rich/useful metadata on each item. This function 
    uses the Retail Demo Store's Product service to retrieve details on each recommended
    item/product.
    ''' 

    logger.debug(event)
    
    products_service_host = os.environ.get('products_service_host')
    if not products_service_host:
        raise ValueError("Missing required environment value for 'products_service_host'")

    logger.debug('Products service host: ' + products_service_host)
    
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

            recommended_items = endpoint.get('RecommendationItems')
            
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
                
                for idx, item_id in enumerate(recommended_items):
                    logger.debug('Looking up product information for product ' + item_id)
                    
                    url = f'http://{products_service_host}/products/id/{item_id}?fullyQualifyImageUrls=1'
                    response = requests.get(url)
                    
                    if response.ok:
                        product = response.json()
                        logger.debug(product)
                        
                        recommendations['Name'][idx] = product['name']
                        recommendations['URL'][idx] = product['url']
                        recommendations['Category'][idx] = product['category']
                        recommendations['Style'][idx] = product['style']
                        recommendations['Description'][idx] = product['description']
                        recommendations['Price'][idx] = '$ {}'.format(product['price'])
                        recommendations['ImageURL'][idx] = product['image']
                    else:
                        logger.error(response)
                        
                endpoint['Recommendations'] = recommendations
                new_endpoints[key] = endpoint
            else:
                logger.error('Endpoint {} does not have any RecommendationItems'.format(key))
    else:
        logger.error('Event is missing Endpoints document')

    logger.debug("Returning endpoints: " + json.dumps(new_endpoints))
    return new_endpoints
