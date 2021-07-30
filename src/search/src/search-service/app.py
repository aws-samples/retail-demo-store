# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.ext.flask.middleware import XRayMiddleware
from aws_xray_sdk.core import patch_all

patch_all()

from flask import Flask, jsonify, Response
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

app = Flask(__name__)
corps = CORS(app)

xray_recorder.configure(service='Search Service')
XRayMiddleware(app, xray_recorder)

# -- Exceptions
class BadRequest(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

# -- Utilities
def get_offset_and_size(request):
    offset = request.args.get('offset', default = 0, type = int)
    if offset < 0:
        raise BadRequest('offset must be greater than or equal to zero')
    size = request.args.get('size', default = 10, type = int)
    if size < 1:
        raise BadRequest('size must be greater than zero')

    return offset, size

# -- Handlers

@app.errorhandler(BadRequest)
def handle_bad_request(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

@app.route('/')
def index():
    return 'Search Service'

@app.route('/search/products', methods=['GET'])
def searchProducts():
    search_term = request.args.get('searchTerm')
    if not search_term:
        raise BadRequest('searchTerm is required')
    search_term = search_term.lower()

    offset, size = get_offset_and_size(request)
    app.logger.info(f'Searching products for "{search_term}" starting at {offset} and returning {size} hits')

    try:
        results = es.search(index = es_products_index_name, body={
            "from": offset,
            "size": size,
            "query": {
                "dis_max" : {
                    "queries" : [
                        { "wildcard" : { "name" : { "value": '{}*'.format(search_term), "boost": 1.2 }}},
                        { "term" : { "category" : search_term }},
                        { "term" : { "style" : search_term }},
                        { "wildcard" : { "description" : { "value": '{}*'.format(search_term), "boost": 0.6 }}}
                    ],
                    "tie_breaker" : 0.7
                }
            }
        })

        app.logger.debug(json.dumps(results))

        found_items = []

        for item in results['hits']['hits']:
            found_items.append({
                'itemId': item['_id']
            })
        return json.dumps(found_items)

    except Exception as e:
        app.logger.exception('Unexpected error performing product search', e)
        raise BadRequest(message = 'Unhandled error', status_code = 500)

@app.route('/similar/products', methods=['GET'])
def similarProducts():
    product_id = request.args.get('productId')
    if not product_id:
        raise BadRequest('productId is required')
    offset, size = get_offset_and_size(request)
    app.logger.info(f'Searching for similar products to "{product_id}" starting at {offset} and returning {size} hits')

    try:
        results = es.search(index = es_products_index_name, body={
            "from": offset,
            "size": size,
                "query": {
                    "more_like_this": {
                        "fields": ["name", "category", "style", "description"],
                        "like": [{
                            "_index": es_products_index_name,
                            "_id": product_id
                        }],
                        "min_term_freq" : 1,
                        "max_query_terms" : 10
                    }
                }
            })

        app.logger.debug(json.dumps(results))

        found_items = []

        for item in results['hits']['hits']:
            found_items.append({
                'itemId': item['_id']
            })
        return json.dumps(found_items)

    except Exception as e:
        app.logger.exception('Unexpected error performing similar product search', e)
        raise BadRequest(message = 'Unhandled error', status_code = 500)

if __name__ == '__main__':
    app.wsgi_app = LoggingMiddleware(app.wsgi_app)
    app.run(debug=True,host='0.0.0.0', port=80)