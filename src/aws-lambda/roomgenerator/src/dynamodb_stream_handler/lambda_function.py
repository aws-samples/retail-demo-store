import json
import os
from typing import Any
import boto3
from botocore.exceptions import ClientError
from aws_lambda_powertools.utilities.data_classes import event_source, DynamoDBStreamEvent
from aws_lambda_powertools import Logger

sfn_client = boto3.client('stepfunctions')
logger = Logger()
state_machine_arn = os.environ['STATE_MACHINE_ARN']

@event_source(data_class=DynamoDBStreamEvent)
def lambda_handler(event: DynamoDBStreamEvent, context) -> None:
    """
    Receives dynamodb stream events for INSERTs of image generation requests.
    Starts a step function for each request
    """
    logger.debug(event)
    for record in event.records:
        start_sfn(record.dynamodb.new_image)


def start_sfn(room_generation_request: dict[str, Any]) -> None:
    """Starts the execution of the Step Function to process the room generation request."""

    id = room_generation_request["id"]
    logger.info(f"Starting processing room generation request for: {id}")

    try:
        sfn_client.start_execution(
            stateMachineArn=state_machine_arn,
            name=id,
            input=json.dumps(room_generation_request)
        )
    except ClientError as error:
        if error.response['Error']['Code'] == 'ExecutionAlreadyExists':
            # There is no guarentee of exactly once delivery for a Lambda stream handler, so this may be a duplicate
            logger.warning(f"Step Function Execution already exists for: {id}, ignoring")
        else:
            logger.exception("Received a Client error")
            # Re-raise error. Lambda stream handler will be configured to retry a limited number of times
            raise error
