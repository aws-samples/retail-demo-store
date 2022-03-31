from assertpy import assert_that
import os
from test_recommendations import get_request_assert

# TODO: this path seem to duplicate with /recommendations. 
# Waiting for James' confirmation on this

API_PATH = 'popular'
DEFAULT_TEST_FEATURE = "product_detail_related"
DEFAULT_TEST_USER_ID = 5097
BASE_PATH = f"/{API_PATH}?userID={DEFAULT_TEST_USER_ID}&feature={DEFAULT_TEST_FEATURE}"

def test_get_populars_should_return_products_with_correct_schema():
    get_request_assert(BASE_PATH)


def test_get_popular_with_numResults_should_return_exact_number_of_result():
    num_results = 3

    response = get_request_assert(
        f"{BASE_PATH}&numResults={num_results}"
    )
    recommendation_resp_obj = response.json()

    assert_that(recommendation_resp_obj).is_length(num_results)


def test_get_popular_with_currentItemID_should_return_different_product():
    # Calling without "currentItemID" param should get this product id

    response = get_request_assert(BASE_PATH)
    recommendation_resp_obj = response.json()
    first_item_id_without_param = recommendation_resp_obj[0]["product"]["id"]

    # Calling with this "currentItemID" param should get another product id
    currentItemID = "89728417-5269-403d-baa3-04b59cdffd0a"

    response = get_request_assert(
        f"{BASE_PATH}&currentItemID={currentItemID}"
    )
    recommendation_resp_obj = response.json()
    first_item_id = recommendation_resp_obj[0]["product"]["id"]

    assert_that(first_item_id).is_not_equal_to(first_item_id_without_param)


def test_get_popular_should_return_image_filename_by_default():
    response = get_request_assert(BASE_PATH)
    recommendation_resp_obj = response.json()
    image_field = recommendation_resp_obj[0]["product"]["image"]
    assert_that(image_field.startswith("http://")).is_false()
    
    
def test_get_popular_with_fullyQualifyImageUrls_should_return_image_url():
    response = get_request_assert(f"{BASE_PATH}&fullyQualifyImageUrls=1")
    recommendation_resp_obj = response.json()
    image_field = recommendation_resp_obj[0]["product"]["image"]
    assert_that(image_field).starts_with('http://')
