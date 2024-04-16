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

@helper.delete
def opensearch_delete(event,_):
  if search_client.indices.exists(index_name):
      search_client.indices.delete(index_name)

@helper.create
@helper.update
def opensearch_create(event,_):
  if not search_client.indices.exists(index_name):
      search_client.indices.create(index_name, body=mapping)

def lambda_handler(event, context):
  """
  Creates the Embeddings Product index if it does not exist in OpenSearch
  """
  helper(event, context)