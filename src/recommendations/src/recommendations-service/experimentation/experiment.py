# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import logging

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

    def __init__(self, table, **data):
        self._table = table
        self.id = data['id']
        self.feature = data['feature']
        self.name = data['name']
        self.status = data['status']
        self.type = data['type']

        self.variations = []

        for v in data['variations']:
            self.variations.append(Variation(**v))

    @abstractmethod
    def get_items(self, user_id, current_item_id = None, item_list = None, num_results = 10, tracker = None):
        """ For a given user, returns item recommendations for this experiment along with experiment tracking/correlation information """
        pass

    def track_conversion(self, user_id, variation_index, result_rank):
        """ Call this method to track a conversion/outcome for an experiment """
        if variation_index < 0 or variation_index >= len(self.variations):
            raise Exception('variation_index is out of bounds')

        log.debug(f'Incrementing conversion count for variation {variation_index}, rank {result_rank}, based on user {user_id}')

        return self._increment_convert_count(variation_index)

    def _increment_exposure_count(self, variation, count = 1):
        """ Call this method when a user is exposed to a variation of an experiment """
        return self.__increment_variation_count('exposures', variation, count)

    def _increment_convert_count(self, variation, count = 1):
        """ Call this method when a user converts for a variation of an experiment """
        return self.__increment_variation_count('conversions', variation, count)

    def __increment_variation_count(self, field_name, variation, count = 1):
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

    def _create_correlation_id(self, user_id, variation_index, result_rank):
        """ Returns an identifier representing a recommended item for an experiment """
        return f'{self.id}-{user_id}-{variation_index}-{result_rank}'

    def _getClassName(self):
        return self.__class__.__name__