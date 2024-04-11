from typing import Any, List
from pathlib import PurePath
from aws_lambda_powertools.utilities.data_classes import event_source, SQSEvent
from aws_lambda_powertools import Logger
from opensearchpy.helpers import bulk
from opensearchpy import OpenSearch
import os

index_name=os.environ['OPENSEARCH_INDEX_NAME']
search_client = OpenSearch(
            hosts = [{'host': os.environ['OPENSEARCH_DOMAIN_HOST'], 'port': os.environ.get('OPENSEARCH_DOMAIN_PORT', 443)}],
            use_ssl = True
        )

logger = Logger(utc=True)

@event_source(data_class=SQSEvent)
def lambda_handler(event: SQSEvent, context):
    """
    Bulk indexes the product embeddings and captions into OpenSearch
    Batch size is controlled by the SQS Lambda trigger
    """
    docs = create_docs(event)
    success, errors = bulk(search_client, docs)

    logger.info(f"{success} products indexed, {len(errors)} errors")
    if errors:
        logger.error({errors})

def create_docs(event: SQSEvent) -> List[dict[str, Any]]:
    """
    Converts the records in the SQS Event to docs that will be indexed into OpenSearch.
    Multiple records can be delivered in a single event.
    Each record will be formatted as follows:
     {'bucket': 'bucket_name', 'key': 'category/productId.jpg', 
       'data': {"embedding": [0.031100968, 0.0036890781, ...], "caption": "Description of product image ..."}}
    """
    docs = []
    for record in event.records:
        try:
            body = record.json_body
            id, category = get_id_category(body)

            doc = {}
            doc['_index'] = index_name
            doc['_id'] = id
            doc['category'] = category
            doc['embedding'] = body['data']['embedding']
            doc['caption'] = body['data']['caption']
            docs.append(doc)
        except Exception:
            logger.exception(f"Problem indexing record, skipping... {record}")
            pass
    return docs

def get_id_category(body: dict[str, Any]) -> tuple[str, str]:
    p = PurePath(body['key'])
    id = p.stem
    category = p.parts[-2]
    return id, category