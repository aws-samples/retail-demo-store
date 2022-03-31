import os
import json
from assertpy import assert_that
from test_recommendations import post_request_assert

API_PATH = "/rerank"
cwd = os.path.dirname(os.path.abspath(__file__))

def read_file(path, api_path):
    filepath = os.path.join(cwd, path)
    with open(filepath) as f:
        body = json.loads(f.read())[api_path]
    return body

input_request_body = read_file("json_request_bodies.json", API_PATH)


def test_post_rerank_should_return_with_correct_schema():
    post_request_assert(API_PATH) 

def test_post_rerank_should_return_shuffled_items():
    response = post_request_assert(API_PATH) 
    items = response.json()
    
    assert_that(items).is_length(len(input_request_body['items']))

    # TODO: Rerank doesn't work without Optimizely or Personalize
    # Once we have an automated way to deploy Personalize, we can use these assertions to verify that rerank happens
    # assert_that(items).is_not_equal_to(input_request_body['items'])

