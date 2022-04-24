# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import boto3
import os
import json
import logging
from typing import Dict,List
from expiring_dict import ExpiringDict
from experimentation.features import FEATURE_NAMES
from experimentation.experiment_evidently import EvidentlyExperiment

log = logging.getLogger(__name__)

evidently = boto3.client('evidently')
# Cache feature evals for 30 seconds to balance latency and timeliness of picking up experiments
eval_features_by_user_cache = ExpiringDict(30)

project_name = os.environ['EVIDENTLY_PROJECT_NAME']

class EvidentlyFeatureResolver:
    """
    This class is used by ExperimentManager to determine if an Evidently experiment is active
    for a feature as well as for mapping a correlation ID to an EvidentlyExperiment instance for logging outcomes.
    """

    def evaluate_feature(self, user_id: str, feature: str) -> EvidentlyExperiment:
        """ Evaluates a storefront feature for a user
        An EvidentlyExperiment will be returned if there is an active Evidently experiment for the feature or
        None if an experiment is not active.
        """
        cache_key = user_id
        evaluated = eval_features_by_user_cache.get(cache_key)
        if evaluated is None:
            evaluated = self._call_evidently_evaluate_features(user_id)
            eval_features_by_user_cache[cache_key] = evaluated

            log.debug('Eval feature results for user/feature %s/%s: %s', user_id, feature, evaluated)
        else:
            log.debug('Found cached eval feature result for user/feature %s/%s: %s', user_id, feature, evaluated)

        experiment = None
        feature_found = False

        for eval_feature in evaluated:
            if eval_feature.get('feature').split('/')[-1] == feature:
                feature_found = True
                log.debug('Found matching feature in evaluated with reason %s', eval_feature.get('reason'))
                if eval_feature.get('reason') == 'EXPERIMENT_RULE_MATCH':
                    variation_config = json.loads(eval_feature['value']['stringValue'])
                    # Config convenience check allowing ARN to be expressed as 'arn' in Evidently feature.
                    if 'inference_arn' not in variation_config and 'arn' in variation_config:
                        variation_config['inference_arn'] = variation_config.pop('arn')

                    details = json.loads(eval_feature['details'])

                    experiment_config = {
                        'id': details['experiment'],
                        'name': details['experiment'],
                        'feature': feature,
                        'project': eval_feature['project'].split('/')[-1],
                        'status': 'ACTIVE',
                        'type': 'evidently',
                        'variations': [ variation_config ],
                        'variation_name': eval_feature['variation']
                    }

                    experiment = EvidentlyExperiment(**experiment_config)

                break

        if not feature_found:
            log.warning('Feature "%s" not found in Evidently for project "%s"', feature, project_name)

        return experiment

    def create_from_correlation_id(self, correlation_id: str) -> EvidentlyExperiment:
        """ Creates an EvidentlyExperiment given a correlation ID

        A correlation ID is created by EvidentlyExperiment for each recommended item that is part of an
        active experiment. This ID is used when logging outcomes/conversions to map back to an experiment.
        """
        id_bits = correlation_id.split('~')
        if id_bits[0] != 'evidently':
            raise Exception('Correlation ID does not appear to belong to an Evidently experiment')

        feature = id_bits[2]

        experiment_config = {
            'id': 'evidently',
            'name': 'Evidently Experiment',
            'feature': feature,
            'status': 'ACTIVE',
            'type': 'evidently',
            'variations': [ ],
        }

        return EvidentlyExperiment(**experiment_config)

    def _call_evidently_evaluate_features(self, user_id: str) -> List[Dict]:
        requests = []
        for feature in FEATURE_NAMES:
            requests.append({
                'entityId': user_id,
                'feature': feature
            })

        response = evidently.batch_evaluate_feature(
            project=project_name,
            requests=requests
        )

        return response['results']