import json
import boto3
import os
from botocore.exceptions import ClientError
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.data_classes import event_source, SNSEvent

sf_client = boto3.client('stepfunctions')
dynamodb = boto3.resource('dynamodb')

table_name = os.environ['DYNAMODB_TABLE_NAME']
table = dynamodb.Table(table_name)

logger = Logger(utc=True)

def resume_sfn(message: str) -> None:
    message = json.loads(message)
    inference_id = message["inferenceId"]
    output_location = message["responseParameters"]["outputLocation"]
    
    item = table.get_item(
        Key={
            'id': inference_id
        },
        ProjectionExpression="task_token"
    )["Item"]
    
    response = {
        "id": inference_id,
        "output_location": output_location
    }
    try:
        sf_client.send_task_success(
            taskToken=item["task_token"],
            output=json.dumps(response)
        )
    except ClientError as error:
        if error.response['Error']['Code'] in ['TaskDoesNotExist', 'InvalidToken', 'TaskTimedOut']:
            logger.warning(f"Unable to resume step function for: {inference_id}. Potentially a duplicate, therefore ignoring.", exc_info=error)

@event_source(data_class=SNSEvent)
def lambda_handler(event: SNSEvent, context):
    for record in event.records:
        resume_sfn(record.sns.message)