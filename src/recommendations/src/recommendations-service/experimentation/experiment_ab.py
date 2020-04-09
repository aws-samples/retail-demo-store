# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import time
import hashlib
import logging

from experimentation.experiment import Experiment, Variation
from experimentation.tracking import Tracker

log = logging.getLogger(__name__)

class ABExperiment(Experiment):
    """ Implements a traditional A/B/n test across 2 or more variations where users are randomly and consistently partitioned across n groups """

    def __init__(self, table, **data):
        super(ABExperiment, self).__init__(table, **data)

    def get_items(self, user_id, current_item_id = None, item_list = None, num_results = 10, tracker = None):
        if not user_id:
            raise Exception('user_id is required')
        if len(self.variations) < 2:
            raise Exception(f'Experiment {self.id} does not have 2 or more variations')

        # Determine which variation to use for the user.
        variation_idx = self.calculate_variation_index(user_id)
        log.debug(f'{self._getClassName()} - assigned user {user_id} to variation {variation_idx} for experiment {self.feature}.{self.name}')

        # Increment exposure counter for variation for this experiment.
        self._increment_exposure_count(variation_idx)

        # Get item recommendations from the variation's resolver.
        variation = self.variations[variation_idx]

        resolve_params = {
            'user_id': user_id,
            'product_id': current_item_id,
            'product_list': item_list,
            'num_results': num_results
        }
        items = variation.resolver.get_items(**resolve_params)

        # Inject experiment details into recommended item list.
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
                    'variation_index': variation_idx,
                    'variation': variation.config
                }
            }

            tracker.log_exposure(event)

        return items

    def calculate_variation_index(self, user_id):
        """ Given a user_id and this experiment's configuration, return the variation

        The same variation will be returned for given user for this experiment no 
        matter how many times this method is called.
        """
        if len(self.variations) == 0:
            return -1

        hash_str = f'experiments.{self.feature}.{self.name}.{user_id}'.encode('ascii')
        hash_int = int(hashlib.sha1(hash_str).hexdigest()[:15], 16)
        index = hash_int % len(self.variations)

        return index
