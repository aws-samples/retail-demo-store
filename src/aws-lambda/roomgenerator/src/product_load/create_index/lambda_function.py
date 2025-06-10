from crhelper import CfnResource
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth
import boto3
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
region = os.environ['AWS_DEFAULT_REGION']
search_collection_endpoint = os.environ['OPENSEARCH_COLLECTION_HOST']
final_host = search_collection_endpoint.replace("https://", "")
search_client = OpenSearch(
            hosts = [{'host': final_host, 'port': os.environ.get('OPENSEARCH_COLLECTION_PORT', 443)}],
            http_auth=AWSV4SignerAuth(boto3.Session().get_credentials(), region, 'aoss'),
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection,
            timeout=30, 
            max_retries=10, 
            retry_on_timeout=True
        )
helper = CfnResource()

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