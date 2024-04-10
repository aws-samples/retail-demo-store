from crhelper import CfnResource
from opensearchpy import OpenSearch
import os

mapping = {
  "settings": {
    "index.knn": True
  },
  "mappings" : {
      "properties" : {
          "category": { "type" : "text" },
          "caption":  { "type" : "text" },
          "embedding": {
            "type": "knn_vector",
            "dimension": 1024,
            "method": {
              "name": "hnsw",
              "space_type": "l2",
              "engine": "faiss"
            }
          }
      }
  }
}

index_name=os.environ['OPENSEARCH_INDEX_NAME']
search_client = OpenSearch(
            hosts = [{'host': os.environ['OPENSEARCH_DOMAIN_HOST'], 'port': os.environ.get('OPENSEARCH_DOMAIN_PORT', 443)}],
            use_ssl = True
        )
helper = CfnResource()

def create_index():
    if not search_client.indices.exists(index_name):
        search_client.indices.create(index_name, body=mapping)

@helper.create
def opensearch_create(event,_):
    create_index()

def lambda_handler(event, context):
    """
    Creates the Embeddings Product index if it does not exist in OpenSearch
    """
    # If the event has a RequestType, we're being called by CFN as custom resource
    if event.get('RequestType'):
        helper(event, context)
    else:
        create_index()
