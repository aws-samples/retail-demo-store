import boto3
import json
import os
from typing import Any
from aws_lambda_powertools import Logger, Metrics
from aws_lambda_powertools.utilities.typing import LambdaContext

s3_client = boto3.client('s3')
sagemaker_client = boto3.client('sagemaker-runtime')
dynamodb_client = boto3.client('dynamodb')

input_image_bucket = os.environ['INPUT_IMAGE_BUCKET']
inference_input_bucket = os.environ['INFERENCE_INPUT_BUCKET']
endpoint_name = os.environ.get('ENDPOINT_NAME', 'controlnet-depth-sdxl')
table_name = os.environ['DYNAMODB_TABLE_NAME']

logger = Logger(utc=True)
metrics = Metrics()

NEGATIVE_PROMPT =  "Avoid monochrome, pixelation, clutter, distorted proportions, and low-detail textures."
INFERENCE_INPUT_S3_PREFIX = "async_inference/input/"

@metrics.log_metrics(capture_cold_start_metric=True)
def lambda_handler(event: dict[str, Any], context: LambdaContext) -> dict[str, Any]:

    response = invoke_async_endpoint(event)
    return {
        "output_location": response['OutputLocation']
    }

def invoke_async_endpoint(event: dict[str, Any]) -> dict[str,Any]:
    event_payload = event["input"]
    id = event_payload["id"]
    logger.info(f"Processing image id: {event_payload["image_key"]}")

    input_data = {}
    input_data["prompt"] = event_payload["prompt"]
    input_data["steps"] = 8
    input_data["strength"] = 0.9
    input_data["guidance_scale"] = 8
    input_data["controlnet_conditioning_scale"] = 0.35
    input_data["cross_attention_scale"] = 1.0
    input_data["negative_prompt"] = NEGATIVE_PROMPT
    input_data["init_image_s3"] = {
        "Bucket": input_image_bucket,
        "Key": event_payload["image_key"]
    }
    
    inference_input_s3_key = f"{INFERENCE_INPUT_S3_PREFIX}{id}"
    s3_client.put_object(Bucket=inference_input_bucket, ContentType="application/json", Key=inference_input_s3_key, Body=json.dumps(input_data))

    update_db(id, event['token'], 'Generating')
    # handle any errors
    response = sagemaker_client.invoke_endpoint_async(
        EndpointName=endpoint_name, 
        InferenceId=id,
        ContentType="application/json", 
        InputLocation=f"s3://{inference_input_bucket}/{inference_input_s3_key}"
    )
    
    return response

def update_db(id: str, task_token: str, status: str) -> None:
    dynamodb_client.update_item(
        TableName=table_name, 
        Key={
            'id': {
                'S': id
            }
        },
        ExpressionAttributeValues={
            ':task_token': {'S': task_token},
            ':state': {'S' : status}
        },
        UpdateExpression='SET task_token = :task_token, room_state = :state')