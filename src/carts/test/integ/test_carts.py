import os
from assertpy import assert_that
from testhelpers.integ import (
    absolute_file_path,
    get_request_assert,
    post_request_assert,
    put_request_assert,
    read_file
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