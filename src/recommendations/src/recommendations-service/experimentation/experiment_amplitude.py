# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import os
from datetime import datetime
from . import experiment, resolvers
import requests
import logging

amplitude_rec_id = os.environ.get('AMPLITUDE_RECOMMENDATION_ID', 'NONE')
amplitude_secret_key = os.environ.get('AMPLITUDE_SECRET_KEY', 'NONE')
amplitude_configured =  amplitude_rec_id != 'NONE' and amplitude_secret_key != 'NONE'

log = logging.getLogger(__name__)

class AmplitudeFeatureTest(experiment.Experiment):
    def get_items(self, user_id, current_item_id=None, item_list=None, num_results=10, tracker=None, filter_values=None, context=None, timestamp: datetime = None):
        assert user_id, "`user_id` is required"

        # Call Amplitude
        # If user is in control, get DefaultResolver (featrued products)
        # else recommend the amplitude ones as this user get the treatment in the experiment

        # All the kwargs that are passed to ResolverFactory.get will be stored as a JSON feature variable.
        # algorithm_type = optimizely_sdk.get_feature_variable_string(self.feature, 'algorithm_type', user_id=user_id)
        # algorithm_config = optimizely_sdk.get_feature_variable_json(self.feature, 'algorithm_config', user_id=user_id)
        # resolver = resolvers.ResolverFactory.get(type=algorithm_type, **algorithm_config)

        # items = resolver.get_items(user_id=user_id,
        #                            product_id=current_item_id,
        #                            product_list=item_list,
        #                            num_results=num_results,
        #                            filter_values=filter_values,
        #                            context=context)

        response = requests.get('https://profile-api.amplitude.com', 
            headers={'Authorization': f'Api-Key ${amplitude_secret_key}'})

        log.info(f'${response}')

        feature = 'home_product_recs' # Only for the home page for this workshop

        for rank, item in enumerate(items, 1):
            correlation_id = self._create_correlation_id(user_id, variation_key, rank)
            item['experiment'] = {'type': 'amplitude',
                                  'feature': self.feature,
                                  'name': experiment_key,
                                  'experiment_key': experiment_key,
                                  'variationIndex': variation_key,
                                  'revision_number': config.revision,
                                  'correlationId': correlation_id}
        return items

    def track_conversion(self, correlation_id: str, timestamp: datetime = datetime.now()):
        """ Conversion tracking is handled by the Optimizely client library """
        pass