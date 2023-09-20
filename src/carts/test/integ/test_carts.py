import json
import os

import requests
from assertpy import assert_that
from testhelpers.integ import (
    absolute_file_path,
    get_request_assert,
    post_request_assert,
    put_request_assert,
    full_request_url
)
from dotenv import load_dotenv

load_dotenv()

DEFAULT_LOCAL_API = 'http://localhost:80'
test_cart_id = os.getenv('TEST_CART_ID', 'a2433611-5033-4e6d-b03d-9db2c49dc939')
test_username = os.getenv('TEST_USERNAME', 'test_user')
cwd = os.path.dirname(os.path.abspath(__file__))
request_bodies_path = absolute_file_path(cwd, "json_request_bodies.json")
schemas_path = absolute_file_path(cwd, "json_schemas.json")
carts_api_url = os.getenv("CARTS_API_URL", DEFAULT_LOCAL_API)

def test_post_carts_should_return_with_correct_schema():
    endpoint = "/carts"
    post_request_assert(
        carts_api_url, endpoint, request_bodies_path, schemas_path
    )

def test_get_carts_should_return_with_correct_schema():
    endpoint = "/carts?username=:username"
    params = {":username": test_username}
    get_request_assert(carts_api_url, endpoint, schemas_path, endpoint_params=params)

def test_get_cart_by_id_should_return_with_correct_schema():
    endpoint = "/carts/:cart_id"
    params = {":cart_id": test_cart_id}
    get_request_assert(carts_api_url, endpoint, schemas_path, params)
    
def test_put_cart_by_id_should_return_with_correct_schema():
    endpoint = "/carts/:cart_id"
    params = {":cart_id": test_cart_id}
    put_request_assert(carts_api_url, endpoint, request_bodies_path, schemas_path, params)
    
def test_post_carts_invalid_cart():
    endpoint = "/carts"
    body = {"invalid_key": "invalid_value"} 
    response = requests.post(full_request_url(carts_api_url, endpoint), data=json.dumps(body))
    assert_that(response.status_code).is_equal_to(400)
    assert_that(response.json()["error"]).is_equal_to("Bad request, please check your input")

def test_get_nonexistent_cart():
    endpoint = "/carts/nonexistent_id"
    response = requests.get(full_request_url(carts_api_url, endpoint))
    assert_that(response.status_code).is_equal_to(404)
    assert_that(response.json()["error"]).is_equal_to("Not found")
    
def test_update_with_invalid_cart():
    endpoint = f"/carts/{test_cart_id}"
    body = {"invalid_key": "invalid_value"}
    response = requests.put(full_request_url(carts_api_url, endpoint), data=json.dumps(body))
    assert_that(response.status_code).is_equal_to(400)
    assert_that(response.json()["error"]).is_equal_to("Bad request, please check your input")
    
def test_update_with_id_mismatch():
    endpoint = f"/carts/{test_cart_id}"
    body = {"id": "invalid_value"}
    response = requests.put(full_request_url(carts_api_url, endpoint), data=json.dumps(body))
    assert_that(response.status_code).is_equal_to(400)
    assert_that(response.json()["error"]).is_equal_to("Bad request, please check your input")
    
def test_update_with_nonexistent_cart():
    endpoint = "/carts/nonexistent_id"
    body = {"id": "invalid_value"}
    response = requests.put(full_request_url(carts_api_url, endpoint), data=json.dumps(body))
    assert_that(response.status_code).is_equal_to(404)
    assert_that(response.json()["error"]).is_equal_to("Not found")