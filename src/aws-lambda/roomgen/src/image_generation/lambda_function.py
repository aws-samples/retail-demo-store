import boto3
import json
import os
from aws_lambda_powertools import Logger

s3_client = boto3.client('s3')
sagemaker_client = boto3.client('sagemaker-runtime')
dynamodb_client = boto3.client('dynamodb')

input_image_bucket = os.environ['INPUT_IMAGE_BUCKET']
endpoint_name = os.environ.get('ENDPOINT_NAME', 'controlnet-depth-sdxl')
table_name = os.environ.get('DYNAMODB_TABLE_NAME', 'photo')

logger = Logger(service="roomgen-image-generator")

NEGATIVE_PROMPT =  "Avoid monochrome, pixelation, clutter, distorted proportions, and low-detail textures."


def lambda_handler(event: dict, context) -> dict:
    event_payload = event["input"]

    id = event_payload["id"]
    image_prefix = event_payload["image_prefix"]
    image_key = event_payload["image_key"]
    prompt = event_payload["prompt"]
    task_token = event['token']

    logger.info(f"Processing image id: {image_key}")

    input_data = {}
    input_data["prompt"] = prompt
    input_data["steps"] = 15
    input_data["guidance_scale"] = 2.5
    input_data["controlnet_conditioning_scale"] = 0.5
    input_data["cross_attention_scale"] = 1.2
    input_data["negative_prompt"] = NEGATIVE_PROMPT
    input_data["init_image_s3"] = {
        "Bucket": input_image_bucket,
        "Key": image_key
    }

    input_location_key = f"{image_prefix}{id}"
    s3_client.put_object(Bucket=input_image_bucket, ContentType="application/json", Key=input_location_key, Body=json.dumps(input_data))

    # handle any errors
    response = sagemaker_client.invoke_endpoint_async(
        EndpointName=endpoint_name, 
        InferenceId=id,
        ContentType="application/json", 
        InputLocation=f"s3://{input_image_bucket}/{input_location_key}"
    )
    update_db(id, task_token, 'Generating')
    
    return {
        "output_location": response['OutputLocation']
    }

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
        UpdateExpression='SET task_token = :task_token, room_state = :status')