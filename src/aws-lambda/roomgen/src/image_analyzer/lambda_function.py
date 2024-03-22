import json
import io
import base64
import os
from dataclasses import dataclass, asdict, field
from typing import Any, List
from PIL import Image
import boto3
from botocore.exceptions import ClientError
from opensearchpy import OpenSearch
from aws_lambda_powertools import Logger, Metrics
from aws_lambda_powertools.utilities.typing import LambdaContext

s3_client = boto3.client('s3')
rekognition_client = boto3.client('rekognition')
bedrock_runtime = boto3.client(service_name="bedrock-runtime")
dynamodb_client = boto3.client('dynamodb')

search_domain_scheme = os.environ.get('OPENSEARCH_DOMAIN_SCHEME', 'https')
search_domain_host = os.environ['OPENSEARCH_DOMAIN_HOST']
search_domain_port = os.environ.get('OPENSEARCH_DOMAIN_PORT', 443)

search_client = OpenSearch(
    [search_domain_host],
    scheme=search_domain_scheme,
    port=search_domain_port,
)

input_image_bucket = os.environ['INPUT_IMAGE_BUCKET']
embedded_products_index_name = os.environ['OPENSEARCH_INDEX_NAME']

table_name = os.environ['DYNAMODB_TABLE_NAME']

logger = Logger(utc=True)
metrics = Metrics()

room_style_prompt_mapping = {
    'minimalist': 'Transform a traditional living room into a modern, minimalist space with sleek furniture and natural light enhancement.', 
    'modern': 'Revamp a traditional living room into a Mid Century Modern oasis featuring clean lines, organic forms, and a mix of different materials such as wood, metal, and glass.', 
    'bohemian': 'Rework a traditional living room into a Bohemian Chic haven with eclectic furnishings, vibrant textiles, and an abundance of plants and cultural artifacts.', 
    'rustic': 'Update a traditional living room into a Rustic Farmhouse setting with reclaimed wood accents, comfortable and practical furniture, and a warm, neutral color palette.', 
    'industrial': 'Transform a traditional living area into an edgy Industrial loft, highlighting raw, unfinished materials like exposed brick and steel, open spaces, and vintage-inspired lighting for a touch of modernity.', 
    'scandanavian': 'Redesign a conventional living space into a serene, Scandinavian sanctuary that emphasizes functionality, natural light flooding, and a palette of soft, muted colors paired with elements of wood.'
}

@dataclass
class SimilarItem:
    id: str
    caption: str

@dataclass
class LabelBox:
    name: str
    bounding_box: dict[str, int]
    similar_items: List[SimilarItem] = field(default_factory=list)

@dataclass
class RoomGenerationRequest:
    id: str
    room_style: str
    image_prefix: str
    image_key: str

@metrics.log_metrics(capture_cold_start_metric=True)
def lambda_handler(event: dict[str, Any], context: LambdaContext) -> dict:
    request = RoomGenerationRequest(event["id"], event['room_style'], event["image_prefix"], event["image_key"])
    
    labelled_furniture = get_labelled_furniture(input_image_bucket, request.image_key)
    prompt = create_approximate_prompt(request.room_style, labelled_furniture)
    
    update_db(request.id, labelled_furniture, prompt)

    response = asdict(request)
    response['prompt'] = prompt
    return response

def get_labelled_furniture(input_image_bucket:str, image_key: str) -> List[LabelBox]:
    labelled_furniture: List[LabelBox] = analyze_image(input_image_bucket, image_key)
    initial_image: Image = fetch_image(input_image_bucket, image_key)
    for furniture_item_box in labelled_furniture:
        try:
            cropped_image: bytes = crop_image(initial_image, furniture_item_box)
            embeddings: List[float] = get_embeddings(cropped_image, furniture_item_box.name)
            similar_items: List[SimilarItem] = get_similar_items(embeddings)
        except Exception:
            logger.error(f"Couldn't process labelled box: {furniture_item_box.name}")
        else:
            furniture_item_box.similar_items = similar_items
    return labelled_furniture

def fetch_image(bucket: str, key: str) -> Image:
    response = s3_client.get_object(Bucket=bucket, Key=key)
    image_bytes = response["Body"].read()
    return Image.open(io.BytesIO(image_bytes))

def analyze_image(bucket: str, key: str, rekognition_max_labels: int = 10, rekognition_min_confidence: int = 10) -> List[LabelBox]:
    # Prepare the request
    params = {
        'Image': {
            'S3Object': {
                'Bucket': bucket,
                'Name': key
            }
        },
        'MaxLabels': rekognition_max_labels, 
        'MinConfidence': rekognition_min_confidence
    }
    response = rekognition_client.detect_labels(**params)    
    label_boxes = []
    for label in response.get('Labels', []):
        for instance in label.get('Instances', []):
            if bounding_box := instance.get('BoundingBox'):
                label_boxes.append(LabelBox(
                    name=label.get('Name', 'Unknown'),
                    bounding_box={
                        'Left': bounding_box.get('Left'),
                        'Top': bounding_box.get('Top'),
                        'Width': bounding_box.get('Width'),
                        'Height': bounding_box.get('Height')
                    }
                ))
    return label_boxes

def crop_image(image: Image, box: LabelBox) -> bytes:
    def to_pixel_coordinates(relative_coord, dimension) -> float:
        return round(relative_coord * dimension)
          
    left = to_pixel_coordinates(box.bounding_box['Left'] if 'Left' in box.bounding_box else 0, 1024)
    top = to_pixel_coordinates(box.bounding_box['Top'] if 'Top' in box.bounding_box else 0, 1024)
    width = to_pixel_coordinates(box.bounding_box['Width'] if 'Width' in box.bounding_box else 0, 1024)
    height = to_pixel_coordinates(box.bounding_box['Height'] if 'Height' in box.bounding_box else 0, 1024)
    try:    
        # Crop the image according to the bounding box
        cropped_image = image.crop((left, top, left + width, top + height))
        buffered = io.BytesIO()
        cropped_image.save(buffered, format="PNG")      
    except Exception as error:
        logger.exception('Error processing image box')
        raise error
    else:
        logger.info(f"{box.name} cropped successfully")
        return buffered.getvalue()

# Function to send an inference request to the Titan model
def get_embeddings(image_bytes: bytes, text_description: str) -> List[float]:
    # Encode the bytes to base64
    img_base64 = base64.b64encode(image_bytes)
    # Convert bytes to string
    img_base64_str = img_base64.decode()

    body = json.dumps({
        "inputText": text_description,
        "inputImage": img_base64_str
    })
    try:
        response = bedrock_runtime.invoke_model(
            body=body, 
            modelId="amazon.titan-embed-image-v1",
            accept="application/json", 
            contentType="application/json"
        )
        response_body = json.loads(response.get("body").read())
    except ClientError as error:
        logger.exception("Error getting Titan embeddings")
        raise error
    else:
        return response_body.get("embedding")
    
def get_similar_items(embeddings: bytes, size=3) -> List[SimilarItem]:
    query = {
        "size": size,
        "_source": ["caption"],
        "query": {
            "knn": {
                "embedding": {
                    "vector": embeddings,
                    "k": size
                }
            }
        }
    }
    try: 
        response = search_client.search(query, index = embedded_products_index_name)
    except ClientError as error:
        logger.exception('There was a problem retrieving similar items')
        raise error
    else:
        hits = response['hits']['hits']
        # Update the box with similarItems
        return [SimilarItem(hit['_id'], hit['_source']['caption']) for hit in hits]

def create_approximate_prompt(room_style: str, labelled_furniture: List[LabelBox]):
    # Get the base prompt for the style requested
    new_prompt = room_style_prompt_mapping[room_style]
    max_length = 350

    captions = [labelled_box.similar_items[0].caption for labelled_box in labelled_furniture if labelled_box.similar_items]
    if not captions:
        return new_prompt[:max_length]  # Return the base prompt if no labels
    
    # Calculate the average length we can afford for each label to approximate even distribution
    average_length_per_item = (max_length - len(new_prompt)) // len(captions)
    logger.debug(f"Average length per item: {average_length_per_item}")
    # Append an evenly distributed part of each item's similar_items[0][4]
    for caption in captions:
        # Calculate the length to use, ensuring we don't exceed our average target too much
        part_length = min(average_length_per_item, len(caption))
        # Add the item part to the new_prompt
        # Remove some standard text that won't add anything
        new_prompt += "," + caption.replace("The image shows ", "")[:part_length]
        # Break if we reach or exceed the max_length
        if len(new_prompt) >= max_length:
            break
    
    return new_prompt[:max_length]

def update_db(id: str, labels: List[LabelBox], prompt: str) -> None:        
    boxes = [{'M': {
        'name': {'S': label.name},
        'bounding_box': {'M': {key: {"N": str(value)} for key, value in label.bounding_box.items()}},
        'similar_items': {'L': [{"S": item.id} for item in label.similar_items]}
    }} for label in labels]
    dynamodb_client.update_item(
        TableName=table_name, 
        Key={
            'id': {
                'S': id
            }
        },
        ExpressionAttributeValues={
            ':state': {'S' : 'Analyzing'},
            ':labels': {'L': boxes},
            ':prompt': {'S': prompt}
        },
        UpdateExpression='SET room_state = :state, prompt = :prompt, labels = :labels')
