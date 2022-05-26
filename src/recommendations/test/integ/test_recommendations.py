from assertpy import assert_that
import os
from testhelpers.integ import (
    absolute_file_path,
    get_request_assert
)


cwd = os.path.dirname(os.path.abspath(__file__))
request_bodies_path = absolute_file_path(cwd, "json_request_bodies.json")
schemas_path = absolute_file_path(cwd, "json_schemas.json")
recommendation_api_url = os.getenv("RECOMMENDATIONS_API_URL") or sys.exit(
    "Please provide an environment variable RECOMMENDATIONS_API_URL"
)

DEFAULT_PARAMS = {":userID": 5097, ":feature": "product_detail_related"}


def test_get_recommendations_should_return_products_with_correct_schema():
    endpoint = "/recommendations?userID=:userID&feature=:feature"
    params = DEFAULT_PARAMS 
    get_request_assert(recommendation_api_url, endpoint, schemas_path, params)


def test_get_recommendations_with_numResults_should_return_exact_number_of_result():
    num_results = 3

    endpoint = "/recommendations?userID=:userID&feature=:feature&numResults=:numResults"
    params = {
        **DEFAULT_PARAMS,
        ":numResults": num_results,
    }
    response = get_request_assert(recommendation_api_url, endpoint, schemas_path, params)
    recommendation_resp_obj = response.json()

    assert_that(recommendation_resp_obj).is_length(num_results)


def test_get_recommendations_with_currentItemID_should_return_different_product():
    # Calling without "currentItemID" param should get this product id
    endpoint = "/recommendations?userID=:userID&feature=:feature&currentItemID"
    params = DEFAULT_PARAMS
    response = get_request_assert(recommendation_api_url, endpoint, schemas_path, params)
    recommendation_resp_obj = response.json()
    first_item_id_without_param = recommendation_resp_obj[0]["product"]["id"]

    # Calling with this "currentItemID" param should get another product id
    currentItemID = "89728417-5269-403d-baa3-04b59cdffd0a"

    endpoint = "/recommendations?userID=:userID&feature=:feature&currentItemID=:currentItemID"
    params = {
        **DEFAULT_PARAMS,
        ":currentItemID": currentItemID
    }
    response = get_request_assert(recommendation_api_url, endpoint, schemas_path, params)
    recommendation_resp_obj = response.json()
    first_item_id = recommendation_resp_obj[0]["product"]["id"]

    assert_that(first_item_id).is_not_equal_to(first_item_id_without_param)


def test_get_recommendations_should_return_image_filename_by_default():
    endpoint = "/recommendations?userID=:userID&feature=:feature&currentItemID"
    params = DEFAULT_PARAMS
    response = get_request_assert(recommendation_api_url, endpoint, schemas_path, params)
    recommendation_resp_obj = response.json()
    image_field = recommendation_resp_obj[0]["product"]["image"]

    assert_that(image_field.startswith("http://")).is_false()
    
    
def test_get_recommendations_with_fullyQualifyImageUrls_should_return_image_url():
    endpoint = "/recommendations?userID=:userID&feature=:feature&currentItemID&fullyQualifyImageUrls=:fullyQualifyImageUrls"
    params = {
        **DEFAULT_PARAMS,
        ":fullyQualifyImageUrls": 1,
    }
    response = get_request_assert(recommendation_api_url, endpoint, schemas_path, params)
    recommendation_resp_obj = response.json()
    image_field = recommendation_resp_obj[0]["product"]["image"]
    
    assert_that(image_field).starts_with('http://')
