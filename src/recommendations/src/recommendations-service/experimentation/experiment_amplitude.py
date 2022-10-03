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

    def get_amplitude_items(self, user_id):
        uid = f'{user_id:0>5}' 
        response = requests.get('https://profile-api.amplitude.com/v1/userprofile', 
            headers={'Authorization': f'Api-Key {amplitude_secret_key}'},
            params={'user_id': uid, 'rec_id': amplitude_rec_id})
        res = response.json()
        items = []
        is_user_in_control_group = True
        if res:
            for item in res['userData']['recommendations'][0]['items']:
                items.append({'itemId': item})

            is_user_in_control_group = res['userData']['recommendations'][0]['is_control']

        return is_user_in_control_group, items

    def get_items(self, user_id, current_item_id=None, item_list=None, num_results=10, tracker=None, filter_values=None, context=None, timestamp: datetime = None):
        assert user_id, "`user_id` is required"

        is_control, items = self.get_amplitude_items(user_id)

        if is_control:  # This user is in the control group, show them most popular products        
            algorithm_config = {}
            resolver = resolvers.ResolverFactory.get(type=resolvers.ResolverFactory.TYPE_PRODUCT, **algorithm_config)

            items = resolver.get_items(user_id=user_id,
                                        product_id=current_item_id,
                                        product_list=item_list,
                                        num_results=num_results,
                                        filter_values=filter_values,
                                        context=context)

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