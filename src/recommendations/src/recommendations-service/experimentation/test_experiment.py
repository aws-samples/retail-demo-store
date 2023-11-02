# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import unittest
import uuid
import json

from experimentation.resolvers import ResolverFactory, PersonalizeRecommendationsResolver, DefaultProductResolver
from experimentation.experiment_ab import ABExperiment
from experimentation.experiment_interleaving import InterleavingExperiment
from experimentation.experiment_evidently import EvidentlyExperiment

"""
python -m unittest experimentation/test_experiment.py
"""

class TestExperiments(unittest.TestCase):
    def test_ab_experiment(self):
        exp_config = {
            'id': uuid.uuid4().hex,
            'feature': 'test-feature',
            'name': 'test-ab-experiment',
            'type': 'ab',
            'status': 'ACTIVE',
            'variations': [{
                'type': ResolverFactory.TYPE_PERSONALIZE_RECOMMENDATIONS,
                'inference_arn': 'arn:aws:personalize:us-east-1:123456789:campaign/some_name'
            },{
                'type': ResolverFactory.TYPE_PRODUCT,
                'products_service_host': '10.10.10.10'
            }]
        }

        experiment = ABExperiment('ExperimentStrategy', **exp_config)

        self.assertEqual(experiment.id, exp_config['id'])
        self.assertEqual(experiment.feature, exp_config['feature'])
        self.assertEqual(experiment.name, exp_config['name'])
        self.assertEqual(experiment.status, exp_config['status'])

        self.assertEqual(len(experiment.variations), 2)
        self.assertTrue(type(experiment.variations[0].resolver) is PersonalizeRecommendationsResolver)
        self.assertTrue(type(experiment.variations[1].resolver) is DefaultProductResolver)

    def test_interleaved_balanced(self):
        exp_config = {
            'id': uuid.uuid4().hex,
            'feature': 'test-feature',
            'name': 'test-interleaved-experiment',
            'type': 'interleaving',
            'status': 'ACTIVE',
            'method': InterleavingExperiment.METHOD_BALANCED,
            'variations': [{
                'type': ResolverFactory.TYPE_PERSONALIZE_RECOMMENDATIONS,
                'inference_arn': 'arn:aws:personalize:us-east-1:123456789:recommender/some_name'
            },{
                'type': ResolverFactory.TYPE_PRODUCT,
                'products_service_host': '10.10.10.10'
            }]
        }

        experiment = InterleavingExperiment('ExperimentStrategy', **exp_config)

        self.assertEqual(experiment.method, exp_config['method'])

        list_of_item_lists = [[] for x in range(2)]
        list_of_item_lists[0] = [ {'itemId':'a'}, {'itemId':'b'}, {'itemId':'c'}, {'itemId':'d'}, {'itemId':'g'}, {'itemId':'h'}, {'itemId':'l'}, {'itemId':'m'}, {'itemId':'n'}]
        list_of_item_lists[1] = [ {'itemId':'b'}, {'itemId':'e'}, {'itemId':'a'}, {'itemId':'f'}, {'itemId':'g'}, {'itemId':'h'}, {'itemId':'x'}, {'itemId':'y'}, {'itemId':'z'}]

        results = experiment._interleave_balanced('12', list_of_item_lists, 5)
        #print(f'Interleaved results: {results}')

        self.assertEqual(len(results), 5)

    def test_interleaved_team_draft(self):
        exp_config = {
            'id': uuid.uuid4().hex,
            'feature': 'test-feature',
            'name': 'test-interleaved-experiment',
            'type': 'interleaving',
            'status': 'ACTIVE',
            'method': InterleavingExperiment.METHOD_TEAM_DRAFT,
            'variations': [{
                'type': ResolverFactory.TYPE_PERSONALIZE_RECOMMENDATIONS,
                'inference_arn': 'arn:aws:personalize:us-east-1:123456789:campaign/some_name'
            },{
                'type': ResolverFactory.TYPE_PRODUCT,
                'products_service_host': '10.10.10.10'
            }]
        }

        experiment = InterleavingExperiment('ExperimentStrategy', **exp_config)

        self.assertEqual(experiment.method, exp_config['method'])

        list_of_item_lists = [[] for x in range(2)]
        list_of_item_lists[0] = [ {'itemId':'a'}, {'itemId':'b'}, {'itemId':'c'}, {'itemId':'d'}, {'itemId':'g'}, {'itemId':'h'}, {'itemId':'l'}, {'itemId':'m'}, {'itemId':'n'}]
        list_of_item_lists[1] = [ {'itemId':'b'}, {'itemId':'e'}, {'itemId':'a'}, {'itemId':'f'}, {'itemId':'g'}, {'itemId':'h'}, {'itemId':'x'}, {'itemId':'y'}, {'itemId':'z'}]

        results = experiment._interleave_team_draft('12', list_of_item_lists, 5)
        #print(f'Interleaved results: {results}')

        self.assertEqual(len(results), 5)

    def test_evidently(self):
        feature = 'home_product_recs'
        eval_feature = {
            'details': {
                'experiment': feature
            },
            'entityId': '123-user',
            'feature': feature,
            'project': 'retaildemostore',
            'reason': 'EXPERIMENT_RULE_MATCH',
            'value': {
                'stringValue': '{"type":"personalize-recommendations","inference_arn":"arn:aws:personalize:us-east-1:123456789:recommender/retaildemostore-recommended-for-you"}'
            },
            'variation': 'Personalize-UserPersonalization'
        }

        variation_config = json.loads(eval_feature['value']['stringValue'])

        experiment_config = {
            'id': eval_feature['details']['experiment'],
            'name': eval_feature['details']['experiment'],
            'feature': feature,
            'project': eval_feature['project'],
            'status': 'ACTIVE',
            'type': 'evidently',
            'variations': [ variation_config ],
            'variation_name': eval_feature['variation']
        }

        experiment = EvidentlyExperiment(**experiment_config)
        self.assertEqual(experiment.id, eval_feature['details']['experiment'])
        self.assertEqual(experiment.feature, feature)
        self.assertEqual(experiment.name, eval_feature['details']['experiment'])
        self.assertEqual(experiment.status, 'ACTIVE')

        self.assertEqual(len(experiment.variations), 1)
        self.assertTrue(type(experiment.variations[0].resolver) is PersonalizeRecommendationsResolver)
