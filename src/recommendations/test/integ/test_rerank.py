import os
from assertpy import assert_that
from testhelpers.integ import (
    absolute_file_path,
    post_request_assert,
    read_file
)
from dotenv import load_dotenv

load_dotenv()

DEFAULT_LOCAL_API = 'http://localhost:8005'

cwd = os.path.dirname(os.path.abspath(__file__))
request_bodies_path = absolute_file_path(cwd, "json_request_bodies.json")
schemas_path = absolute_file_path(cwd, "json_schemas.json")
recommendations_api_url = os.getenv("RECOMMENDATIONS_API_URL", DEFAULT_LOCAL_API)

input_request_body = read_file(request_bodies_path, '/rerank')


def test_post_rerank_should_return_with_correct_schema():
    endpoint = "/rerank"
    post_request_assert(recommendations_api_url, endpoint,request_bodies_path, schemas_path )

def test_post_rerank_should_return_shuffled_items():
    endpoint = "/rerank"
    response = post_request_assert(recommendations_api_url, endpoint,request_bodies_path, schemas_path )
    items = response.json()
    
    assert_that(items).is_length(len(input_request_body['items']))

    # TODO: Rerank doesn't work without Optimizely or Personalize
    # Once we have an automated way to deploy Personalize, we can use these assertions to verify that rerank happens
    # assert_that(items).is_not_equal_to(input_request_body['items'])

