# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import os

from optimizely import optimizely

from . import experiment, resolvers


optimizely_sdk = optimizely.Optimizely(sdk_key=os.environ.get('OPTIMIZELY_SDK_KEY'))


class OptimizelyFeatureTest(experiment.Experiment):
    def get_items(self, user_id, current_item_id = None, item_list = None, num_results = 10, tracker = None):
        assert user_id, "`user_id` is required"

        # All the kwargs that are passed to ResolverFactory.get will be stored as a JSON feature variable.
        resolver_init_kwargs = optimizely_sdk.get_feature_variable_json(self.feature, 'resolver_init_kwargs',
                                                                        user_id=user_id)
        resolver = resolvers.ResolverFactory.get(**resolver_init_kwargs)

        items = resolver.get_items(user_id=user_id,
                                   product_id=current_item_id,
                                   product_list=item_list,
                                   num_results=num_results)

        config = optimizely_sdk.get_optimizely_config()

        assert self.feature in config.features_map, f'Feature {self.feature} is not set up properly on Optimizely'
        feature = config.features_map[self.feature]

        assert feature.experiments_map.keys() > 0, "No feature tests have been set up for this feature"
        experiment_key = list(feature.experiments_map.keys())[0]

        variation_key = optimizely_sdk.get_variation(experiment_key, user_id)

        for rank, item in enumerate(items, 1):
            correlation_id = self._create_correlation_id(user_id, variation_key, rank)
            item['experiment'] = {'type': 'optimizely',
                                  'feature': self.feature,
                                  'name': experiment_key,
                                  'experiment_key': experiment_key,
                                  'variationIndex': variation_key,
                                  'revision_number': config.revision,
                                  'correlationId': correlation_id}
        return items
