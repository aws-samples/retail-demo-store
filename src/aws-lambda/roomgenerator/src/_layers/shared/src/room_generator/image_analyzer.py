import json
import io
import base64
from dataclasses import dataclass, field
from typing import List
from PIL import Image
import boto3
from botocore.exceptions import ClientError
from opensearchpy import OpenSearch
from aws_lambda_powertools import Logger

s3_client = boto3.client('s3')
rekognition_client = boto3.client('rekognition')
bedrock_runtime = boto3.client('bedrock-runtime')

@dataclass
class SimilarItem:
    id: str
    caption: str

@dataclass
class LabelBox:
    name: str
    bounding_box: dict[str, int]
    similar_items: List[SimilarItem] = field(default_factory=list)

class ImageAnalyzer():
    def __init__(self, opensearch_hosts: List[dict[str,str]], opensearch_index_name: str, logger: Logger):
        self.search_client = OpenSearch(
            hosts = opensearch_hosts,
            use_ssl = True
        )
        self.embedded_products_index_name = opensearch_index_name
        self.logger = logger
    
    def get_labelled_furniture(self, input_image_bucket:str, image_key: str) -> List[LabelBox]:
        labelled_furniture: List[LabelBox] = self.__analyze_image(input_image_bucket, image_key)
        initial_image: Image = self.__fetch_image(input_image_bucket, image_key)
        for furniture_item_box in labelled_furniture:
            try:
                cropped_image: bytes = self.__crop_image(initial_image, furniture_item_box)
                embeddings: List[float] = self.__get_embeddings(cropped_image, furniture_item_box.name)
                similar_items: List[SimilarItem] = self.__get_similar_items(embeddings)
            except Exception as error:
                self.logger.error(f"Could process labelled box: {furniture_item_box.name}", exc_info=error)
            else:
                furniture_item_box.similar_items = similar_items
        return labelled_furniture
    
    def resize_image(self, image_bytes: bytes, size: tuple[int, int]) -> bytes:
        image = Image.open(io.BytesIO(image_bytes))
        resized_image = image.resize(size=size)
        buffered = io.BytesIO()
        resized_image.save(buffered, format="PNG")
        return buffered.getvalue()

    def __fetch_image(self, bucket: str, key: str) -> Image:
        response = s3_client.get_object(Bucket=bucket, Key=key)
        image_bytes = response["Body"].read()
        return Image.open(io.BytesIO(image_bytes))

    def __analyze_image(self, bucket: str, key: str, rekognition_max_labels: int = 10, rekognition_min_confidence: int = 10) -> List[LabelBox]:
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

    def __crop_image(self, image: Image, box: LabelBox) -> bytes:
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
            self.logger.exception('Error processing image box')
            raise error
        else:
            self.logger.info(f"{box.name} cropped successfully")
            return buffered.getvalue()

    # Function to send an inference request to the Titan model
    def __get_embeddings(self, image_bytes: bytes, text_description: str) -> List[float]:
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
            self.logger.exception("Error getting Titan embeddings")
            raise error
        else:
            return response_body.get("embedding")
        
    def __get_similar_items(self, embeddings: bytes, size=3) -> List[SimilarItem]:
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
            response = self.search_client.search(query, index = self.embedded_products_index_name)
        except ClientError as error:
            self.logger.exception('There was a problem retrieving similar items')
            raise error
        else:
            hits = response['hits']['hits']
            # Update the box with similarItems
            return [SimilarItem(hit['_id'], hit['_source']['caption']) for hit in hits]
