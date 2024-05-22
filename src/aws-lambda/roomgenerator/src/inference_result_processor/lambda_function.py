import json
import boto3
import base64
import os
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools import Logger, Metrics
from urllib.parse import urlparse
from room_generator.db import RoomGenerationRequests
from room_generator.image_analyzer import ImageAnalyzer

image_bucket = os.environ['INPUT_IMAGE_BUCKET']

logger = Logger(utc=True)
metrics = Metrics()

s3_client = boto3.client('s3')
image_analyzer = ImageAnalyzer(
                    opensearch_hosts=[{'host': os.environ['OPENSEARCH_DOMAIN_HOST'], 'port': os.environ.get('OPENSEARCH_DOMAIN_PORT', 443)}],
                    opensearch_index_name=os.environ['OPENSEARCH_INDEX_NAME'], 
                    logger=logger)
dynamodb = boto3.resource('dynamodb')
db = RoomGenerationRequests(dynamodb.Table(os.environ['DYNAMODB_TABLE_NAME']))

@metrics.log_metrics(capture_cold_start_metric=True)
def lambda_handler(event, context: LambdaContext) -> dict:
    id = event["id"]
    output_location = event["output_location"]
    
    _, image_key, thumbnail_image_key = fetch_and_store_image(id, output_location)
    db.update(id, state='Re-Analyzing', final_image_key=image_key, thumbnail_image_key=thumbnail_image_key)

    labelled_furniture = image_analyzer.get_labelled_furniture(image_bucket, image_key)
    db.update(id, state='Done', labels=labelled_furniture)

    return {
        'image_bucket': image_bucket,
        'final_image_key': image_key,
        'thumbnail_image_key': thumbnail_image_key
    }

def fetch_and_store_image(id: str, output_location: str) -> tuple[str, str]:
    o = urlparse(output_location)
    bucket = o.netloc
    key = o.path.lstrip('/')

    inference_response = s3_client.get_object(Bucket=bucket, Key=key)
    result = inference_response["Body"].read().decode('utf-8')
    payload = json.loads(result) 
    image: bytes = [base64.b64decode(image) for image in payload["generated_images"]][0]

    room_request = db.get(id, "image_prefix")
    image_key = f"{room_request['image_prefix']}{id}_final.jpg"
    thumbnail_image_key = f"{room_request['image_prefix']}{id}_small.png"

    thumbnail_image = image_analyzer.resize_image(image, (128,128))

    s3_client.put_object(Bucket=image_bucket, ContentType="image/jpeg", Key=image_key, Body=image)
    s3_client.put_object(Bucket=image_bucket, ContentType="image/png", Key=thumbnail_image_key, Body=thumbnail_image)

    return image_bucket, image_key, thumbnail_image_key