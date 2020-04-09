# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from flask import Flask
from flask import request
from flask_cors import CORS
from datetime import datetime
from elasticsearch import Elasticsearch

import json
import uuid
import os, sys
import pprint
import boto3
import time
import uuid

es_search_domain_scheme = os.environ.get('ES_SEARCH_DOMAIN_SCHEME', 'https')
es_search_domain_host = os.environ['ES_SEARCH_DOMAIN_HOST']
es_search_domain_port = os.environ.get('ES_SEARCH_DOMAIN_PORT', 443)
es_products_index_name = 'products'

es = Elasticsearch(
    [es_search_domain_host],
    scheme=es_search_domain_scheme,
    port=es_search_domain_port,
)

# -- Logging
class LoggingMiddleware(object):
    def __init__(self, app):
        self._app = app

    def __call__(self, environ, resp):
        errorlog = environ['wsgi.errors']
        pprint.pprint(('REQUEST', environ), stream=errorlog)

        def log_response(status, headers, *args):
            pprint.pprint(('RESPONSE', status, headers), stream=errorlog)
            return resp(status, headers, *args)

        return self._app(environ, log_response)

# -- End Logging

# -- Handlers

app = Flask(__name__)
corps = CORS(app)

@app.route('/')
def index():
    return 'Search Service' 

@app.route('/search/products', methods=['GET', 'POST'])
def searchProducts():
    if request.method == 'GET':

        try:
            searchTerm = request.args.get('searchTerm').lower()

            app.logger.info(searchTerm)

            results = es.search(index = es_products_index_name, body={
                "query": {
                    "dis_max" : {
                        "queries" : [
                            { "wildcard" : { "name" : { "value": '{}*'.format(searchTerm), "boost": 1.2 }}},
                            { "term" : { "category" : searchTerm }},
                            { "term" : { "style" : searchTerm }},
                            { "wildcard" : { "description" : { "value": '{}*'.format(searchTerm), "boost": 0.6 }}}
                        ],
                        "tie_breaker" : 0.7
                    }
                }
            })

            app.logger.info(json.dumps(results))

            found_items = []

            for item in results['hits']['hits']:
                found_items.append({
                    'itemId': item['_id']
                })
            return json.dumps(found_items)

        except Exception as e:
            app.logger.error(e)
            return str(e)

    if request.method == 'POST':
        app.logger.info("Request Received, Processing")

@app.route('/similar/products', methods=['GET'])
def similarProducts():
    try:
        productId = request.args.get('productId')

        app.logger.info(productId)

        results = es.search(index = es_products_index_name, 
                            body={
                                "query": {
                                    "more_like_this": {
                                        "fields": ["name", "category", "style", "description"],
                                        "like": [{
                                            "_index": es_products_index_name,
                                            "_id": productId
                                        }],
                                        "min_term_freq" : 1,
                                        "max_query_terms" : 10
                                    }
                                }
                            })

        app.logger.info(json.dumps(results))

        found_items = []

        for item in results['hits']['hits']:
            found_items.append({
                'itemId': item['_id']
            })
        return json.dumps(found_items)

    except Exception as e:
        app.logger.error(e)
        return str(e)

if __name__ == '__main__':
    app.wsgi_app = LoggingMiddleware(app.wsgi_app)
    app.run(debug=True,host='0.0.0.0', port=80)