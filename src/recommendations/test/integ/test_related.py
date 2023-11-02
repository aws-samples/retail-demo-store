import os
from assertpy import assert_that
import validators
from testhelpers.integ import (
    absolute_file_path,
    get_request_assert
)
from dotenv import load_dotenv

load_dotenv()

DEFAULT_LOCAL_API = 'http://localhost:8005'

cwd = os.path.dirname(os.path.abspath(__file__))
request_bodies_path = absolute_file_path(cwd, "json_request_bodies.json")
schemas_path = absolute_file_path(cwd, "json_schemas.json")
recommendations_api_url = os.getenv("RECOMMENDATIONS_API_URL", DEFAULT_LOCAL_API)

DEFAULT_PARAMS = {
    ":feature": "product_detail_related",
    # If Optimizely is configured, this field will be used to select a specific Experiment.
    # The default deployment doesn't have Optmizely so this value doesn't affect the result.
    ":currentItemID": "89728417-5269-403d-baa3-04b59cdffd0a",
}
def test_get_related_with_default_params_should_return_a_non_empty_list_of_product():
    endpoint = "/related?userID=:userID&feature=:feature&currentItemID=:currentItemID"
    params = DEFAULT_PARAMS
    response = get_request_assert(recommendations_api_url, endpoint, schemas_path, params)
    related_resp_obj = response.json()

    assert_that(related_resp_obj).is_not_empty()

def test_get_related_with_numResults_params_should_return_exact_number_of_result():
    num_results = 3

    endpoint = "/recommendations?userID=:userID&feature=:feature&currentItemID&numResults=:numResults"
    params = {
        **DEFAULT_PARAMS,
        ":numResults": num_results
    }
    response = get_request_assert(recommendations_api_url, endpoint, schemas_path, params)
    related_resp_obj = response.json()

    assert_that(related_resp_obj).is_length(num_results)


def test_get_related_should_return_image_filename_by_default():
    endpoint = "/related?userID=:userID&feature=:feature&currentItemID=:currentItemID"
    params = DEFAULT_PARAMS
    response = get_request_assert(recommendations_api_url, endpoint, schemas_path, params)
    recommendation_resp_obj = response.json()
    image_field = recommendation_resp_obj[0]["product"]["image"]

    assert_that(image_field.startswith("http://")).is_false()


def test_get_related_with_fullyQualifyImageUrls_should_return_image_url():

    endpoint = "/recommendations?userID=:userID&feature=:feature&currentItemID&fullyQualifyImageUrls=:fullyQualifyImageUrls"
    params = {
        **DEFAULT_PARAMS,
        ":fullyQualifyImageUrls": 1
    }
    response = get_request_assert(recommendations_api_url, endpoint, schemas_path, params)
    recommendation_resp_obj = response.json()
    image_field = recommendation_resp_obj[0]["product"]["image"]

    assert_that(validators.url(image_field))