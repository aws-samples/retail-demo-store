import os
from dataclasses import dataclass, asdict
from typing import Any
from aws_lambda_powertools import Logger, Metrics
from aws_lambda_powertools.utilities.typing import LambdaContext
from room_generator.db import RoomGenerationRequests
from room_generator.image_analyzer import ImageAnalyzer
from prompt import create_approximate_prompt
import boto3

input_image_bucket = os.environ['INPUT_IMAGE_BUCKET']

logger = Logger(utc=True)
metrics = Metrics()

image_analyzer = ImageAnalyzer(
                    opensearch_hosts=[{'host': os.environ['OPENSEARCH_DOMAIN_HOST'], 'port': os.environ.get('OPENSEARCH_DOMAIN_PORT', 443)}],
                    opensearch_index_name=os.environ['OPENSEARCH_INDEX_NAME'], 
                    logger=logger)
dynamodb = boto3.resource('dynamodb')
db = RoomGenerationRequests(dynamodb.Table(os.environ['DYNAMODB_TABLE_NAME']))

@dataclass
class RoomGenerationRequest:
    id: str
    room_style: str
    image_prefix: str
    image_key: str

@metrics.log_metrics(capture_cold_start_metric=True)
def lambda_handler(event: dict[str, Any], context: LambdaContext) -> dict:
    request = RoomGenerationRequest(event["id"], event['room_style'], event["image_prefix"], event["image_key"])
    
    labelled_furniture = image_analyzer.get_labelled_furniture(input_image_bucket, request.image_key)
    prompt = create_approximate_prompt(request.room_style, labelled_furniture)
    
    db.update(request.id, labels=labelled_furniture, prompt=prompt, state='Analyzing')

    response = asdict(request)
    response['prompt'] = prompt
    return response