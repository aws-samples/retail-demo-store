# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import os
from datetime import datetime
from . import experiment, resolvers
import requests
import logging

amplitude_rec_id = os.environ.get('AMPLITUDE_RECOMMENDATION_ID', 'NONE')
amplitude_secret_key = os.environ.get('AMPLITUDE_SECRET_API_KEY', 'NONE')
amplitude_configured =  amplitude_rec_id != 'NONE' and amplitude_secret_key != 'NONE'

class AmplitudeFeatureTest(experiment.Experiment):
    def get_items(self, user_id, current_item_id=None, item_list=None, num_results=10, tracker=None, filter_values=None, context=None, timestamp: datetime = None):
        assert user_id, "`user_id` is required"

        # Call Amplitude
        # If user is in control, get DefaultResolver (featrued products)
        # else recommend the amplitude ones as this user get the treatment in the experiment

        algorithm_config = {}
        resolver = resolvers.ResolverFactory.get(type=resolvers.ResolverFactory.TYPE_PRODUCT, **algorithm_config)

        items = resolver.get_items(user_id=user_id,
                                    product_id=current_item_id,
                                    product_list=item_list,
                                    num_results=num_results,
                                    filter_values=filter_values,
                                    context=context)

        print(f'******************** Amp Resolver Items: {items}')

        response = requests.get('https://profile-api.amplitude.com/v1/userprofile', 
            headers={'Authorization': f'Api-Key {amplitude_secret_key}'},
            params={'user_id': f'{user_id}', 'rec_id': amplitude_rec_id})

        print(f'********************* Amplitude Items: {response.content}')

        self.feature = 'home_product_recs' # Only for the home page for this workshop

        for rank, item in enumerate(items, 1):
            correlation_id = self._create_correlation_id(user_id, 0, rank)

            item_experiment = {
                'id': self.id,
                'feature': self.feature,
                'name': self.name,
                'type': self.type,
                'variationIndex': 0,
                'resultRank': rank,
                'correlationId': correlation_id
            }

            item.update({
                'experiment': item_experiment
            })

            rank += 1

            #correlation_id = self._create_correlation_id(user_id, variation_key, rank)
            # item['experiment'] = {'type': 'amplitude',
            #                       'feature': self.feature,
            #                       'name': f'Amplitude {amplitude_rec_id}'}
        return items

    def track_conversion(self, correlation_id: str, timestamp: datetime = datetime.now()):
        """ Conversion tracking is handled by the Optimizely client library """
        pass