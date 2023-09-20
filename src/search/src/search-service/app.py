# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.ext.flask.middleware import XRayMiddleware
from aws_xray_sdk.core import patch_all

from flask import Flask, jsonify
from flask import request
from flask_cors import CORS
from opensearchpy import OpenSearch, NotFoundError

import json
import os
import pprint

patch_all()


INDEX_DOES_NOT_EXIST = 'index_not_found_exception'

search_domain_scheme = os.environ.get('OPENSEARCH_DOMAIN_SCHEME', 'https')
search_domain_host = os.environ['OPENSEARCH_DOMAIN_HOST']
search_domain_port = os.environ.get('OPENSEARCH_DOMAIN_PORT', 443)
INDEX_PRODUCTS = 'products'

search_client = OpenSearch(
    [search_domain_host],
    scheme=search_domain_scheme,
    port=search_domain_port,
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
def search_products():
    search_term = request.args.get('searchTerm')
    if not search_term:
        raise BadRequest('searchTerm is required')
    search_term = search_term.lower()

    offset, size = get_offset_and_size(request)
    collapse_size = int(max(size / 15, 15))
    app.logger.info('Searching products for "%s" starting at %d and returning %d hits with collapse size of %d',
        search_term, offset, size, collapse_size
    )

    try:
        # Query OpenSearch using a disjunction max query across multiple fields using the "match_bool_prefix".
        # The "match_bool_prefix" query will tokenize the search expression where the last token is turned into
        # a prefix query. This is good match for an "auto-complete" search UX.
        # To improve the diversity of hits across categories (particularly important when the search expression is
        # short/vague), the search is collapsed on the category keyword field. This ensures that the top hits are pulled
        # from all categories which are then aggregated into a unified response.
        results = search_client.search(index = INDEX_PRODUCTS, body={
            "from": offset,
            "size": size,
            "query": {
                "dis_max" : {
                    "queries" : [
                        { "match_bool_prefix" : { "name" : { "query": search_term, "boost": 1.2 }}},
                        { "match_bool_prefix" : { "category" : search_term }},
                        { "match_bool_prefix" : { "style" : search_term }},
                        { "match_bool_prefix" : { "description" : { "query": search_term, "boost": 0.6 }}}
                    ],
                    "tie_breaker" : 0.7
                }
            },
            "fields":[
                "_id"
            ],
            "_source": False,
            "collapse": {
                "field": "category.keyword",
                "inner_hits": {
                    "name": "category_hits",
                    "size": collapse_size,
                    "fields":[
                        "_id"
                    ],
                    "_source": False
                }
            }
        })

        app.logger.debug(json.dumps(results))

        # Because we're collapsing results across categories, the total hits will likely be > size.
        total_hits = results["hits"]["total"]["value"]
        app.logger.debug('Total hits across categories: %d', total_hits)

        cats_with_hits = len(results["hits"]["hits"])
        avg_hits_cat = int(size / cats_with_hits) if cats_with_hits > 0 else 0
        app.logger.debug('Average hits per category: %d', avg_hits_cat)
        hits_for_cats = []
        accum_hits = 0
        cats_with_more = 0

        # Determine the number of hits per category that we can use.
        for item in results['hits']['hits']:
            cat_hits = item["inner_hits"]["category_hits"]["hits"]["total"]["value"]
            if cat_hits > avg_hits_cat:
                cats_with_more += 1
            hits_this_cat = min(cat_hits, avg_hits_cat)
            accum_hits += hits_this_cat
            hits_for_cats.append([cat_hits, hits_this_cat])

        if accum_hits < size and cats_with_more:
            # Still more room available. Add more items across categories that have more than average.
            more_each = int((size - accum_hits) / cats_with_more)
            for counts in hits_for_cats:
                more_this_cat = min(more_each, counts[0] - counts[1])
                accum_hits += more_this_cat
                counts[1] += more_this_cat

        found_items = []

        for idx, item in enumerate(results['hits']['hits']):
            cat_hits = item["inner_hits"]["category_hits"]["hits"]["hits"]

            if accum_hits < size and hits_for_cats[idx][1] < hits_for_cats[idx][0]:
                # If still more room available, use first one with more to give.
                to_add = min(size - accum_hits, hits_for_cats[idx][0] - hits_for_cats[idx][1])
                hits_for_cats[idx][1] += to_add
                accum_hits += to_add

            added = 0
            for hit in cat_hits:
                found_items.append({
                    'itemId': hit['_id']
                })
                added += 1
                if added == hits_for_cats[idx][1]:
                    break

        return json.dumps(found_items)

    except NotFoundError as e:
        if e.error == INDEX_DOES_NOT_EXIST:
            app.logger.error('Search index does not exist')
            raise BadRequest(message = 'Index does not exist yet; please complete search workshop', status_code = 404)
        raise BadRequest(message = 'Not Found', status_code = 404)

    except Exception as e:
        app.logger.exception('Unexpected error performing product search', e)
        raise BadRequest(message = 'Unhandled error', status_code = 500)

@app.route('/similar/products', methods=['GET'])
def similar_products():
    product_id = request.args.get('productId')
    if not product_id:
        raise BadRequest('productId is required')
    offset, size = get_offset_and_size(request)
    app.logger.info(f'Searching for similar products to "{product_id}" starting at {offset} and returning {size} hits')

    try:
        results = search_client.search(index = INDEX_PRODUCTS, body={
            "from": offset,
            "size": size,
                "query": {
                    "more_like_this": {
                        "fields": ["name", "category", "style", "description"],
                        "like": [{
                            "_index": INDEX_PRODUCTS,
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

    except NotFoundError as e:
        if e.error == INDEX_DOES_NOT_EXIST:
            app.logger.error('Search index does not exist')
            raise BadRequest(message = 'Index does not exist yet; please complete search workshop', status_code = 404)
        raise BadRequest(message = 'Not Found', status_code = 404)

    except Exception as e:
        app.logger.exception('Unexpected error performing similar product search', e)
        raise BadRequest(message = 'Unhandled error', status_code = 500)

if __name__ == '__main__':
    app.wsgi_app = LoggingMiddleware(app.wsgi_app)
    app.run(debug=True,host='0.0.0.0', port=80)