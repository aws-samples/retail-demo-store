# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import boto3
import logging
from datetime import datetime

from . import experiment

log = logging.getLogger(__name__)

evidently = boto3.client('evidently')

EXPOSURE_METRIC_VALUE = 0.0000001
CONVERSION_METRIC_VALUE = 1.0000001

class EvidentlyExperiment(experiment.Experiment):
    def __init__(self, **data):
        super().__init__(None, data)
        self.variation_name = data['variation_name']
        self.project = data['project']

    def get_items(self, user_id, current_item_id=None, item_list=None, num_results=10, tracker=None, context=None):
        if not user_id:
            raise Exception('user_id is required')
        if len(self.variations) != 1:
            raise Exception(f'Experiment {self.id} does not have a single pre-resolved variation')

        variation = self.variations[0]

        resolve_params = {
            'user_id': user_id,
            'product_id': current_item_id,
            'product_list': item_list,
            'num_results': num_results,
            'context': context
        }

        items = variation.resolver.get_items(**resolve_params)

        # Inject experiment details into recommended item list.
        rank = 1
        for item in items:
            correlation_id = self._create_correlation_id(user_id, self.variation_name, rank)

            item_experiment = {
                'id': self.id,
                'feature': self.feature,
                'name': self.name,
                'type': self.type,
                'variationIndex': self.variation_name,
                'resultRank': rank,
                'correlationId': correlation_id
            }

            item.update({
                'experiment': item_experiment
            })

            rank += 1

        # Log exposure with Evidently
        self._send_evidently_event(user_id, EXPOSURE_METRIC_VALUE)

        return items

    def track_conversion(self, user_id, variation_index, result_rank):
        """ Call this method to track a conversion/outcome for an experiment """
        self._send_evidently_event(user_id, CONVERSION_METRIC_VALUE)

    def _send_evidently_event(self, user_id: str, metric_value: float):
        metric_name = f'{self._snake_to_camel_case(self.feature)}Clicked'
        response = evidently.put_project_events(
            project = self.project,
            events = [
                {
                    'type': 'aws.evidently.custom',
                    'timestamp': datetime.now(),
                    'data': {
                        'details': {
                            metric_name: metric_value
                        },
                        'userDetails': {
                            'userId': user_id
                        }
                    }
                }
            ]
        )
        log.debug(response)

    def _snake_to_camel_case(self, snake: str) -> str:
        first, *others = snake.split('_')
        return ''.join([first.lower(), *map(str.title, others)])