# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

# Utility script for local development that indexes products in a local 
# Elasticsearch instance. Typically you would be running Elasticsearch 
# in a local Docker container for development. See the docker-compose.yml
# file for details.

# When deploying to AWS, products are either indexed by a Lambda function 
# (custom resource) or using the Search workshop notebook.

import json
import os
import sys
import requests
import yaml
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

INDEX_NAME = 'products'

# Defaults assume you're running Elasticsearch locally on port 9200
es_search_domain_scheme = os.environ.get('ES_SEARCH_DOMAIN_SCHEME', 'http')
es_search_domain_host = os.environ.get('ES_SEARCH_DOMAIN_HOST', 'localhost')
es_search_domain_port = os.environ.get('ES_SEARCH_DOMAIN_PORT', 9200)

logger.info('Elasticsearch scheme: ' + es_search_domain_scheme)
logger.info('Elasticsearch endpoint: ' + es_search_domain_host)
logger.info('Elasticsearch port: ' + str(es_search_domain_port))
    
url = '{}://{}:{}/{}'.format(es_search_domain_scheme, es_search_domain_host, es_search_domain_port, INDEX_NAME)

headers = { "Content-Type": "application/json" }

r = requests.get(url, headers = headers)

# If index exists, delete it so we freshly index products.
if r.ok:
    logger.info('Deleting index ' + INDEX_NAME)
    requests.delete(url)
    r = requests.get(url, headers = headers)

if r.ok:
    logger.info('Index exists! Nothing to do.')
else:
    logger.info('Index does NOT exist!')

    request_body = {
        "settings" : {
            "number_of_shards": 1,
            "number_of_replicas": 0
        }
    }
    logger.info("Creating '{}' index...".format(INDEX_NAME))

    r = requests.put(url, headers = headers, json = request_body)
    logger.info('Indexing products...')
    products_indexed = 0
    with open('../products/src/products-service/data/products.yaml') as file:
        products_list = yaml.load(file, Loader=yaml.FullLoader)

        for product in products_list:
            url = '{}://{}:{}/{}/_doc/{}'.format(es_search_domain_scheme, es_search_domain_host, es_search_domain_port, INDEX_NAME, product['id'])
            r = requests.put(url, headers = headers, json = product)
            products_indexed += 1

    logger.info('{} products successfully indexed!'.format(products_indexed))
