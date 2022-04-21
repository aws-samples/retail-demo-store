# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import boto3
import os
import json
from typing import Dict,List
from expiring_dict import ExpiringDict
from features import FEATURE_NAMES

from experimentation.experiment_evidently import EvidentlyExperiment

evidently = boto3.client('evidently')
eval_features_by_user_cache = ExpiringDict(60)   # 1 minute

project_arn = os.environ['EVIDENTLY_PROJECT_ARN']

RULE_MATCH = 'EXPERIMENT_RULE_MATCH'

class EvidentlyFeatureResolver:

    def evaluate_feature(self, user_id: str, feature: str) -> EvidentlyExperiment:
        evaluated = eval_features_by_user_cache.get(user_id)
        if evaluated is None:
            evaluated = self._call_evidently_evaluate_features(user_id)
            eval_features_by_user_cache[user_id] = evaluated

        experiment = None
        for eval_feature in evaluated:
            if eval_feature.get('feature') == feature:
                if eval_feature.get('reason') == RULE_MATCH:
                    experiment_config = {
                        'id': eval_feature['details']['experiment'],
                        'name': eval_feature['details']['experiment'],
                        'feature': feature,
                        'project': eval_feature['project'],
                        'status': 'ACTIVE',
                        'type': 'evidently',
                        'variations': [ json.loads(eval_feature['value']['stringValue']) ],
                        'variation_name': eval_feature['variation']
                    }

                    experiment = EvidentlyExperiment(None, **experiment_config)

                break

        return experiment

    def _call_evidently_evaluate_features(self, user_id: str) -> List[Dict]:
        requests = []
        for feature in FEATURE_NAMES:
            requests.append({
                'entityId': user_id,
                'feature': feature
            })

        response = evidently.batch_evaluate_feature(
            project=project_arn,
            requests=requests
        )

        return response['results']