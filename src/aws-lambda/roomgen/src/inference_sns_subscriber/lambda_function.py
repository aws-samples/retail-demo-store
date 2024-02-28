import json
import boto3
import os
from aws_lambda_powertools.utilities.data_classes import event_source, SNSEvent

sf_client = boto3.client('stepfunctions')
dynamodb = boto3.resource('dynamodb')

table_name = os.environ.get('DYNAMODB_TABLE_NAME', 'photo')
table = dynamodb.Table(table_name)

@event_source(data_class=SNSEvent)
def lambda_handler(event: SNSEvent, context):
    
    for record in event.records:
        message = json.loads(record.sns.message)
        inference_id = message["inferenceId"]
        output_location = message["responseParameters"]["outputLocation"]
        
        item = table.get_item(
            Key={
                'id': inference_id
            },
            ProjectionExpression="task_token"
        )
        task_token = item["Item"]["task_token"]
        
        response = {
            "id": inference_id,
            "output_location": output_location
        }
        # Catch any exception.
        # What happens if this is a duplicate -> Catch Task does not exist error
        sf_client.send_task_success(
            taskToken=task_token,
            output=json.dumps(response)
        )