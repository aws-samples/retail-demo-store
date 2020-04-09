# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import numpy as np
import logging
import json
import time

from experimentation.experiment import Experiment

log = logging.getLogger(__name__)

class MultiArmedBanditExperiment(Experiment):
    """ Implementation of the multi-armed bandit problem using the Thompson Sampling approach 
    to exploring variations to identify and exploit the best performing variation
    """
    def __init__(self, table, **data):
        super(MultiArmedBanditExperiment, self).__init__(table, **data)

    def get_items(self, user_id, current_item_id = None, item_list = None, num_results = 10, tracker = None):
        if not user_id:
            raise Exception('user_id is required')
        if len(self.variations) < 2:
            raise Exception(f'Experiment {self.id} does not have 2 or more variations')

        # Determine the variation to use.
        variation_idx = self._select_variation_index()
        log.debug(f'{self._getClassName()} - assigned user {user_id} to variation {variation_idx} for experiment {self.feature}.{self.name}')

        # Increment exposure count for variation
        self._increment_exposure_count(variation_idx)

        # Fetch recommendations using the variation's resolver
        variation = self.variations[variation_idx]

        resolve_params = {
            'user_id': user_id,
            'product_id': current_item_id,
            'product_list': item_list,
            'num_results': num_results
        }
        items = variation.resolver.get_items(**resolve_params)

        # Inject experiment details into recommended items list
        rank = 1
        for item in items:
            correlation_id = self._create_correlation_id(user_id, variation_idx, rank)

            item_experiment = {
                'id': self.id,
                'feature': self.feature,
                'name': self.name,
                'type': self.type,
                'variationIndex': variation_idx,
                'resultRank': rank,
                'correlationId': correlation_id
            }

            item.update({ 
                'experiment': item_experiment
            })

            rank += 1

        if tracker is not None:
            # Track exposure details for analysis
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
                    'variation_index': variation_idx,
                    'variation': variation.config
                }
            }

            tracker.log_exposure(event)

        return items

    def _select_variation_index(self):
        """ Selects the variation using Thompson Sampling """
        variation_count = len(self.variations)
        exposures = np.zeros(variation_count)
        conversions = np.zeros(variation_count)

        for i in range(variation_count):
            variation = self.variations[i]
            exposures[i] = int(variation.config.get('exposures', 0))
            conversions[i] = int(variation.config.get('conversions', 0))

        # Sample from posterior (this is the Thompson Sampling approach)
        # This leads to more exploration because variations with > uncertainty can then be selected
        theta = np.random.beta(conversions + 1, exposures + 1)

        # Select variation index with highest posterior p of converting
        return np.argmax(theta)
