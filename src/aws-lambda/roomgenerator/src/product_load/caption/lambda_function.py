from typing import Any
from pathlib import PurePath
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
import boto3
import base64
import json

bedrock_client = boto3.client('bedrock-runtime')
s3_client = boto3.client('s3')

logger = Logger(utc=True)

def lambda_handler(event: dict[str, Any], context: LambdaContext) -> dict[str, Any]:
    """
    Returns the product caption for the referenced image using Claude 3 Haiku model through Bedrock
    """
    bucket = event['bucket']
    key = event['key']

    response_text = call_bedrock(bucket, key)

    return {
        "caption": response_text
    }

def call_bedrock(bucket: str, key: str) -> str:
    body = create_claude_request(bucket, key)

    response = bedrock_client.invoke_model(
        body=body, 
        modelId="anthropic.claude-3-haiku-20240307-v1:0",
        accept="application/json", 
        contentType="application/json"
    )
    response_body = json.loads(response['body'].read())
    response_text = response_body.get("content")[0].get("text")
    return response_text

def create_claude_request(bucket: str, key:str) -> str:
    image = fetch_image(bucket, key)
    # Encode the bytes to base64
    img_base64 = base64.b64encode(image)
    # Get the category folder containing the image
    p = PurePath(key)
    img_category = p.parts[-2]

    # Convert bytes to string
    img_base64_str = img_base64.decode()
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": img_base64_str
                                }
                            },
                            {
                                "type": "text",
                                "text": f"Identify the {img_category} product in the image. Then identify the dominant color or colours of the {img_category} product. Be descriptive. Ignore the background. Name the product and then describe it without any preamble. <example>Sofa, deep, plush green color with a smooth, velvet-like texture. It features a rectangular shape with a modern, streamlined silhouette and two cylindrical cushions at either end, serving as armrests. The sofa has three seat cushions that create a single seating surface without separations, and the back cushion runs the length of the sofa in a single piece as well, contributing to its sleek design. There are no visible patterns or prints on the fabric, which gives it a rich, uniform look. The sofa's legs are short, cylindrical, and appear to be made of light-colored wood</example>"
                            }
                        ]
                    }
            ]
    })
    
    return body

def fetch_image(bucket: str, key: str) -> bytes:
  response = s3_client.get_object(Bucket=bucket, Key=key)
  return response["Body"].read()