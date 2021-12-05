# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import time
import logging
from dataclasses import dataclass
from typing import Dict

from experimentation.experiment import Experiment

log = logging.getLogger(__name__)

@dataclass
class ExternalExperimentConfig:
    id: str
    feature: str
    name: str
    type: str
    variation_config: Dict[str,str]
    variation_index: int

class ExternalExperiment(Experiment):
    """ Externally managed experiment where the variation is provided to the experiment """

    def __init__(self, table, **data):
        super().__init__(table, **data)
        self.variation_index = data.get('variation_index', 0)

    def get_items(self, user_id, current_item_id=None, item_list=None, num_results=10, tracker=None, context=None):
        if not user_id:
            raise Exception('user_id is required')

        if len(self.variations) != 1:
            raise Exception(f'Experiment {self.id} should have exactly 1 variation')

        log.debug(f'{self._getClassName()} - assigned user {user_id} to variation {self.variation_index} for experiment {self.feature}.{self.name}')

        # Get item recommendations from the variation's resolver.
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
            correlation_id = self._create_correlation_id(user_id, self.variation_index, rank)

            item_experiment = {
                'id': self.id,
                'feature': self.feature,
                'name': self.name,
                'type': self.type,
                'variationIndex': self.variation_index,
                'resultRank': rank,
                'correlationId': correlation_id
            }

            item.update({
                'experiment': item_experiment
            })

            rank += 1

        if tracker is not None:
            # Detailed tracking of exposure.
            event = {
                'event_type': 'Experiment Exposure',
                'event_timestamp': int(round(time.time() * 1000)),
                'attributes': {
                    'user_id': user_id,
                    'experiment': {
                        'id': self.id,
                        'feature': self.feature,
                        'name': self.name,
                        'type': self.type
                    },
                    'variation_index': self.variation_index,
                    'variation': variation.config
                }
            }

            tracker.log_exposure(event)

        return items

    def _create_correlation_id(self, user_id, variation_index, result_rank):
        """ Returns an identifier representing a recommended item for an experiment """
        return f'{self.type}_{self.id}_{user_id}_{variation_index}_{result_rank}'
