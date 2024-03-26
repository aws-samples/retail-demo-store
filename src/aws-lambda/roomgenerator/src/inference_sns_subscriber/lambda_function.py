import json
import boto3
import os
from botocore.exceptions import ClientError
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.data_classes import event_source, SNSEvent
from room_generator.db import RoomGenerationRequests

sf_client = boto3.client('stepfunctions')
dynamodb = boto3.resource('dynamodb')

dynamodb = boto3.resource('dynamodb')
db = RoomGenerationRequests(dynamodb.Table(os.environ['DYNAMODB_TABLE_NAME']))

logger = Logger(utc=True)

def resume_sfn(message: str) -> None:
    message = json.loads(message)
    inference_id = message["inferenceId"]
    output_location = message["responseParameters"]["outputLocation"]
    
    room_request = db.get(inference_id, attrs="task_token")
    
    response = {
        "id": inference_id,
        "output_location": output_location
    }
    try:
        sf_client.send_task_success(
            taskToken=room_request["task_token"],
            output=json.dumps(response)
        )
    except ClientError as error:
        if error.response['Error']['Code'] in ['TaskDoesNotExist', 'InvalidToken', 'TaskTimedOut']:
            logger.warning(f"Unable to resume step function for: {inference_id}. Potentially a duplicate, therefore ignoring.", exc_info=error)

@event_source(data_class=SNSEvent)
def lambda_handler(event: SNSEvent, context):
    for record in event.records:
        resume_sfn(record.sns.message)