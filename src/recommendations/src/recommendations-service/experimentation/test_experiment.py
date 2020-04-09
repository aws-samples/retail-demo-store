# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import unittest
import json
import botocore
import uuid

from unittest.mock import patch
from experimentation.resolvers import ResolverFactory, Resolver, PersonalizeRecommendationsResolver, DefaultProductResolver
from experimentation.experiment import Variation
from experimentation.experiment_manager import ExperimentManager
from experimentation.experiment_ab import ABExperiment
from experimentation.experiment_interleaving import InterleavingExperiment
from experimentation.experiment_mab import MultiArmedBanditExperiment

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
                'campaign_arn': 'some_arn'
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
                'campaign_arn': 'some_arn'
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
                'campaign_arn': 'some_arn'
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
