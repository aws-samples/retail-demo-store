from urllib.parse import unquote_plus
from aws_lambda_powertools.utilities.data_classes import event_source, S3Event
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools import Logger
import boto3
from botocore.exceptions import ClientError
import json
import os

state_machine_arn = os.environ['STATE_MACHINE_ARN']

sf_client = boto3.client('stepfunctions')
logger = Logger(utc=True)

def start_sfn(payload: str) -> None:
    try:
        sf_client.start_execution(
            stateMachineArn=state_machine_arn,
            input=payload
        )
    except ClientError as error:
        logger.exception(f"Unable to start step function for: {payload}")
        raise error

@event_source(data_class=S3Event)
def lambda_handler(event: S3Event, context: LambdaContext) -> None:
    """
    S3 Lambda Event function.
    Triggered on creation of a new resized image
    Multiple records can be delivered in a single event
    Starts a Step function workflow for each image 
    """
    for record in event.records:
        start_sfn(json.dumps({
            "bucket": event.bucket_name,
            "key": unquote_plus(record.s3.get_object.key)
        }))