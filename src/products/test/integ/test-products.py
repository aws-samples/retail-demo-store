import testhelpers.integ as integhelpers
import os
from dotenv import load_dotenv

load_dotenv()

DEFAULT_LOCAL_URL = 'http://localhost:8001'

products_api_url = os.getenv('PRODUCTS_API_URL', DEFAULT_LOCAL_URL)
test_product_id = os.getenv('TEST_PRODUCT_ID', '8bffb5fb-624f-48a8-a99f-b8e9c64bbe29')
test_category_name = os.getenv('TEST_CATEGORY_NAME', 'tools')
test_category_id = os.getenv('TEST_CATEGORY_ID', '16')

cwd = os.path.dirname(os.path.abspath(__file__))
request_bodies_path = integhelpers.absolute_file_path(cwd, "json_request_bodies.json")
schemas_path = integhelpers.absolute_file_path(cwd, "json_schemas.json")


def test_get_products_all():

    endpoint = "/products/all"
    integhelpers.get_request_assert(products_api_url, endpoint, schemas_path)


def test_get_products_id():

    endpoint = "/products/id/:product_id"
    params = {":product_id": test_product_id}
    integhelpers.get_request_assert(products_api_url, endpoint, schemas_path, params)


def test_get_products_featured():

    endpoint = "/products/featured"
    integhelpers.get_request_assert(products_api_url, endpoint, schemas_path)


def test_get_products_category():

    endpoint = "/products/category/:category_name"
    params = {":category_name": test_category_name}
    integhelpers.get_request_assert(products_api_url, endpoint, schemas_path, params)


def test_put_products_id():

    endpoint = "/products/id/:product_id"
    params = {":product_id": test_product_id}
    integhelpers.put_request_assert(products_api_url, endpoint, request_bodies_path, schemas_path, params)


# Test disabled until known issue with this endpoint is resolved
# def test_put_products_id_inventory():
#
#     endpoint = "/products/id/:product_id/inventory"
#     params = {":product_id": test_product_id}
#     integhelpers.put_request_assert(products_api_url, endpoint, request_bodies_path, schemas_path, params)


# Test disabled until known issue with this endpoint is resolved
# def test_delete_products_id():
#
#     endpoint = "/products/id/:product_id"
#     integhelpers.delete_request_assert(products_api_url, endpoint, schemas_path)


def test_post_products():

    endpoint = "/products"
    integhelpers.post_request_assert(products_api_url, endpoint, request_bodies_path, schemas_path)


def test_get_categories_all():

    endpoint = "/categories/all"
    integhelpers.get_request_assert(products_api_url, endpoint, schemas_path)


def test_get_categories_id():

    endpoint = "/categories/id/:category_id"
    params = {":category_id": test_category_id}
    integhelpers.get_request_assert(products_api_url, endpoint, schemas_path, params)

