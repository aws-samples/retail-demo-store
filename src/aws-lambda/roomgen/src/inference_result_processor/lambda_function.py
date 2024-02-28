import json
import boto3
import base64
import os
from urllib.parse import urlparse

s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

image_bucket = os.environ['INPUT_IMAGE_BUCKET']
table_name = os.environ.get('DYNAMODB_TABLE_NAME', 'photo')
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    id = event["id"]
    output_location = event["output_location"]
    
    o = urlparse(output_location)
    bucket = o.netloc
    key = o.path.lstrip('/')
    
    inference_response = s3_client.get_object(Bucket=bucket, Key=key)
    result = inference_response["Body"].read().decode('utf-8')
    
    payload = json.loads(result)
    
    decoded_images = [base64.b64decode(image) for image in payload["generated_images"]]

    item = table.get_item(
        Key={
            'id': id
        },
        ProjectionExpression="image_prefix"
    )

    image_prefix = item["Item"]['image_prefix']

    s3_client.put_object(Bucket=image_bucket, ContentType="image/jpeg", Key=f"{image_prefix}{id}_final.jpg", Body=decoded_images[0])

    table.update_item(
         Key={
            'id': id
        },
        ExpressionAttributeValues={
            ':state': 'Done',
            ':final_image_key': f"{image_prefix}{id}_final.jpg"
        },
        UpdateExpression='SET room_state = :state, final_image_key = :final_image_key'
    )