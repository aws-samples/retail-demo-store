# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import logging

from datetime import datetime
from typing import Dict
from botocore.exceptions import ClientError
from abc import ABC, abstractmethod
from experimentation.resolvers import ResolverFactory

log = logging.getLogger(__name__)

class Variation:
    def __init__(self, **data):
        self.config = data
        self.resolver = ResolverFactory.get(**data)

class Experiment(ABC):
    """ Base class for all experiment types """

    def __init__(self, **data):
        self.id = data['id']
        self.feature = data['feature']
        self.name = data['name']
        self.status = data['status']
        self.type = data['type']

        self.variations = []

        for v in data['variations']:
            self.variations.append(Variation(**v))

    @abstractmethod
    def get_items(self, user_id, current_item_id=None, item_list=None, num_results=10, tracker=None, filter_values = None, context = None, timestamp: datetime = None, promotion: Dict = None):
        """ For a given user, returns item recommendations for this experiment along with experiment tracking/correlation information """
        pass

    @abstractmethod
    def track_conversion(self, correlation_id: str, timestamp: datetime) -> int:
        """ Call this method to track a conversion/outcome for an experiment """
        pass

    def _create_correlation_id(self, user_id: str, variation_index: int, result_rank: int) -> str:
        """ Returns an identifier representing a recommended item for an experiment """
        return f'{self.id}~{user_id}~{variation_index}~{result_rank}'

    def _getClassName(self):
        return self.__class__.__name__

class BuiltInExperiment(Experiment):
    """ Base class for all built-in experiment types """

    def __init__(self, table, **data):
        super().__init__(**data)
        self._table = table

    def track_conversion(self, correlation_id: str, timestamp: datetime) -> int:
        """ Call this method to track a conversion/outcome for an experiment """
        correlation_bits = correlation_id.split('~')
        user_id = correlation_bits[1]
        variation_index = int(correlation_bits[2])
        result_rank = int(correlation_bits[3])

        if variation_index < 0 or variation_index >= len(self.variations):
            raise Exception('variation_index is out of bounds')

        log.debug(f'Incrementing conversion count for variation {variation_index}, rank {result_rank}, based on user {user_id}')

        return self._increment_convert_count(variation_index)

    def _increment_exposure_count(self, variation: int, count: int = 1) -> int:
        """ Call this method when a user is exposed to a variation of an experiment """
        return self.__increment_variation_count('exposures', variation, count)

    def _increment_convert_count(self, variation: int, count: int = 1) -> int:
        """ Call this method when a user converts for a variation of an experiment """
        return self.__increment_variation_count('conversions', variation, count)

    def __increment_variation_count(self, field_name: str, variation: int, count: int = 1) -> int:
        try:
            response = self._table.update_item(
                Key={'id': self.id},
                UpdateExpression=f'SET variations[{variation}].{field_name} = variations[{variation}].{field_name} + :incr',
                ExpressionAttributeValues={
                    ':incr': count
                },
                ReturnValues='UPDATED_NEW'
            )
            return int(response['Attributes']['variations'][0][field_name])
        except ClientError as e:
            if e.response['Error']['Code'] == 'ValidationException':
                response = self._table.update_item(
                    Key={'id': self.id},
                    UpdateExpression=f'SET variations[{variation}].{field_name} = :incr',
                    ExpressionAttributeValues={
                        ':incr': count
                    },
                    ReturnValues='UPDATED_NEW'
                )
                return int(response['Attributes']['variations'][0][field_name])
            else:
                raise e