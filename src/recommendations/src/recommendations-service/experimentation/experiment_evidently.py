# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import boto3
import json
import logging
import os
from datetime import datetime
from typing import Dict, List
from . import experiment

log = logging.getLogger(__name__)

evidently = boto3.client('evidently')

EXPOSURE_METRIC_VALUE = 0.0000001
CONVERSION_METRIC_VALUE = 1.0000001

class EvidentlyExperiment(experiment.Experiment):
    """ Experiment implementation for a Amazon CloudWatch Evidently experiment """
    def __init__(self, **data):
        super().__init__(**data)
        self.variation_name = data.get('variation_name')
        self.project = data.get('project', os.environ.get('EVIDENTLY_PROJECT_NAME'))

    def get_items(self, user_id: str, current_item_id: str = None, item_list: List = None, num_results: int = 10, tracker=None, filter_values=None, context=None, timestamp: datetime = None, promotion: Dict = None):
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
            'filter_values': filter_values,
            'context': context,
            'promotion': promotion
        }

        items = variation.resolver.get_items(**resolve_params)

        # Inject experiment details into recommended item list.
        rank = 1
        for item in items:
            correlation_id = self._create_evidently_correlation_id(user_id)

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
        self._send_evidently_event(user_id, EXPOSURE_METRIC_VALUE, timestamp)

        return items

    def track_conversion(self, correlation_id: str, timestamp: datetime = datetime.now()):
        """ Call this method to track a conversion/outcome for an experiment """
        correlation_bits = correlation_id.split('~')
        user_id = correlation_bits[1]
        self._send_evidently_event(user_id, CONVERSION_METRIC_VALUE, timestamp)

    def _send_evidently_event(self, user_id: str, metric_value: float, timestamp: datetime = datetime.now()):
        # In case None is passed for timestamp
        timestamp = datetime.now() if not timestamp else timestamp

        # We convert the feature name from snake case to camel case for the metric value key.
        metric_name = f'{self._snake_to_camel_case(self.feature)}Clicked'

        response = evidently.put_project_events(
            project = self.project,
            events = [
                {
                    'type': 'aws.evidently.custom',
                    'timestamp': timestamp,
                    'data': json.dumps({
                        'details': {
                            metric_name: metric_value
                        },
                        'userDetails': {
                            'userId': str(user_id)
                        }
                    })
                }
            ]
        )
        log.debug(response)

    def _create_evidently_correlation_id(self, user_id: str) -> str:
        """ Returns an identifier representing a recommended item for an experiment """
        return f'evidently~{user_id}~{self.feature}'

    def _snake_to_camel_case(self, snake: str) -> str:
        """ Converts string in snake case to camel case """
        first, *others = snake.split('_')
        return ''.join([first.lower(), *map(str.title, others)])