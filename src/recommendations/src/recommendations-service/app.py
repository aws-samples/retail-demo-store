# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

# AWS X-ray support
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.ext.flask.middleware import XRayMiddleware
from aws_xray_sdk.core import patch_all

patch_all()

from typing import Dict, List, Tuple, Union
from flask import Flask, jsonify, Response
from flask import request

from flask_cors import CORS
from experimentation.experiment_manager import ExperimentManager
from experimentation.resolvers import DefaultProductResolver, PersonalizeRecommendationsResolver, \
    PersonalizeRankingResolver, RankingProductsNoOpResolver, PersonalizeContextComparePickResolver, RandomPickResolver
from experimentation.utils import CompatEncoder
from expiring_dict import ExpiringDict

import json
import os
import pprint
import boto3
import requests
import random
import logging
from datetime import datetime

NUM_DISCOUNTS = 2

EXPERIMENTATION_LOGGING = True
DEBUG_LOGGING = True

random.seed(42)  # Keep our demonstration deterministic

# Since the DescribeRecommender/DescribeCampaign APIs easily throttles and we just
# need the recipe from the recommender/campaign and it won't change often (if at all),
# use a cache to help smooth out periods where we get throttled.
personalize_meta_cache = ExpiringDict(2 * 60 * 60)

servicediscovery = boto3.client('servicediscovery')
personalize = boto3.client('personalize')
personalize_runtime = boto3.client('personalize-runtime')
ssm = boto3.client('ssm')
codepipeline = boto3.client('codepipeline')
sts = boto3.client('sts')
cw_events = boto3.client('events')

# SSM parameter name for the Personalize filter for purchased and c-store items
filter_purchased_param_name = '/retaildemostore/personalize/filters/filter-purchased-arn'
filter_cstore_param_name = '/retaildemostore/personalize/filters/filter-cstore-arn'
filter_purchased_cstore_param_name = '/retaildemostore/personalize/filters/filter-purchased-and-cstore-arn'
filter_include_categories_param_name = '/retaildemostore/personalize/filters/filter-include-categories-arn'
promotion_filter_param_name = '/retaildemostore/personalize/filters/promoted-items-filter-arn'
promotion_filter_no_cstore_param_name = '/retaildemostore/personalize/filters/promoted-items-no-cstore-filter-arn'
offers_arn_param_name = '/retaildemostore/personalize/personalized-offers-arn'

# -- Shared Functions

def get_recipe(arn):
    """ Returns the Amazon Personalize recipe ARN for the specified campaign/recommender ARN """
    recipe = None

    is_recommender = arn.split(':')[5].startswith('recommender/')

    resource = personalize_meta_cache.get(arn)
    if not resource:
        if is_recommender:
            response = personalize.describe_recommender(recommenderArn = arn)
            if response.get('recommender'):
                resource = response['recommender']
                personalize_meta_cache[arn] = resource
        else:
            response = personalize.describe_campaign(campaignArn = arn)
            if response.get('campaign'):
                resource = response['campaign']
                personalize_meta_cache[arn] = resource

    if resource:
        if is_recommender:
            recipe = resource['recipeArn']
        else:
            solution_version = personalize_meta_cache.get(resource['solutionVersionArn'])

            if not solution_version:
                response = personalize.describe_solution_version(solutionVersionArn = resource['solutionVersionArn'])
                if response.get('solutionVersion'):
                    solution_version = response['solutionVersion']
                    personalize_meta_cache[resource['solutionVersionArn']] = solution_version

            if solution_version:
                recipe = solution_version['recipeArn']

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

def get_timestamp_from_request() -> datetime:
    timestamp_raw = request.args.get('timestamp')
    if not timestamp_raw and request.method == 'POST':
        if request.is_json:
            timestamp_raw = request.json.get('timestamp')
        elif request.content_type.startswith('application/x-www-form-urlencoded'):
            timestamp_raw = request.form.get('timestamp')

    timestamp: datetime = None
    if timestamp_raw:
        if isinstance(timestamp_raw, str) and not timestamp_raw.isnumeric():
            raise BadRequest('timestamp is not numeric (must be unix time)')
        timestamp = datetime.fromtimestamp(int(timestamp_raw))

    return timestamp

def get_products_service_host_and_port() -> Tuple[str, int]:
    """ Returns a tuple of the products service host name and port """
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

    return products_service_host, products_service_port

def fetch_product_details(item_ids: Union[str, List[str]], fully_qualify_image_urls=False) -> List[Dict]:
    """ Fetches details for one or more products from the products service """
    products_service_host, products_service_port = get_products_service_host_and_port()

    item_ids_csv = item_ids if isinstance(item_ids, str) else ','.join(item_ids)

    url = f'http://{products_service_host}:{products_service_port}/products/id/{item_ids_csv}?fullyQualifyImageUrls={fully_qualify_image_urls}'
    app.logger.debug(f"Asking for product info from {url}")

    products = []

    response = requests.get(url)
    if response.ok:
        products = response.json()
        if not isinstance(products, list):
            products = [ products ]

    return products

def get_products(feature, user_id, current_item_id, num_results, default_inference_arn_param_name,
                 default_filter_arn_param_name, filter_values=None, user_reqd_for_inference=False, fully_qualify_image_urls=False,
                 promotion: Dict = None
                 ):
    """ Returns products given a UI feature, user, item/product.

    If a feature name is provided and there is an active experiment for the
    feature, the experiment will be used to retrieve products. Otherwise,
    the default behavior will be used which will look to see if an Amazon Personalize
    campaign/recommender is available. If not, the Product service will be called to get products
    from the same category as the current product.
    Args:
        feature: Used to track different experiments - different experiments pertain to different features
        user_id: If supplied we are looking at user personalization
        current_item_id: Or maybe we are looking at related items
        num_results: Num to return
        default_inference_arn_param_name: If no experiment active, use this SSM parameters to get recommender Arn
        default_filter_arn_param_name: If no experiment active, use this SSM parameter to get filter Arn, if exists
        filter_values: Values to pass at inference for the filter
        user_reqd_for_inference: Require a user ID to use Personalze - otherwise default
        fully_qualify_image_urls: Fully qualify image URLs n here
        promotion: Personalize promotional filter configuration
    Returns:
        A prepared HTTP response object.
    """

    items = []
    resp_headers = {}
    experiment = None
    exp_manager = None

    # Get active experiment if one is setup for feature and we have a user.
    if feature and user_id:
        exp_manager = ExperimentManager()
        experiment = exp_manager.get_active(feature, user_id)

    if experiment:
        # Get items from experiment.
        tracker = exp_manager.default_tracker()

        items = experiment.get_items(
            user_id = user_id,
            current_item_id = current_item_id,
            num_results = num_results,
            tracker = tracker,
            filter_values = filter_values,
            timestamp = get_timestamp_from_request(),
            promotion = promotion
        )

        resp_headers['X-Experiment-Name'] = experiment.name
        resp_headers['X-Experiment-Type'] = experiment.type
        resp_headers['X-Experiment-Id'] = experiment.id
    else:
        # Fallback to default behavior of checking for campaign/recommender ARN parameter and
        # then the default product resolver.
        values = get_parameter_values([default_inference_arn_param_name, default_filter_arn_param_name])

        inference_arn = values[0]
        filter_arn = values[1]

        if inference_arn and (user_id or not user_reqd_for_inference):

            logger.info(f"get_products: Supplied campaign/recommender: {inference_arn} (from {default_inference_arn_param_name}) Supplied filter: {filter_arn} (from {default_filter_arn_param_name}) Supplied user: {user_id}")

            resolver = PersonalizeRecommendationsResolver(inference_arn = inference_arn, filter_arn = filter_arn)

            items = resolver.get_items(
                user_id = user_id,
                product_id = current_item_id,
                num_results = num_results,
                filter_values = filter_values,
                promotion = promotion
            )

            resp_headers['X-Personalize-Recipe'] = get_recipe(inference_arn)
        else:
            products_service_host, products_service_port = get_products_service_host_and_port()
            resolver = DefaultProductResolver(products_service_host = products_service_host, products_service_port = products_service_port)

            items = resolver.get_items(product_id = current_item_id, num_results = num_results)

    item_ids = [item['itemId'] for item in items]

    products = fetch_product_details(item_ids, fully_qualify_image_urls)
    for item in items:
        item_id = item['itemId']

        product = next((p for p in products if p['id'] == item_id), None)
        if product is not None and 'experiment' in item and 'url' in product:
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

    return items, resp_headers

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
logger = app.logger
corps = CORS(app, expose_headers=['X-Experiment-Name', 'X-Experiment-Type', 'X-Experiment-Id', 'X-Personalize-Recipe'])

xray_recorder.configure(service='Recommendations Service')
XRayMiddleware(app, xray_recorder)

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
    campaign/recommender for related items is available. If not, the Product service
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

    # The default filter includes products from the same category as the current item.
    filter_ssm = request.args.get('filter', filter_include_categories_param_name)
    # We have short names for these filters
    if filter_ssm == 'cstore': filter_ssm = filter_cstore_param_name
    elif filter_ssm == 'purchased': filter_ssm = filter_purchased_param_name
    app.logger.info("Filter SSM for /related: %s", filter_ssm)

    filter_values = None
    if filter_ssm == filter_include_categories_param_name:
        category = request.args.get('currentItemCategory')
        if not category:
            products = fetch_product_details(current_item_id)
            if products:
                category = products[0]['category']

        filter_values = { "CATEGORIES": f"\"{category}\"" }

    # Determine name of feature where related items are being displayed
    feature = request.args.get('feature')

    fully_qualify_image_urls = request.args.get('fullyQualifyImageUrls', '0').lower() in [ 'true', 't', '1']

    try:
        # If a user ID is provided, automatically perform reranking of related items to personalize items (composite use case).
        if user_id:
            rerank_items = True
            related_count = num_results * 3
        else:
            rerank_items = False
            related_count = num_results

        items, resp_headers = get_products(
            feature = feature,
            user_id = user_id,
            current_item_id = current_item_id,
            num_results = related_count,
            default_inference_arn_param_name='/retaildemostore/personalize/related-items-arn',
            default_filter_arn_param_name=filter_ssm,
            filter_values=filter_values,
            fully_qualify_image_urls = fully_qualify_image_urls
        )

        if rerank_items:
            app.logger.info('Reranking related items to personalize order for user %s', user_id)
            items, resp_headers = get_ranking(user_id, items, feature = None, resp_headers = resp_headers)

            items = items[0:num_results]    # Trim back down to the requested number of items.

        resp = Response(json.dumps(items, cls=CompatEncoder), content_type = 'application/json', headers = resp_headers)
        return resp

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
    campaign/recommender is available. If not, the Product service will be called to get
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

    # The default filter is the not-already-purchased filter
    filter_ssm = request.args.get('filter', filter_purchased_param_name)
    # We have short names for these filters
    if filter_ssm == 'cstore': filter_ssm = filter_cstore_param_name
    elif filter_ssm == 'purchased': filter_ssm = filter_purchased_param_name
    app.logger.info(f"Filter SSM for /recommendations: {filter_ssm}")

    fully_qualify_image_urls = request.args.get('fullyQualifyImageUrls', '0').lower() in [ 'true', 't', '1']

    promotion = None
    promotion_filter_arn = get_parameter_values(promotion_filter_param_name)[0]
    if promotion_filter_arn:
        promotion = {
            'name': 'promotedItem',
            'percentPromotedItems': 25,
            'filterArn': promotion_filter_arn
        }

    try:
        items, resp_headers = get_products(
            feature = feature,
            user_id = user_id,
            current_item_id = current_item_id,
            num_results = num_results,
            default_inference_arn_param_name='/retaildemostore/personalize/recommended-for-you-arn',
            default_filter_arn_param_name=filter_ssm,
            fully_qualify_image_urls = fully_qualify_image_urls,
            promotion = promotion
        )

        response = Response(json.dumps(items, cls=CompatEncoder), content_type = 'application/json', headers = resp_headers)

        app.logger.debug("Recommendations response to be returned: %s", response)
        return response

    except Exception as e:
        app.logger.exception('Unexpected error generating recommendations', e)
        raise BadRequest(message = 'Unhandled error', status_code = 500)

@app.route('/popular', methods=['GET'])
def popular():
    """ Returns item/product recommendations for a given user in the context
    of a current item (e.g. the user is viewing a product and I want to provide
    recommendations for other products they may be interested in).

    If an experiment is currently active for this feature ('home_product_recs'),
    recommendations will be provided by the experiment. Otherwise, the default
    behavior will be used which will look to see if an Amazon Personalize
    campaign/recommender is available. If not, the Product service will be called to get
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

    # The default filter is the exclude already purchased and c-store products filter
    filter_ssm = request.args.get('filter', filter_purchased_cstore_param_name)
    # We have short names for these filters
    if filter_ssm == 'cstore': filter_ssm = filter_cstore_param_name
    elif filter_ssm == 'purchased': filter_ssm = filter_purchased_cstore_param_name
    app.logger.info(f"Filter SSM for /recommendations: {filter_ssm}")

    fully_qualify_image_urls = request.args.get('fullyQualifyImageUrls', '0').lower() in [ 'true', 't', '1']

    promotion = None
    promotion_filter_arn = get_parameter_values(promotion_filter_no_cstore_param_name)[0]
    if promotion_filter_arn:
        promotion = {
            'name': 'promotedItem',
            'percentPromotedItems': 25,
            'filterArn': promotion_filter_arn
        }

    try:
        items, resp_headers = get_products(
            feature = feature,
            user_id = user_id,
            current_item_id = current_item_id,
            num_results = num_results,
            default_inference_arn_param_name='/retaildemostore/personalize/popular-items-arn',
            default_filter_arn_param_name=filter_ssm,
            fully_qualify_image_urls = fully_qualify_image_urls,
            promotion = promotion
        )

        response = Response(json.dumps(items, cls=CompatEncoder), content_type = 'application/json', headers = resp_headers)

        app.logger.debug("Recommendations response to be returned: %s", response)
        return response

    except Exception as e:
        app.logger.exception('Unexpected error generating recommendations', e)
        raise BadRequest(message = 'Unhandled error', status_code = 500)

def ranking_request_params():
    """
    Utility function which grabs a JSON body and extracts the UserID, item list and feature name.
    Returns:
        3-tuple of user ID, item list and feature name
    """

    content = request.json
    app.logger.info(f"JSON payload: {content}")

    user_id = content.get('userID')
    if not user_id:
        raise BadRequest('userID is required')

    items = content.get('items')
    if not items:
        raise BadRequest('items is required')

    # Determine name of feature where reranked items are being displayed
    feature = content.get('feature')
    if not feature:
        feature = request.args.get('feature')

    app.logger.info(f"Items pulled from json: {items}")

    return user_id, items, feature

def get_ranking(user_id, items, feature,
                default_inference_arn_param_name='/retaildemostore/personalize/personalized-ranking-arn',
                top_n=None, context=None, resp_headers=None):
    """
    Re-ranks a list of items using personalized reranking.
    Or delegates to experiment manager if there is an active experiment.

    Args:
        user_id (int):
        items (list[dict]): e.g. [{"itemId":"33", "url":"path_to_product33"},
                                  {"itemId":"22", "url":"path_to_product22"}]
        feature: Used to lookup the currently active experiment.
        default_inference_arn_param_name: For discounts this would be different.
        top_n (Optional[int]): Only return the top N ranked if not None.
        context (Optional[dict]): If available, passed to the reranking Personalization recipe.
        resp_headers (Optional[dict]): Response headers from chained call

    Returns:
        Items as passed in, but ordered according to reranker - also might have experimentation metadata added.
    """

    app.logger.info(f"Items given for ranking: {items}")

    # Extract item IDs from items supplied by caller. Note that unranked items
    # can be specified as a list of objects with just an 'itemId' key or as a
    # list of fully defined items/products (i.e. with an 'id' key).
    item_map = {}
    unranked_items = []
    for item in items:
        item_id = item.get('itemId')
        if not item_id:
            item_id = item.get('id')
        if not item_id and item.get('product'):
            item_id = item.get('product').get('id')
        item_map[item_id] = item
        unranked_items.append(item_id)

    app.logger.info(f"Unranked items: {unranked_items}")

    if resp_headers is None:
        resp_headers = {}

    experiment = None
    exp_manager = None

    # Get active experiment if one is setup for feature.
    if feature:
        exp_manager = ExperimentManager()
        experiment = exp_manager.get_active(feature, user_id)

    if experiment:
        app.logger.info('Using experiment: %s', experiment.name)

        # Get ranked items from experiment.
        tracker = exp_manager.default_tracker()

        ranked_items = experiment.get_items(
            user_id=user_id,
            item_list=unranked_items,
            tracker=tracker,
            context=context,
            timestamp=get_timestamp_from_request()
        )

        app.logger.debug("Experiment ranking resolver gave us this ranking: %s", ranked_items)

        resp_headers['X-Experiment-Name'] = experiment.name
        resp_headers['X-Experiment-Type'] = experiment.type
        resp_headers['X-Experiment-Id'] = experiment.id
    else:
        # Fallback to default behavior of checking for campaign/recommender ARN parameter and
        # then the default product resolver.
        values = get_parameter_values([default_inference_arn_param_name, filter_purchased_param_name])
        app.logger.info(f'Falling back to Personalize: {values}')

        inference_arn = values[0]
        filter_arn = values[1]

        if inference_arn:
            resolver = PersonalizeRankingResolver(inference_arn=inference_arn, filter_arn=filter_arn)
            recipe_arn = get_recipe(inference_arn)
            if resp_headers.get('X-Personalize-Recipe'):
                resp_headers['X-Personalize-Recipe'] = resp_headers['X-Personalize-Recipe'] + ',' + recipe_arn
            else:
                resp_headers['X-Personalize-Recipe'] = recipe_arn
        else:
            app.logger.info(f'Falling back to No-op: {values}')
            resolver = RankingProductsNoOpResolver()

        ranked_items = resolver.get_items(
            user_id=user_id,
            product_list=unranked_items,
            context=context
        )

    response_items = []
    if top_n is not None:
        # We may not want to return them all - for example in a "pick the top N" scenario.
        ranked_items = ranked_items[:top_n]

    for ranked_item in ranked_items:
        # Unlike with /recommendations and /related we are not hitting the products API to get product info back
        # The caller may have left that info in there so in case they have we want to leave it in.
        item = item_map.get(ranked_item.get('itemId'))

        if 'experiment' in ranked_item:

            item['experiment'] = ranked_item['experiment']

            if 'url' in item:
                # Append the experiment correlation ID to the product URL so it gets tracked if used by client.
                product_url = item.get('url')
                if '?' in product_url:
                    product_url += '&'
                else:
                    product_url += '?'

                product_url += 'exp=' + ranked_item['experiment']['correlationId']

                item['url'] = product_url

        response_items.append(item)

    return response_items, resp_headers

@app.route('/rerank', methods=['POST'])
def rerank():
    """
    Gets user ID, items list and feature and gets ranking of items according to reranking campaign.
    """
    items = []
    try:
        user_id, items, feature = ranking_request_params()
        print('ITEMS', items)
        response_items, resp_headers = get_ranking(user_id, items, feature)
        app.logger.debug(f"Response items for reranking: {response_items}")
        resp = Response(json.dumps(response_items, cls=CompatEncoder), content_type='application/json',
                        headers=resp_headers)
        return resp
    except Exception as e:
        app.logger.exception('Unexpected error reranking items', e)
        return json.dumps(items)


def get_top_n(user_id, items, feature, top_n,
            default_inference_arn_param_name='/retaildemostore/personalize/personalized-ranking-arn'):
    """
    Gets Top N items using provided campaign/recommender.
    Or delegates to experiment manager if there is an active experiment.

    Args:
        user_id (int): User to get the topN for
        items (list[dict]): e.g. [{"itemId":"33", "url":"path_to_product33"},
                                  {"itemId":"22", "url":"path_to_product22"}]
        feature: Used to lookup the currently active experiment.
        top_n (int): Only return the top N ranked if not None.
        default_inference_arn_param_name: Change this to use a different campaign/recommender.

    Returns:
        Items as passed in, but truncated according to picker - also might have experimentation metadata added.
    """

    app.logger.info(f"Items given for top-n: {items}")

    # Extract item IDs from items supplied by caller. Note that unranked items
    # can be specified as a list of objects with just an 'itemId' key or as a
    # list of fully defined items/products (i.e. with an 'id' key).
    item_map = {}
    unranked_items = []
    for item in items:
        item_id = item.get('itemId') if item.get('itemId') else item.get('id')
        item_map[item_id] = item
        unranked_items.append(item_id)

    app.logger.info(f"Pre-selection items: {unranked_items}")

    resp_headers = {}
    experiment = None
    exp_manager = None

    # Get active experiment if one is setup for feature.
    if feature:
        exp_manager = ExperimentManager()
        experiment = exp_manager.get_active(feature, user_id)

    if experiment:
        app.logger.info('Using experiment: ' + experiment.name)

        # Get ranked items from experiment.
        tracker = exp_manager.default_tracker()

        topn_items = experiment.get_items(
            user_id=user_id,
            item_list=unranked_items,
            tracker=tracker,
            num_results=top_n,
            timestamp=get_timestamp_from_request()
        )

        app.logger.debug(f"Experiment ranking resolver gave us this ranking: {topn_items}")

        resp_headers['X-Experiment-Name'] = experiment.name
        resp_headers['X-Experiment-Type'] = experiment.type
        resp_headers['X-Experiment-Id'] = experiment.id
    else:
        # Fallback to default behavior of checking for campaign/recommender ARN parameter and
        # then the default product resolver.
        values = get_parameter_values([default_inference_arn_param_name, filter_purchased_param_name])
        app.logger.info(f'Falling back to Personalize: {values}')

        inference_arn = values[0]
        filter_arn = values[1]

        if inference_arn:
            resolver = PersonalizeContextComparePickResolver(inference_arn=inference_arn, filter_arn=filter_arn,
                                                             with_context={'Discount': 'Yes'},
                                                             without_context={})
            resp_headers['X-Personalize-Recipe'] = get_recipe(inference_arn)
        else:
            app.logger.info(f'Falling back to No-op: {values}')
            resolver = RandomPickResolver()

        topn_items = resolver.get_items(
            user_id=user_id,
            product_list=unranked_items,
            num_results=top_n
        )

    logger.info(f"Sorted items: returned from resolver: {topn_items}")

    response_items = []

    for top_item in topn_items:
        # Unlike with /recommendations and /related we are not hitting the products API to get product info back
        # The caller may have left that info in there so in case they have we want to leave it in.
        item_id = top_item['itemId']
        item = item_map[item_id]

        if 'experiment' in top_item:

            item['experiment'] = top_item['experiment']

            if 'url' in item:
                # Append the experiment correlation ID to the product URL so it gets tracked if used by client.
                product_url = item.get('url')
                if '?' in product_url:
                    product_url += '&'
                else:
                    product_url += '?'

                product_url += 'exp=' + top_item['experiment']['correlationId']

                item['url'] = product_url

        response_items.append(item)

    logger.info(f"Top-N response: with details added back in: {topn_items}")

    return response_items, resp_headers


@app.route('/choose_discounted', methods=['POST'])
def choose_discounted():
    """
    Gets user ID, items list and feature and chooses which items to discount according to the
    reranking campaign. Gets a ranking with discount applied and without (using contextual metadata)
    and looks at the difference. The products are ordered according to how the response is expected
    to improve after applying discount.

    The items that are not chosen for discount will be returned as-is but with the "discounted" key set to False.
    The items that are chosen for discount will have the "discounted" key set to True.

    If there is an experiment active for this feature the request for ranking for choosing discounts will have been
    routed through the experiment resolver and discounts chosen according to whichever approach is active. The
    items will have experiment information recorded against them and if URLs were provided for products these will be
    suffixed with an experiment tracking correlation ID. That way, different approaches to discounting can be compared,
    as with different approaches to recommendations and reranking in other campaigns.
    """
    items = []
    try:
        user_id, items, feature = ranking_request_params()
        response_items, resp_headers = get_top_n(user_id, items, feature, NUM_DISCOUNTS)
        discount_item_map = {item['itemId']: item for item in response_items}

        return_items = []
        for item in items:
            item_id = item['itemId']
            if item_id in discount_item_map:
                # This was picked for discount so we flag it as a discounted item. It may also have experiment
                # information recorded against it by get_ranking() if an experiment is active.
                discounted_item = discount_item_map[item_id]
                discounted_item['discounted'] = True
                return_items.append(discounted_item)
            else:
                # This was not picked for discount, so is not participating in any experiment comparing
                # discount approaches and we also do not flag it as a discounted item
                item['discounted'] = False
                return_items.append(item)

        resp = Response(json.dumps(items, cls=CompatEncoder), content_type='application/json',
                        headers=resp_headers)
        return resp
    except Exception as e:
        app.logger.exception('Unexpected error calculating discounted items', e)
        return json.dumps(items)


def get_offers_service():
    """
    Get offers service URL root. Check for env variables first in case we're running in a local Docker container (dev mode)
    """

    service_host = os.environ.get('OFFERS_SERVICE_HOST')
    service_port = os.environ.get('OFFERS_SERVICE_PORT', 80)

    if not service_host or service_host.strip().lower() == 'offers.retaildemostore.local':
        # Get product service instance. We'll need it rehydrate product info for recommendations.
        response = servicediscovery.discover_instances(
            NamespaceName='retaildemostore.local',
            ServiceName='offers',
            MaxResults=1,
            HealthStatus='HEALTHY'
        )

        service_host = response['Instances'][0]['Attributes']['AWS_INSTANCE_IPV4']

    return service_host, service_port


def get_all_offers_by_id():
    """We might wish to prepopulate all offers if we are going to be picking up multiple offers."""
    offers_service_host, offers_service_port = get_offers_service()
    url = f'http://{offers_service_host}:{offers_service_port}/offers'
    logger.debug(f"Asking for offers info from {url}")
    offers_response = requests.get(url)  # we let connection error propagate
    logger.debug(f"Got offer info: {offers_response}")
    if not offers_response.ok:
        logger.error(f"Offers service not giving us offers: {offers_response.reason}")
        raise BadRequest(message='Cannot obtain offers', status_code=500)
    offers = offers_response.json()['tasks']
    offers_by_id = {str(offer['id']): offer for offer in offers}
    return offers_by_id


def get_offer_by_id(offer_id):
    offers_service_host, offers_service_port = get_offers_service()
    url = f'http://{offers_service_host}:{offers_service_port}/offers/{offer_id}'
    logger.debug(f"Asking for offer info from {url}")
    offers_response = requests.get(url)  # we let connection error propagate
    logger.debug(f"Got offer info: {offers_response}")
    if not offers_response.ok:
        logger.error(f"Offers service not giving us offers: {offers_response.reason}")
        raise BadRequest(message='Cannot obtain offers', status_code=500)
    offer = offers_response.json()['task']
    return offer


@app.route('/coupon_offer', methods=['GET'])
def coupon_offer():
    """
    Returns an offer recommendation for a given user.

    Hits the offers endpoint to find what offers are available, get their preferences for adjusting scores.
    Uses Amazon Personalize if available to score them.
    Returns the highest scoring offer.

    Experimentation is disabled because we are sending the offers through Pinpoint emails and for this
    demonstration we would need to add some more complexity to track those within the current framework.
    Pinpoint also has A/B experimentation built in which can be used.
    """

    user_id = request.args.get('userID')
    if not user_id:
        raise BadRequest('userID is required')

    resp_headers = {}
    try:

        inference_arn = get_parameter_values(offers_arn_param_name)[0]
        offers_service_host, offers_service_port = get_offers_service()

        url = f'http://{offers_service_host}:{offers_service_port}/offers'
        app.logger.debug(f"Asking for offers info from {url}")
        offers_response = requests.get(url)
        app.logger.debug(f"Got offer info: {offers_response}")

        if not offers_response.ok:
            app.logger.exception('Offers service did not return happily', offers_response.reason())
            raise BadRequest(message='Cannot obtain offers', status_code=500)
        else:

            offers = offers_response.json()['tasks']
            offers_by_id = {str(offer['id']): offer for offer in offers}
            offer_ids = sorted(list(offers_by_id.keys()))

            if not inference_arn:
                app.logger.warning('No campaign Arn set for offers - returning arbitrary')
                # We deterministically choose an offer
                # - random approach would have been chosen_offer_id = random.choice(offer_ids)
                chosen_offer_id = offer_ids[int(user_id) % len(offer_ids)]
                chosen_score = None
            else:
                resp_headers['X-Personalize-Recipe'] = get_recipe(inference_arn)
                logger.info(f"Input to Personalized Ranking for offers: userId: {user_id}({type(user_id)}) "
                            f"inputList: {offer_ids}")
                get_recommendations_response = personalize_runtime.get_recommendations(
                    campaignArn=inference_arn,
                    userId=user_id,
                    numResults=len(offer_ids)
                )

                logger.info(f'Recommendations returned: {json.dumps(get_recommendations_response)}')

                return_key = 'itemList'
                # Here is where might want to incorporate some business logic
                # for more information on how these scores are used see
                # https://aws.amazon.com/blogs/machine-learning/introducing-recommendation-scores-in-amazon-personalize/

                # An alternative approach would be to train Personalize to produce recommendations based on objectives
                # we specify rather than the default which is to maximise the target event. For more information, see
                # https://docs.aws.amazon.com/personalize/latest/dg/optimizing-solution-for-objective.html

                user_scores = {item['itemId']: float(item['score']) for item in
                               get_recommendations_response[return_key]}
                # We assume we have pre-calculated the adjusting factor, can be a mix of probability when applicable,
                # calculation of expected return per offer, etc.
                adjusted_scores = {offer_id: score * offers_by_id[offer_id]['preference']
                                   for offer_id, score in user_scores.items()}
                logger.info(f"Scores after adjusting for preference parameters: {adjusted_scores}")

                # Normalise these - makes it easier to do further adjustments
                score_sum = sum(adjusted_scores.values())
                adjusted_scores = {offer_id: score / score_sum
                                   for offer_id, score in adjusted_scores.items()}
                logger.info(f"Scores after normalising adjusted scores: {adjusted_scores}")

                # Just one way we could add some randomness - adds serendipity though removes personalization a bit
                # because we have the scores though we retain a lot of the personalization
                random_factor = 0.0
                adjusted_scores = {offer_id: score*(1-random_factor) + random_factor*random.random()
                                   for offer_id, score in adjusted_scores.items()}
                logger.info(f"Scores after adding randomness: {adjusted_scores}")

                # We can do many other things here, like randomisation, normalisation in different dimensions,
                # tracking per-user, offer, quotas, etc. Here, we just select the most promising adjusted score
                chosen_offer_id = max(adjusted_scores, key=adjusted_scores.get)
                chosen_score = user_scores[chosen_offer_id]
                chosen_adjusted_score = adjusted_scores[chosen_offer_id]

            chosen_offer = offers_by_id[chosen_offer_id]
            if chosen_score is not None:
                chosen_offer['score'] = chosen_score
                chosen_offer['adjusted_score'] = chosen_adjusted_score

        resp = Response(json.dumps({'offer': chosen_offer}, cls=CompatEncoder),
                        content_type='application/json', headers=resp_headers)

        app.logger.debug(f"Recommendations response to be returned for offers: {resp}")
        return resp

    except Exception as e:
        app.logger.exception('Unexpected error generating recommendations', e)
        raise BadRequest(message='Unhandled error', status_code=500)


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

    exp_manager = ExperimentManager()

    try:
        experiment = exp_manager.get_by_correlation_id(correlation_id)
        if not experiment:
            return jsonify({ 'status_code': 404, 'message': 'Experiment not found' }), 404

        experiment.track_conversion(correlation_id, get_timestamp_from_request())

        return jsonify(success=True)

    except Exception as e:
        app.logger.exception('Unexpected error logging outcome', e)
        raise BadRequest(message='Unhandled error', status_code=500)

if __name__ == '__main__':

    if DEBUG_LOGGING:
        level = logging.DEBUG
    else:
        level = logging.INFO
    app.logger.setLevel(level)
    if EXPERIMENTATION_LOGGING:
        logging.getLogger('experimentation').setLevel(level=level)
        logging.getLogger('experimentation.experiment_manager').setLevel(level=level)
        for handler in app.logger.handlers:
            logging.getLogger('experimentation').addHandler(handler)
            logging.getLogger('experimentation.experiment_manager').addHandler(handler)
            handler.setLevel(level)  # this will get the main app logs to CloudWatch

    app.wsgi_app = LoggingMiddleware(app.wsgi_app)

    app.run(debug=True, host='0.0.0.0', port=80)
