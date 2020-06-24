# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from abc import ABC, abstractmethod

import requests
import boto3
import json
import urllib.parse
import logging

log = logging.getLogger(__name__)
servicediscovery = boto3.client('servicediscovery')

class Resolver(ABC):
    """ Abstract base class for all resolvers"""
    @abstractmethod
    def get_items(self, **kwargs):
        """ Returns recommended items for this resolver

        Arguments:
            Parameters needed by resolver to return recommendations
        
        Return: 
            List of dictionaries where each dictionary minimally includes an 'itemId' key representing a recommended item
        """
        pass

class DefaultProductResolver(Resolver):
    """ Provides recommendations using the Product service

    This class uses the Product service to return items/products from the same 
    category as the currently displayed product or featured products if the 
    current product does not belong to a category. Therefore, this class is a 
    good example of a simple non-personalized approach to making recommendations
    which can be used to test against more sophisticated variations.
    """

    def __init__(self, **params):
        # All we need to initialize this resolver is the instance host/IP and port for the Product service
        self.products_service_host = params.get('products_service_host')
        self.products_service_port = params.get('products_service_port', 80)
        if not self.products_service_host:
            # host/IP wasn't provided so attempt to discover instance
            response = servicediscovery.discover_instances(
                NamespaceName='retaildemostore.local',
                ServiceName='products',
                MaxResults=1,
                HealthStatus='HEALTHY'
            )

            self.products_service_host = response['Instances'][0]['Attributes']['AWS_INSTANCE_IPV4']
            log.debug('DefaultProductResolver - fetched product service instance ' + self.products_service_host)
        else:
            log.debug('DefaultProductResolver - using product service instance ' + self.products_service_host)

        self.fully_qualify_image_urls = params.get('fully_qualify_image_urls', False)

    def get_items(self, **kwargs):
        """ Returns recommended items given a product_id from curated list of products

        Arguments:
            product_id - item ID of the currently displayed product (optional)
            num_results - number of recommendations to return (optional)
        """
        product_id = kwargs.get('product_id')

        num_results = 10
        if kwargs.get('num_results'):
            num_results = int(kwargs['num_results'])

        items = []

        category = None

        if product_id:
            # Lookup product to determine if it belongs to a category
            url = f'http://{self.products_service_host}:{self.products_service_port}/products/id/{product_id}'
            log.debug('DefaultProductResolver - getting product details ' + url)
            response = requests.get(url)

            if response.ok:
                category = response.json()['category']

        if category:
            # Product belongs to a category so get list of products in same category
            url = f'http://{self.products_service_host}:{self.products_service_port}/products/category/{category}?fullyQualifyImageUrls={self.fully_qualify_image_urls}'
            log.debug('DefaultProductResolver - getting products for category ' + url)
            response = requests.get(url)
        else:
            # Product not specified or does not belong to a category so fallback to featured products
            url = f'http://{self.products_service_host}:{self.products_service_port}/products/featured?fullyQualifyImageUrls={self.fully_qualify_image_urls}'
            log.debug('DefaultProductResolver - getting featured products ' + url)
            response = requests.get(url)

        if response.ok:
            # Create response making sure not to include current product
            for product in response.json():
                if product['id'] != product_id:
                    items.append({'itemId': str(product['id'])})

                    if len(items) >= num_results:
                        break
        else:
            raise Exception(f'Error calling products service: {response.status_code}: {response.reason}')

        return items

class SearchSimilarProductsResolver(Resolver): 
    """ Provides recommendations using the Search service

    This class uses the Search service to return items/products similar to 
    an existing/current item/product. Internally the Search service uses 
    the Elasticsearch "more like this" query type which can be considered 
    a content filtering approach to recommendations. So still not personalized 
    but an improvement over the DefaultProductResolver.
    """
    def __init__(self, **params): 
        # All we need to initialize this resolver is the instance host/IP and port for the Search service
        self.search_service_host = params.get('search_service_host') 
        self.search_service_port = params.get('search_service_port', 80) 
        if not self.search_service_host: 
            # host/IP wasn't provided so attempt to discover instance
            response = servicediscovery.discover_instances( 
                NamespaceName='retaildemostore.local', 
                ServiceName='search', 
                MaxResults=1, 
                HealthStatus='HEALTHY' 
            ) 
 
            self.search_service_host = response['Instances'][0]['Attributes']['AWS_INSTANCE_IPV4'] 
            log.debug('SearchSimilarProductsResolver - fetched search service instance ' + self.search_service_host) 
        else: 
            log.debug('SearchSimilarProductsResolver - using search service instance ' + self.search_service_host) 
 
    def get_items(self, **kwargs): 
        """ Returns recommended items given a product_id from using similar item search

        Arguments:
            product_id - item ID of the currently displayed product (required)
            num_results - number of recommendations to return (optional)
        """
        product_id = kwargs.get('product_id') 
        if not product_id: 
            raise Exception('product_id is required') 
 
        num_results = 10 
        if kwargs.get('num_results'): 
            num_results = int(kwargs['num_results']) 
 
        url = f'http://{self.search_service_host}:{self.search_service_port}/similar/products?productId={product_id}' 
        log.debug('SearchSimilarProductsResolver - getting similar products ' + url) 
        response = requests.get(url) 
 
        items = [] 
 
        if response.ok: 
            items = response.json()
            if len(items) > num_results:
                items = items[:num_results]
        else: 
            raise Exception(f'Error calling products service: {response.status_code}: {response.reason}') 
 
        return items 

class PersonalizeRecommendationsResolver(Resolver):
    """ Provides recommendations from an Amazon Personalize campaign """
    __personalize_runtime = boto3.client('personalize-runtime')

    def __init__(self, **params):
        # All we need to initialize this resolver is the ARN for the Personalize campaign
        self.campaign_arn = params.get('campaign_arn')
        if not self.campaign_arn:
            raise Exception('campaign_arn required for PersonalizeRecommendationsResolver')

        # Optionally support filter specified at resolver creation.
        self.filter_arn = params.get('filter_arn')

    def get_items(self, **kwargs):
        """ Returns recommendations from an Amazon Personalize campaign trained with a user recommendation recipe such as HRNN
        
        Arguments:
            user_id - ID for the user for which to make recommendations (required for user personalization recipes such as HRNN)
            product_id - ID for the item to return similar products (required for related products recipes such as SIMS)
            num_results - maximum number of recommendations to return (optional)
            filter_arn - ARN for filter to exclude recommended items (overrides ctor filter_arn) (optional)
        """
        params = {
            'campaignArn': self.campaign_arn 
        }

        user_id = kwargs.get('user_id')
        item_id = kwargs.get('product_id')
        num_results = kwargs.get('num_results')
        filter_arn = kwargs.get('filter_arn')

        if not user_id and not item_id:
            raise Exception('user_id or product_id is required')

        if user_id:
            params['userId'] = user_id

            if filter_arn:
                params['filterArn'] = filter_arn
            elif self.filter_arn:
                params['filterArn'] = self.filter_arn

        if item_id:
            params['itemId'] = item_id

        if num_results:
            params['numResults'] = num_results

        log.debug('PersonalizeRecommendationsResolver - getting recommendations ' + str(params))

        response = PersonalizeRecommendationsResolver.__personalize_runtime.get_recommendations(**params)

        return response['itemList']

class HttpResolver(Resolver):
    """ Provides item recommendations provided by an HTTP resource such as a web service 

    This class is intended to provide example of how you might incorporate 
    recommendations from, say, an existing recommendation system as part of
    an experiment to evaluate Amazon Personalize.
    """
    def __init__(self, **params):
        self.base_url = params.get('base_url')
        if not self.base_url:
            raise Exception('base_url required for HttpResolver')
        self.user_id_parameter_name = params.get('user_id_parameter_name', 'userId')
        self.item_id_parameter_name = params.get('item_id_parameter_name', 'itemId')
        self.num_results_parameter_name = params.get('num_results_parameter_name', 'numResults')

    def get_items(self, **kwargs):
        user_id = kwargs.get('user_id')
        item_id = kwargs.get('product_id')
        num_results = 10
        if kwargs.get('num_results'):
            num_results = int(kwargs['num_results'])

        params = {}

        if user_id:
            params[self.user_id_parameter_name] = user_id
        if item_id:
            params[self.item_id_parameter_name] = item_id
        if num_results:
            params[self.num_results_parameter_name] = num_results

        url = self.base_url
        if '?' in url:
            url += '&'
        else:
            url += '?'

        url += urllib.parse.urlencode(params)

        log.debug('HttpResolver - calling ' + url)
        response = requests.get(url)

        items = []

        if response.ok:
            # This logic assumes we need to do some mapping from the endpoint
            # to the expected response. In this case, we're assuming that the
            # endpoint returns a list of 'id' which we need to map to 'itemId'.
            for item in response.json():
                items.append({'itemId': str(item['id'])})

                if len(items) >= num_results:
                    break
        else:
            raise Exception(f'Error calling HTTP endpoint service: {response.status_code}: {response.reason}')

        return items

class PersonalizeRankingResolver(Resolver):
    """ Provides personalized ranking of products from an Amazon Personalize campaign 
    
    The campaign must be trained using the Personalized-Ranking recipe
    """
    __personalize_runtime = boto3.client('personalize-runtime')

    def __init__(self, **params):
        # All we need to initialize this resolver is the ARN for the Personalize campaign
        self.campaign_arn = params.get('campaign_arn')
        if not self.campaign_arn:
            raise Exception('campaign_arn required for PersonalizeRankingResolver')

    def get_items(self, **kwargs):
        """ Returns reranking items from an Amazon Personalize campaign trained with Personalized-Ranking recipe
        
        Arguments:
            user_id - ID for the user for which to rerank items (required for Personalized-Ranking recipe)
            product_list - list of product IDs to rerank for the user
        """
        user_id = kwargs.get('user_id')
        input_list = kwargs.get('product_list')

        if not user_id:
            raise Exception('user_id is required')

        if not input_list:
            raise Exception('product_list is required')

        params = {
            'campaignArn': self.campaign_arn,
            'userId': str(user_id),
            'inputList': input_list
        }

        log.debug('PersonalizeRankingResolver - getting personalized ranking ' + str(params))

        response = PersonalizeRankingResolver.__personalize_runtime.get_personalized_ranking(**params)

        return response['personalizedRanking']

class RankingProductsNoOpResolver(Resolver):
    """ Simply returns the provided items in unchanged order; a dummy or no-op resolver for ranking use-cases 

    This class is intended to provide a no-op experience for item/product ranking
    use-cases. In other words, if you want the default behavior. The returned items 
    are formatted the same as Personalize to support consistent handling for clients.
    """
    def get_items(self, **kwargs):
        """ Returns reranking items from an Amazon Personalize campaign trained with Personalized-Ranking recipe
        
        Arguments:
            user_id - ID for the user for which to rerank items (required for Personalized-Ranking recipe)
            product_list - list of product IDs to rerank for the user
        """
        input_list = kwargs.get('product_list')

        if not input_list:
            raise Exception('product_list is required')

        # Reformat response as an array of dict with 'itemId' key to match what Personalize would return.
        echo_items = []
        for item_id in input_list:
            echo_items.append({'itemId': item_id})

        return echo_items

class ResolverFactory:
    """ Provides resolver instance given a type and initialization arguments """
    TYPE_HTTP = 'http'
    TYPE_PRODUCT = 'product'
    TYPE_SIMILAR = 'similar'
    TYPE_PERSONALIZE_RECOMMENDATIONS = 'personalize-recommendations'
    TYPE_PERSONALIZE_RANKING = 'personalize-ranking'
    TYPE_RANKING_NO_OP = 'ranking-no-op'

    __resolvers = {}

    @staticmethod
    def register_resolver(type, resolver):
        """ Used by resolvers to register their implementations with the factory """
        ResolverFactory.__resolvers[type] = resolver

    @staticmethod
    def get(type, **params):
        """ Returns an instance of a resolver given its type and initialization arguments """
        log.debug('ResolverFactory - resolving type/params ' + str(type) + '/' + str(params))
        resolver = ResolverFactory.__resolvers.get(type)
        if not resolver:
            raise ValueError(type)
        return resolver(**params)

# Register resolvers with factory

# These resolvers can be used for user recommendations and related product recommendations
ResolverFactory.register_resolver(ResolverFactory.TYPE_PRODUCT, DefaultProductResolver)
ResolverFactory.register_resolver(ResolverFactory.TYPE_SIMILAR, SearchSimilarProductsResolver)
ResolverFactory.register_resolver(ResolverFactory.TYPE_PERSONALIZE_RECOMMENDATIONS, PersonalizeRecommendationsResolver)
ResolverFactory.register_resolver(ResolverFactory.TYPE_HTTP, HttpResolver)
# These resolvers are used with product reranking use-cases
ResolverFactory.register_resolver(ResolverFactory.TYPE_PERSONALIZE_RANKING, PersonalizeRankingResolver)
ResolverFactory.register_resolver(ResolverFactory.TYPE_RANKING_NO_OP, RankingProductsNoOpResolver)
