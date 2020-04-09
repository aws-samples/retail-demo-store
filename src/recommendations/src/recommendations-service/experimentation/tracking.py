# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
import boto3

from abc import ABC, abstractmethod
from experimentation.utils import CompatEncoder

kinesis = boto3.client('kinesis')

class Tracker(ABC):
    """ Base class for tracking detailed exposure and outcome/conversion events """
    @abstractmethod
    def log_exposure(self, event):
        pass

    @abstractmethod
    def log_outcome(self, event):
        pass

class KinesisTracker(Tracker):
    """ Tracker that writes exposure and outcome events to Kinesis streams

    Using Kinesis for capturing exposure and outcome events has a minimal 
    impact on experiment performance while providing flexibility in 
    analyzing experiment results. For example, Kinesis Firehose can be used
    with the Kinesis stream to asynchronously write experiment events to 
    S3 or Elasticsearch. Then experiment results can be analyzed directly 
    in Elasticsearch or processed from S3 using tools such as AWS Glue, 
    Athena, or EMR.
    """
    def __init__(self, exposure_stream_name, outcome_stream_name):
        self.exposure_stream_name = exposure_stream_name
        self.outcome_stream_name = outcome_stream_name

    def log_exposure(self, event):
        user_id = event['attributes']['user_id']
        experiment_name = event['attributes']['experiment']['name']

        kinesis.put_record(
            StreamName=self.exposure_stream_name,
            Data=json.dumps(event, cls=CompatEncoder),
            PartitionKey=f'{experiment_name}{user_id}'
        )

    def log_outcome(self, event):
        user_id = event['attributes']['user_id']
        experiment_name = event['attributes']['experiment']['name']

        kinesis.put_record(
            StreamName=self.outcome_stream_name,
            Data=json.dumps(event, cls=CompatEncoder),
            PartitionKey=f'{experiment_name}{user_id}'
        )
    