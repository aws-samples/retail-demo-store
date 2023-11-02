import testhelpers.integ as integhelpers
import json
import os
import pytest
from dotenv import load_dotenv
import requests
from assertpy import assert_that

load_dotenv()

DEFAULT_LOCAL_API_URL = "http://localhost:8004"

orders_api_url = os.getenv("ORDERS_API_URL", DEFAULT_LOCAL_API_URL)
test_order_id = os.getenv("TEST_ORDER_ID", '209673d6-46a5-11ee-be56-0242ac120002')
test_username = os.getenv("TEST_USERNAME", "user1344")

cwd = os.path.dirname(os.path.abspath(__file__))
request_bodies_path = integhelpers.absolute_file_path(cwd, "json_request_bodies.json")
schemas_path = integhelpers.absolute_file_path(cwd, "json_schemas.json")


@pytest.fixture()
def created_order():
    print("### Creating a new order")
    endpoint = "/orders"
    body = integhelpers.read_file(request_bodies_path, endpoint)

    response = requests.post(
        integhelpers.full_request_url(orders_api_url, endpoint),
        data=json.dumps(body),
        headers={"Content-Type": "application/json", "Accept": "application/json"},
    )
    assert str(response.status_code).startswith("2")

    # Pass created order object to the test case
    yield json.loads(response.text)

    # There is no endpoint to delete the created order so it's left there

def test_get_orders_all(created_order):
    endpoint = "/orders/all"
    response = integhelpers.get_request_assert(orders_api_url, endpoint, schemas_path)
    all_orders = json.loads(response.text)
    assert len(all_orders) > 0
    assert created_order in all_orders


def test_get_orders_id(created_order):
    endpoint = "/orders/id/:order_id"
    params = {":order_id": created_order['id']}
    integhelpers.get_request_assert(orders_api_url, endpoint, schemas_path, params)


def test_put_orders_id():
    endpoint = "/orders/id/:order_id"
    params = {":order_id": test_order_id}
    integhelpers.put_request_assert(orders_api_url, 
                                    endpoint, 
                                    request_bodies_path, 
                                    schemas_path, 
                                    params)


def test_post_orders():
    endpoint = "/orders"
    integhelpers.post_request_assert(orders_api_url, 
                                     endpoint, 
                                     request_bodies_path, 
                                     schemas_path)


def test_get_orders_username():
    endpoint = "/orders/username/:username"
    params = {":username": test_username}
    integhelpers.get_request_assert(orders_api_url, endpoint, schemas_path, params)
    
def test_get_nonexistent_orders_id():
    endpoint = "/orders/id/nonexistent_id"
    response = requests.get(integhelpers.full_request_url(orders_api_url, endpoint))
    assert_that(response.status_code).is_equal_to(404)
    assert_that(response.text).contains("Not found")
    
def test_post_invalid_orders():
    endpoint = "/orders"
    body = integhelpers.read_file(request_bodies_path, endpoint)
    body['invalid_key'] = 'invalid_value'
    response = requests.post(
        integhelpers.full_request_url(orders_api_url, endpoint),
        data=json.dumps(body),
        headers={"Content-Type": "application/json", "Accept": "application/json"},
    )
    assert_that(response.status_code).is_equal_to(400)
    assert_that(response.text).contains("Bad request, please check your input")

def test_put_invalid_orders():
    endpoint = "/orders/id/:order_id"
    body = integhelpers.read_file(request_bodies_path, endpoint)
    body['invalid_key'] = 'invalid_value'
    endpoint = f"/orders/id/{test_order_id}"
    response = requests.put(
        integhelpers.full_request_url(orders_api_url, endpoint),
        data=json.dumps(body),
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        )
    assert_that(response.status_code).is_equal_to(400)
    assert_that(response.text).contains("Bad request, please check your input")
    
def test_update_nonexistent_orders_id():
    endpoint = "/orders/id/:order_id"
    body = integhelpers.read_file(request_bodies_path, endpoint)
    body['id'] = 'nonexistent_id'
    response = requests.put(
        integhelpers.full_request_url(orders_api_url, endpoint),
        data=json.dumps(body),
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        )
    assert_that(response.status_code).is_equal_to(404)
    assert_that(response.text).contains("Not found")