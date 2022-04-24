# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import boto3
import logging

from boto3.dynamodb.conditions import Key
from experimentation.experiment_ab import ABExperiment
from experimentation.experiment_interleaving import InterleavingExperiment
from experimentation.experiment_mab import MultiArmedBanditExperiment
from experimentation.evidently_feature_resolver import EvidentlyFeatureResolver
from experimentation.experiment_optimizely import OptimizelyFeatureTest, optimizely_sdk, optimizely_configured
from experimentation.tracking import KinesisTracker

log = logging.getLogger(__name__)

ssm = boto3.client('ssm')
dynamodb = boto3.resource('dynamodb')

class ExperimentManager:
    """ Provides access to retrieving active experiments for features """
    TYPE_AB = 'ab'
    TYPE_INTERLEAVING = 'interleaving'
    TYPE_MAB = 'mab'
    TYPE_EVIDENTLY = 'evidently'
    TYPE_OPTIMIZELY = 'optimizely'

    __table_name = None
    __experiments = {}

    @staticmethod
    def register_experiment(type, experiment):
        """ Registers an experiment implementation for the given type """
        ExperimentManager.__experiments[type] = experiment

    def is_configured(self):
        """ Returns True if this environment is setup for running experiments """
        return self.is_optimizely_configured() or self.__get_table()

    def is_optimizely_configured(self):
        return optimizely_configured

    def get_active(self, feature, user_id):
        """ Returns the active experiment for the given feature """
        # 1. If Optimizely is configured for this deployment, check for active Optimizely experiment.
        if self.is_optimizely_configured():
            config = optimizely_sdk.get_optimizely_config()
            if config:
                if feature in config.features_map:
                    optimizely_feature = config.features_map[feature]
                    experiment_keys = optimizely_feature.experiments_map.keys()
                    if len(experiment_keys) > 0:
                        experiment_key = list(experiment_keys)[0]
                        experiment = optimizely_feature.experiments_map[experiment_key]
                        data = {'id': experiment.id,
                                'feature': feature,
                                'name': experiment_key,
                                'status': 'ACTIVE',
                                'type': 'optimizely',
                                'variations': []}
                        return OptimizelyFeatureTest(**data)

        # 2. Check for active Evidently experiment.
        evidently_experiment = EvidentlyFeatureResolver().evaluate_feature(user_id, feature)
        if evidently_experiment:
            return evidently_experiment

        # 3. Lastly, check for an active built-in experiment.
        experiment = None

        table = self.__get_table()

        if table:
            log.debug(f'ExperimentManager - querying {table.table_name} for active experiments for {feature}')

            # Get active experiments for the feature.
            response = table.query(
                IndexName='feature-name-index',
                KeyConditionExpression=Key('feature').eq(feature),
                FilterExpression=Key('status').eq('ACTIVE')
            )

            experiment_count = response['Count']
            if experiment_count > 0:
                experiment_config = response['Items'][0]
                log.debug(f'ExperimentManager - {experiment_count} active experiments found for feature {feature}')

                experiment_type = experiment_config['type']
                experiment_class = ExperimentManager.__experiments.get(experiment_type)
                if not experiment_class:
                    raise ValueError(f'Experiment class for type {experiment_type} could not be found')
                experiment = experiment_class(table, **experiment_config)
            else:
                log.debug(f'ExperimentManager - no active experiments for feature {feature}')

        return experiment

    def get_by_correlation_id(self, correlation_id: str):
        """ Returns an experiment based on a correlation ID """
        id_bits = correlation_id.split('~')

        experiment_id = id_bits[0]
        if experiment_id == ExperimentManager.TYPE_EVIDENTLY:
            return EvidentlyFeatureResolver().create_from_correlation_id(correlation_id)

        return self.get_by_id(experiment_id)

    def get_by_id(self, id):
        """ Looks up a built-in experiment by its ID """
        table = self.__get_table()
        if not table:
            raise Exception('Experiment strategy table has not been configured')

        experiment = None

        response = table.get_item(Key={'id': id})
        if response.get('Item'):
            experiment_config = response['Item']
            experiment_type = experiment_config['type']
            experiment_class = ExperimentManager.__experiments.get(experiment_type)
            if not experiment_class:
                raise ValueError(f'Experiment class for type {experiment_type} could not be found')
            experiment = experiment_class(table, **experiment_config)

        return experiment

    def default_tracker(self):
        """ Creates a Kinesis stream tracker for an experiment if environment is
        configured with a Kinesis stream
        """
        tracker = None

        try:
            response = ssm.get_parameter(Name='retaildemostore-kinesis-event-stream-name')
            if response['Parameter']['Value'] != 'NONE':
                stream_name = response['Parameter']['Value']
                tracker = KinesisTracker(
                    exposure_stream_name = stream_name,
                    outcome_stream_name = stream_name
                )
        except ssm.exceptions.ParameterNotFound:
            pass

        return tracker

    def __get_table(self):
        """ Lazily initializes the DDB table name for experiment strategies """
        if ExperimentManager.__table_name is None:
            log.debug('ExperimentManager - looking up experiment strategy table name from SSM')
            response = ssm.get_parameter(Name='retaildemostore-experiment-strategy-table-name')

            if response['Parameter']['Value']:
                ExperimentManager.__table_name = response['Parameter']['Value']
            else:
                ExperimentManager.__table_name = 'NONE'

            log.debug(f'ExperimentManager - resolved experiment strategy table name to: {ExperimentManager.__table_name}')

        return dynamodb.Table(ExperimentManager.__table_name) if ExperimentManager.__table_name != 'NONE' else None

# Register built-in experiment types here only.
ExperimentManager.register_experiment(ExperimentManager.TYPE_AB, ABExperiment)
ExperimentManager.register_experiment(ExperimentManager.TYPE_INTERLEAVING, InterleavingExperiment)
ExperimentManager.register_experiment(ExperimentManager.TYPE_MAB, MultiArmedBanditExperiment)
