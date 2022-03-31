from assertpy import assert_that
import jsonschema
import requests
import json
import os


recommendations_api_url = os.getenv("RECOMMENDATIONS_API_URL")
cwd = os.path.dirname(os.path.abspath(__file__))
wildcards = {":userID": 5097, ":feature": "product_detail_related"}


def full_request_url(text):
    """
    Build a full request URL from the API URL and endpoint.
    Any URL parameters will be replaced with the value set in the environment variables.
    """
    for key in wildcards.keys():
        text = text.replace(key, str(wildcards[key]))
    return recommendations_api_url + text


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
    return r


def put_request_assert(endpoint):
    """
    Send a PUT request and assert response meets expectations.
    """
    with open(absolute_file_path("json_request_bodies.json")) as f:
        body = json.loads(f.read())[endpoint]
    r = requests.put(full_request_url(endpoint), data=json.dumps(body))
    assertions(r, endpoint)


def post_request_assert(endpoint):
    """
    Send a POST request and assert response meets expectations.
    """
    with open(absolute_file_path("json_request_bodies.json")) as f:
        body = json.loads(f.read())[endpoint]
    r = requests.post(
        full_request_url(endpoint),
        data=json.dumps(body),
        headers={"Content-Type": "application/json", "Accept": "appllication/json"},
    )
    assertions(r, endpoint)
    return r


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
    with open(absolute_file_path("json_schemas.json")) as f:
        path = endpoint.split("?")[0]
        schema = json.loads(f.read())[path]
    jsonschema.validate(json.loads(json_str), schema)
    return True


def test_get_recommendations_should_return_products_with_correct_schema():
    get_request_assert("/recommendations?userID=:userID&feature=:feature")


def test_get_recommendations_with_numResults_should_return_exact_number_of_result():
    num_results = 3

    response = get_request_assert(
        f"/recommendations?userID=:userID&feature=:feature&numResults={num_results}"
    )
    recommendation_resp_obj = response.json()

    assert_that(recommendation_resp_obj).is_length(num_results)


def test_get_recommendations_with_currentItemID_should_return_different_product():
    # Calling without "currentItemID" param should get this product id

    response = get_request_assert(f"/recommendations?userID=:userID&feature=:feature")
    recommendation_resp_obj = response.json()
    first_item_id_without_param = recommendation_resp_obj[0]["product"]["id"]

    # Calling with this "currentItemID" param should get another product id
    currentItemID = "89728417-5269-403d-baa3-04b59cdffd0a"

    response = get_request_assert(
        f"/recommendations?userID=:userID&feature=:feature&currentItemID={currentItemID}"
    )
    recommendation_resp_obj = response.json()
    first_item_id = recommendation_resp_obj[0]["product"]["id"]

    assert_that(first_item_id).is_not_equal_to(first_item_id_without_param)


def test_get_recommendations_should_return_image_filename_by_default():
    response = get_request_assert(f"/recommendations?userID=:userID&feature=:feature")
    recommendation_resp_obj = response.json()
    image_field = recommendation_resp_obj[0]["product"]["image"]
    assert_that(image_field.startswith("http://")).is_false()
    
    
def test_get_recommendations_with_fullyQualifyImageUrls_should_return_image_url():
    response = get_request_assert(f"/recommendations?userID=:userID&feature=:feature&fullyQualifyImageUrls=1")
    recommendation_resp_obj = response.json()
    image_field = recommendation_resp_obj[0]["product"]["image"]
    assert_that(image_field).starts_with('http://')
