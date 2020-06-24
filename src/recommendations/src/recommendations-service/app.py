# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from flask import Flask, jsonify, Response
from flask import request
from flask_cors import CORS
from experimentation.experiment_manager import ExperimentManager
from experimentation.resolvers import DefaultProductResolver, PersonalizeRecommendationsResolver, PersonalizeRankingResolver, RankingProductsNoOpResolver
from experimentation.utils import CompatEncoder

import json
import os, sys
import pprint
import boto3
import logging
import requests

servicediscovery = boto3.client('servicediscovery')
personalize = boto3.client('personalize')
ssm = boto3.client('ssm')

# SSM parameter name for the Personalize filter for purchased items
filter_purchased_param_name = 'retaildemostore-personalize-filter-purchased-arn'

# -- Shared Functions

def get_recipe(campaign_arn):
    """ Returns the Amazon Personalize recipe ARN for the specified campaign ARN """
    recipe = None
    response = personalize.describe_campaign(campaignArn = campaign_arn)

    if response.get('campaign'):
        response = personalize.describe_solution_version(solutionVersionArn = response['campaign']['solutionVersionArn'])
        if response.get('solutionVersion'):
            recipe = response['solutionVersion']['recipeArn']

    return recipe

def get_parameter_values(names):
    """ Returns values for SSM parameters or None for params that don't exist or that have value equal 'NONE' """
    if isinstance(names, str):
        names = [ names ]

    response = ssm.get_parameters(Names = names)

    values = []

    for name in names:
        found = False
        for param in response['Parameters']:
            if param['Name'] == name:
                found = True
                if param['Value'] != 'NONE':
                    values.append(param['Value'])
                else:
                    values.append(None)
                break

        if not found:
            values.append(None)

    assert len(values) == len(names), 'mismatch in number of values returned for names'

    return values

def get_products(feature, user_id, current_item_id, num_results, campaign_arn_param_name, user_reqd_for_campaign = False, fully_qualify_image_urls = False):
    """ Returns products given a UI feature, user, item/product.

    If a feature name is provided and there is an active experiment for the 
    feature, the experiment will be used to retrieve products. Otherwise, 
    the default behavior will be used which will look to see if an Amazon Personalize 
    campaign is available. If not, the Product service will be called to get products 
    from the same category as the current product.
    """

    # Check environment for host and port first in case we're running in a local Docker container (dev mode)
    products_service_host = os.environ.get('PRODUCT_SERVICE_HOST')
    products_service_port = os.environ.get('PRODUCT_SERVICE_PORT', 80)

    if not products_service_host:
        # Get product service instance. We'll need it rehydrate product info for recommendations.
        response = servicediscovery.discover_instances(
            NamespaceName='retaildemostore.local',
            ServiceName='products',
            MaxResults=1,
            HealthStatus='HEALTHY'
        )

        products_service_host = response['Instances'][0]['Attributes']['AWS_INSTANCE_IPV4']

    items = []
    resp_headers = {}
    experiment = None

    # Get active experiment if one is setup for feature and we have a user.
    if feature and user_id:
        exp_manager = ExperimentManager()
        experiment = exp_manager.get_active(feature)

    if experiment:
        # Get items from experiment.
        tracker = exp_manager.default_tracker()

        items = experiment.get_items(
            user_id = user_id, 
            current_item_id = current_item_id, 
            num_results = num_results,
            tracker = tracker
        )

        resp_headers['X-Experiment-Name'] = experiment.name
        resp_headers['X-Experiment-Type'] = experiment.type
        resp_headers['X-Experiment-Id'] = experiment.id
    else:
        # Fallback to default behavior of checking for campaign ARN parameter and 
        # then the default product resolver.
        values = get_parameter_values([ campaign_arn_param_name, filter_purchased_param_name ])

        campaign_arn = values[0]
        filter_arn = values[1]

        if campaign_arn and (user_id or not user_reqd_for_campaign):
            resolver = PersonalizeRecommendationsResolver(campaign_arn = campaign_arn, filter_arn = filter_arn)

            items = resolver.get_items(
                user_id = user_id, 
                product_id = current_item_id, 
                num_results = num_results
            )

            resp_headers['X-Personalize-Recipe'] = get_recipe(campaign_arn)
        else:
            resolver = DefaultProductResolver(products_service_host = products_service_host, products_service_port = products_service_port)

            items = resolver.get_items(product_id = current_item_id, num_results = num_results)

    for item in items:
        itemId = item['itemId']
        url = f'http://{products_service_host}:{products_service_port}/products/id/{itemId}?fullyQualifyImageUrls={fully_qualify_image_urls}'
        response = requests.get(url)

        if response.ok:
            product = response.json()

            if 'experiment' in item and 'url' in product:
                # Append the experiment correlation ID to the product URL so it gets tracked if used by client.
                product_url = product.get('url')
                if '?' in product_url:
                    product_url += '&'
                else:
                    product_url += '?'

                product_url += 'exp=' + item['experiment']['correlationId']

                product['url'] = product_url

            item.update({ 
                'product': product
            })

        item.pop('itemId')

    resp = Response(json.dumps(items, cls=CompatEncoder), content_type = 'application/json', headers = resp_headers)
    return resp

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

# -- Handlers

app = Flask(__name__)
corps = CORS(app, expose_headers=['X-Experiment-Name', 'X-Experiment-Type', 'X-Experiment-Id', 'X-Personalize-Recipe'])

@app.errorhandler(BadRequest)
def handle_bad_request(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

@app.route('/')
def index():
    return 'Recommendations Service'

@app.route('/health')
def health():
    return 'OK'

@app.route('/related', methods=['GET'])
def related():
    """ Returns related products given an item/product.

    If a feature name is provided and there is an active experiment for the 
    feature, the experiment will be used to retrieve related products. Otherwise, 
    the default behavior will be used which will look to see if an Amazon Personalize 
    campaign for the related items campaign is available. If not, the Product service 
    will be called to get products from the same category as the current product.
    """
    user_id = request.args.get('userID')

    current_item_id = request.args.get('currentItemID')
    if not current_item_id:
        raise BadRequest('currentItemID is required')

    num_results = request.args.get('numResults', default = 25, type = int)
    if num_results < 1:
        raise BadRequest('numResults must be greater than zero')
    if num_results > 100:
        raise BadRequest('numResults must be less than 100')

    # Determine name of feature where related items are being displayed
    feature = request.args.get('feature')

    fully_qualify_image_urls = request.args.get('fullyQualifyImageUrls', '0').lower() in [ 'true', 't', '1']

    try:
        return get_products(
            feature = feature, 
            user_id = user_id, 
            current_item_id = current_item_id, 
            num_results = num_results, 
            campaign_arn_param_name = 'retaildemostore-related-products-campaign-arn', 
            fully_qualify_image_urls = fully_qualify_image_urls
        )

    except Exception as e:
        app.logger.exception('Unexpected error generating related items', e)
        raise BadRequest(message = 'Unhandled error', status_code = 500)

@app.route('/recommendations', methods=['GET'])
def recommendations():
    """ Returns item/product recommendations for a given user in the context
    of a current item (e.g. the user is viewing a product and I want to provide
    recommendations for other products they may be interested in).

    If an experiment is currently active for this feature ('home_product_recs'),
    recommendations will be provided by the experiment. Otherwise, the default 
    behavior will be used which will look to see if an Amazon Personalize 
    campaign is available. If not, the Product service will be called to get 
    products from the same category as the current product or featured products.
    """
    user_id = request.args.get('userID')
    if not user_id:
        raise BadRequest('userID is required')

    current_item_id = request.args.get('currentItemID')

    num_results = request.args.get('numResults', default = 25, type = int)
    if num_results < 1:
        raise BadRequest('numResults must be greater than zero')
    if num_results > 100:
        raise BadRequest('numResults must be less than 100')

    # Determine name of feature where related items are being displayed
    feature = request.args.get('feature')

    fully_qualify_image_urls = request.args.get('fullyQualifyImageUrls', '0').lower() in [ 'true', 't', '1']

    try:
        return get_products(
            feature = feature, 
            user_id = user_id, 
            current_item_id = current_item_id, 
            num_results = num_results, 
            campaign_arn_param_name = 'retaildemostore-product-recommendation-campaign-arn', 
            fully_qualify_image_urls = fully_qualify_image_urls
        )

    except Exception as e:
        app.logger.exception('Unexpected error generating recommendations', e)
        raise BadRequest(message = 'Unhandled error', status_code = 500)

@app.route('/rerank', methods=['GET', 'POST'])
def rerank():
    """ Re-ranks a list of items using personalized reranking """
    if request.method == 'POST':
        try:
            content = request.json
            app.logger.info(content)

            user_id = content.get('userID')
            if not user_id:
                raise BadRequest('userID is required')

            items = content.get('items')
            if not items:
                raise BadRequest('items is required')

            # Determine name of feature where reranked items are being displayed
            feature = request.args.get('feature')

            app.logger.info(items)

            # Extract item IDs from items supplied by caller. Note that unranked items 
            # can be specified as a list of objects with just an 'itemId' key or as a 
            # list of fully defined items/products (i.e. with an 'id' key).
            item_map = {}
            unranked_items = []
            for item in items:
                item_id = item.get('itemId') if item.get('itemId') else item.get('id')
                item_map[item_id] = item
                unranked_items.append(item_id)

            app.logger.info(unranked_items)

            ranked_items = []
            resp_headers = {}
            experiment = None

            # Get active experiment if one is setup for feature and we have a user.
            if feature and user_id:
                exp_manager = ExperimentManager()
                experiment = exp_manager.get_active(feature)

            if experiment:
                # Get ranked items from experiment.
                tracker = exp_manager.default_tracker()

                ranked_items = experiment.get_items(
                    user_id = user_id, 
                    item_list = unranked_items,
                    tracker = tracker
                )

                resp_headers['X-Experiment-Name'] = experiment.name
                resp_headers['X-Experiment-Type'] = experiment.type
                resp_headers['X-Experiment-Id'] = experiment.id
            else:
                # No experiment so check if there's a ranking campaign configured.
                campaign_arn = get_parameter_values('retaildemostore-personalized-ranking-campaign-arn')[0]

                if campaign_arn:
                    resolver = PersonalizeRankingResolver(campaign_arn = campaign_arn)
                    resp_headers['X-Personalize-Recipe'] = get_recipe(campaign_arn)
                else:
                    resolver = RankingProductsNoOpResolver()

                ranked_items = resolver.get_items(
                    user_id = user_id, 
                    product_list = unranked_items
                )

            response_items = []
            for ranked_item in ranked_items:
                item = item_map.get(ranked_item.get('itemId'))

                if 'experiment' in ranked_item and 'url' in item:
                    # Append the experiment correlation ID to the product URL so it gets tracked if used by client.
                    product_url = item.get('url')
                    if '?' in product_url:
                        product_url += '&'
                    else:
                        product_url += '?'

                    product_url += 'exp=' + ranked_item['experiment']['correlationId']

                    item['url'] = product_url

                response_items.append(item)

            resp = Response(json.dumps(response_items, cls=CompatEncoder), content_type = 'application/json', headers = resp_headers)
            return resp
    
        except Exception as e:
            app.logger.exception('Unexpected error reranking items', e)
            return json.dumps(items) 

    if request.method == 'GET':
        app.logger.info("Request Received, Processing")

@app.route('/experiment/outcome', methods=['POST'])
def experiment_outcome():
    """ Tracks an outcome/conversion for an experiment """
    if request.content_type.startswith('application/json'):
        content = request.json
        app.logger.info(content)

        correlation_id = content.get('correlationId')
    else:
        correlation_id = request.form.get('correlationId')
        
    if not correlation_id:
        raise BadRequest('correlationId is required')

    correlation_bits = correlation_id.split('-')
    if len(correlation_bits) != 4:
        raise BadRequest('correlationId is invalid')

    exp_manager = ExperimentManager()
    if not exp_manager.is_configured():
        raise BadRequest('Experiments have not been configured')

    try:
        experiment = exp_manager.get_by_id(correlation_bits[0])
        if not experiment:
            return jsonify({ 'status_code': 404, 'message': 'Experiment not found' }), 404

        user_id = correlation_bits[1]
        variation_index = int(correlation_bits[2])
        result_rank = int(correlation_bits[3])
        experiment.track_conversion(user_id = user_id, variation_index = variation_index, result_rank = result_rank)

        return jsonify(success=True)

    except Exception as e:
        app.logger.exception('Unexpected error logging outcome', e)
        raise BadRequest(message = 'Unhandled error', status_code = 500)

if __name__ == '__main__':
    logging.getLogger('exerimentation').setLevel(level = logging.DEBUG)
    app.wsgi_app = LoggingMiddleware(app.wsgi_app)

    app.run(debug=True,host='0.0.0.0', port=80)