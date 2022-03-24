import jsonschema
import requests
import json
import os


products_api_url = os.getenv('PRODUCTS_API_URL')
cwd = os.path.dirname(os.path.abspath(__file__))
wildcards = {
    ":product_id": os.getenv('TEST_PRODUCT_ID'),
    ":category_name": os.getenv('TEST_CATEGORY_ID'),
    ":category_id": os.getenv('TEST_CATEGORY_ID')
}


def full_request_url(text):
    """
    Build a full request URL from the API URL and endpoint.
    Any URL parameters will be replaced with the value set in the environment variables.
    """
    for key in wildcards.keys():
        text = text.replace(key, str(wildcards[key]))
    return products_api_url + text


def absolute_file_path(filename):
    """
    Join a filename in the same directory as this function with the current working directory for the absolute path.
    """
    return os.path.join(cwd, filename)


def get_request_assert(endpoint):
    """
    Send a GET request and assert response meets expectations.
    """
    r = requests.get(full_request_url(endpoint))
    assertions(r, endpoint)


def put_request_assert(endpoint):
    """
    Send a PUT request and assert response meets expectations.
    """
    with open(absolute_file_path('json_request_bodies.json')) as f:
        body = json.loads(f.read())[endpoint]
    r = requests.put(full_request_url(endpoint), data=json.dumps(body))
    assertions(r, endpoint)


def post_request_assert(endpoint):
    """
    Send a POST request and assert response meets expectations.
    """
    with open(absolute_file_path('json_request_bodies.json')) as f:
        body = json.loads(f.read())[endpoint]
    r = requests.post(full_request_url(endpoint), data=json.dumps(body),
                      headers={"Content-Type": "application/json", "Accept": "appllication/json"})
    assertions(r, endpoint)


def delete_request_assert(endpoint):
    """
    Send a DELETE request and assert response meets expectations.
    """
    r = requests.delete(full_request_url(endpoint))
    assertions(r, endpoint)


def assertions(r, endpoint):
    """
    Assert response is successful and validate response body when applicable.
    """
    assert r.status_code is 200
    if r.headers["Content-Type"].startswith("application/json"):
        assert validate_schema(r.text, endpoint) is True
    else:
        assert False


def validate_schema(json_str, endpoint):
    """
    Validate a JSON response body against a schema.
    """
    with open(absolute_file_path('json_schemas.json')) as f:
        schema = json.loads(f.read())[endpoint]

    try:
        jsonschema.validate(json.loads(json_str), schema)
    except jsonschema.exceptions.ValidationError as e:
        return False
    return True


def test_get_products_all():

    get_request_assert("/products/all")


def test_get_products_id():

    get_request_assert("/products/id/:product_id")


def test_get_products_featured():

    get_request_assert("/products/featured")


def test_get_products_category():

    get_request_assert("/products/category/:category_name")


def test_put_products_id():

    put_request_assert("/products/id/:product_id")


# Test disabled until known issue with this endpoint is resolved
# def test_put_products_id_inventory():
#
#     put_request_assert("/products/id/:product_id/inventory")


# Test disabled until known issue with this endpoint is resolved
# def test_delete_products_id():
#
#     delete_request_assert("/products/id/:product_id")


def test_post_products():

    post_request_assert("/products")


def test_get_categories_all():

    get_request_assert("/categories/all")


def test_get_categories_id():

    get_request_assert("/categories/id/:category_id")

