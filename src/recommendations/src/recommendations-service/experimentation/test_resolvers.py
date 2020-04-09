# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import unittest
import json
import botocore
import logging

from unittest.mock import patch
from experimentation.resolvers import (ResolverFactory, HttpResolver, DefaultProductResolver, PersonalizeRecommendationsResolver, 
    SearchSimilarProductsResolver, PersonalizeRankingResolver, RankingProductsNoOpResolver)

"""
python -m unittest experimentation/test_resolvers.py
"""

class TestResolvers(unittest.TestCase):

    def test_factory(self):
        resolver = ResolverFactory.get(ResolverFactory.TYPE_HTTP, base_url = 'http://server.com/path', user_id_parameter_name = 'userId')
        self.assertTrue(type(resolver) is HttpResolver)

        resolver = ResolverFactory.get(ResolverFactory.TYPE_PRODUCT, products_service_host = '10.10.10.10')
        self.assertTrue(type(resolver) is DefaultProductResolver)

        resolver = ResolverFactory.get(ResolverFactory.TYPE_PERSONALIZE_RECOMMENDATIONS, campaign_arn = 'the_arn')
        self.assertTrue(type(resolver) is PersonalizeRecommendationsResolver)

        resolver = ResolverFactory.get(ResolverFactory.TYPE_SIMILAR, search_service_host = '10.10.10.11')
        self.assertTrue(type(resolver) is SearchSimilarProductsResolver)

        resolver = ResolverFactory.get(ResolverFactory.TYPE_PERSONALIZE_RANKING, campaign_arn = 'the_arn')
        self.assertTrue(type(resolver) is PersonalizeRankingResolver)

        resolver = ResolverFactory.get(ResolverFactory.TYPE_RANKING_NO_OP)
        self.assertTrue(type(resolver) is RankingProductsNoOpResolver)

        with self.assertRaises(ValueError):
            ResolverFactory.get('bogus')

    def test_http_resolver(self):
        with patch('experimentation.resolvers.requests.get') as mocked_get:
            mocked_get.return_value.ok = True
            mocked_get.return_value.json.return_value = [{'id':'1'},{'id':'2'},{'id':'3'},{'id':'4'} ]

            resolver = ResolverFactory.get(ResolverFactory.TYPE_HTTP, base_url = 'http://server.com/path', user_id_parameter_name = 'userId')
            items = resolver.get_items(user_id = '1')
            self.assertEqual(len(items), 4)
            self.assertEqual(items[0]['itemId'], '1')
            self.assertEqual(items[1]['itemId'], '2')
            self.assertEqual(items[2]['itemId'], '3')
            self.assertEqual(items[3]['itemId'], '4')

            mocked_get.assert_called_with('http://server.com/path?userId=1&numResults=10')

    def test_product_resolver(self):
        with patch('experimentation.resolvers.requests.get') as mocked_get:
            mocked_get.return_value.ok = True
            mocked_get.return_value.json.return_value = [{'id':'1'},{'id':'2'},{'id':'3'},{'id':'4'} ]

            resolver = ResolverFactory.get(ResolverFactory.TYPE_PRODUCT, products_service_host = '10.10.10.10')
            items = resolver.get_items(product_id = None)
            self.assertEqual(len(items), 4)

    def test_similar_resolver(self):
        with patch('experimentation.resolvers.requests.get') as mocked_get:
            mocked_get.return_value.ok = True
            mocked_get.return_value.json.return_value = [{'itemId':'1'},{'itemId':'2'},{'itemId':'3'},{'itemId':'4'} ]

            resolver = ResolverFactory.get(ResolverFactory.TYPE_SIMILAR, search_service_host = '10.10.10.10', search_service_port = 8000)
            items = resolver.get_items(product_id = '100')
            self.assertEqual(len(items), 4)
            self.assertEqual(items[0]['itemId'], '1')
            self.assertEqual(items[1]['itemId'], '2')
            self.assertEqual(items[2]['itemId'], '3')
            self.assertEqual(items[3]['itemId'], '4')

            mocked_get.assert_called_with('http://10.10.10.10:8000/similar/products?productId=100')

    def test_personalize_recommendations_resolver(self):
        orig = botocore.client.BaseClient._make_api_call

        def mock_make_api_call(self, operation_name, kwarg):
            if operation_name == 'GetRecommendations':
                parsed_response = {'itemList': [{'itemId': '1'}, {'itemId': '2'}]}
                return parsed_response
            return orig(self, operation_name, kwarg)

        with patch('botocore.client.BaseClient._make_api_call', new=mock_make_api_call):
            resolver = ResolverFactory.get(ResolverFactory.TYPE_PERSONALIZE_RECOMMENDATIONS, campaign_arn = 'my_campaign_arn')
            items = resolver.get_items(user_id = '12', product_id = '40', num_results = 20)
            self.assertEqual(len(items), 2)
            self.assertEqual(items[0]['itemId'], '1')
            self.assertEqual(items[1]['itemId'], '2')

    def test_personalize_ranking_resolver(self):
        orig = botocore.client.BaseClient._make_api_call

        def mock_make_api_call(self, operation_name, kwarg):
            if operation_name == 'GetPersonalizedRanking':
                parsed_response = {'personalizedRanking': [{'itemId': '4'}, {'itemId': '3'}, {'itemId': '2'}, {'itemId': '1'}]}
                return parsed_response
            return orig(self, operation_name, kwarg)

        with patch('botocore.client.BaseClient._make_api_call', new=mock_make_api_call):
            resolver = ResolverFactory.get(ResolverFactory.TYPE_PERSONALIZE_RANKING, campaign_arn = 'my_campaign_arn')
            unranked_items = [ '1', '2', '3', '4' ]
            ranked_items = resolver.get_items(user_id = '12', product_list = unranked_items)
            self.assertEqual(len(ranked_items), 4)
            self.assertEqual(ranked_items[0]['itemId'], '4')
            self.assertEqual(ranked_items[1]['itemId'], '3')
            self.assertEqual(ranked_items[2]['itemId'], '2')
            self.assertEqual(ranked_items[3]['itemId'], '1')

    def test_ranking_noop_resolver(self):
        resolver = ResolverFactory.get(ResolverFactory.TYPE_RANKING_NO_OP)
        unranked_items = [ '1', '2', '3', '4' ]
        ranked_items = resolver.get_items(product_list = unranked_items)
        self.assertEqual(len(ranked_items), 4)
        self.assertEqual(ranked_items[0]['itemId'], '1')
        self.assertEqual(ranked_items[1]['itemId'], '2')
        self.assertEqual(ranked_items[2]['itemId'], '3')
        self.assertEqual(ranked_items[3]['itemId'], '4')


if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR)
    unittest.main()