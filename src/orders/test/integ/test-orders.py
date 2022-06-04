import testhelpers.integ as integhelpers
import os
from dotenv import load_dotenv

load_dotenv()

DEFAULT_LOCAL_API_URL = 'http://localhost:8004'

orders_api_url = os.getenv('ORDERS_API_URL', DEFAULT_LOCAL_API_URL)
test_order_id = os.getenv('TEST_ORDER_ID', 1)
test_username = os.getenv('TEST_USERNAME', 'user1344')

cwd = os.path.dirname(os.path.abspath(__file__))
request_bodies_path = integhelpers.absolute_file_path(cwd, "json_request_bodies.json")
schemas_path = integhelpers.absolute_file_path(cwd, "json_schemas.json")


def test_get_orders_all():

    endpoint = "/orders/all"
    integhelpers.get_request_assert(orders_api_url, endpoint, schemas_path)


def test_get_orders_id():

    endpoint = "/orders/id/:order_id"
    params = {":order_id": test_order_id}
    integhelpers.get_request_assert(orders_api_url, endpoint, schemas_path, params)


def test_put_orders_id():

    endpoint = "/orders/id/:order_id"
    params = {":order_id": test_order_id}
    integhelpers.put_request_assert(orders_api_url, endpoint, request_bodies_path, schemas_path, params)


def test_post_orders():

    endpoint = "/orders"
    params = {":order_id": test_order_id}
    integhelpers.post_request_assert(orders_api_url, endpoint, request_bodies_path, schemas_path, params)


def test_get_orders_username():

    endpoint = "/orders/username/:username"
    params = {":username": test_username}
    integhelpers.get_request_assert(orders_api_url, endpoint, schemas_path, params)
