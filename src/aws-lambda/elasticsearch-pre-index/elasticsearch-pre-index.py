# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
import os
import requests
import yaml
import logging
import boto3
from crhelper import CfnResource

logger = logging.getLogger()
logger.setLevel(logging.INFO)
# Initialise the helper, all inputs are optional, this example shows the defaults
helper = CfnResource()

s3 = boto3.resource('s3')

INDEX_NAME = 'products'

@helper.delete
@helper.update
def no_op(_, __):
    # no operation is needed, the elasticsearch domain is just deleted with the resources
    pass

@helper.create
def elasticsearch_create(event,_):
    # Conditionally creates and loads Elasticsearch products index
    # If the products index already exists, this function does nothing.
    # Otherwise, this function will create the products index and add
    # all products from the bundled products.yaml file.

    es_domain_endpoint = event['ResourceProperties']['ElasticsearchDomainEndpoint']
    logger.info('Elasticsearch endpoint: ' + es_domain_endpoint)
    
    url = 'https://{}/{}'.format(es_domain_endpoint, INDEX_NAME)
    
    headers = { "Content-Type": "application/json" }

    r = requests.get(url, headers = headers)

    # For testing: if index exists, tear it down so create/load logic kicks in
    #if r.ok:
    #    logger.info('Deleting index ' + INDEX_NAME)
    #    requests.delete(url)
    #    r = requests.get(url, headers = headers)

    if r.ok:
        logger.info('Index exists! Nothing to do.')
        return es_domain_endpoint
    else:
        logger.info('Index does NOT exist!')

        request_body = {
            "settings" : {
                "number_of_shards": 1,
                "number_of_replicas": 0
            }
        }
        logger.info("Creating '{}' index...".format(INDEX_NAME))

        try:
            r = requests.put(url, headers = headers, json = request_body)
        except Exception as e:
            helper.init_failure(e)
            return False

        logger.info('Indexing products...')
        s3.meta.client.download_file(event['ResourceProperties']['Bucket'], event['ResourceProperties']['File'], '/tmp/products.yaml')
        with open('/tmp/products.yaml') as file:
            products_list = yaml.load(file, Loader=yaml.FullLoader)

            for product in products_list:
                url = 'https://{}/{}/_doc/{}'.format(es_domain_endpoint, INDEX_NAME, product['id'])
                r = requests.put(url, headers = headers, json = product)

        logger.info('Products successfully indexed!')

    helper.Data['Output'] = 'Elasticsearch product index populated'
    return es_domain_endpoint

def lambda_handler(event, context):
    helper(event, context)
