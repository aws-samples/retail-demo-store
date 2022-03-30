from assertpy import assert_that
from test_recommendations import get_request_assert

CURRENT_ITEM_ID = '89728417-5269-403d-baa3-04b59cdffd0a'
# If Optimizely is configured, this field will be used to select a specific Experiment. 
# The default deployment doesn't have Optmizely so this value doesn't affect the result.
FEATURE = 'product_detail_related' 

def test_get_related_with_default_params_should_return_a_non_empty_list_of_product():
    response = get_request_assert(
        f"/related?userID=:userID&feature={FEATURE}&currentItemID={CURRENT_ITEM_ID}"
    )
    related_resp_obj = response.json()

    assert_that(related_resp_obj).is_not_empty()

def test_get_related_with_numResults_params_should_return_exact_number_of_result():
    num_results = 3

    response = get_request_assert(
        f"/related?userID=:userID&feature={FEATURE}&currentItemID={CURRENT_ITEM_ID}&numResults={num_results}"
    )
    related_resp_obj = response.json()

    assert_that(related_resp_obj).is_length(num_results)


def test_get_related_should_return_image_filename_by_default():
    response = get_request_assert(f"/related?userID=:userID&feature={FEATURE}&currentItemID={CURRENT_ITEM_ID}")
    recommendation_resp_obj = response.json()
    image_field = recommendation_resp_obj[0]["product"]["image"]
    assert_that(image_field.startswith("http://")).is_false()
    
    
def test_get_related_with_fullyQualifyImageUrls_should_return_image_url():
    response = get_request_assert(f"/related?userID=:userID&feature={FEATURE}&currentItemID={CURRENT_ITEM_ID}&fullyQualifyImageUrls=1")
    recommendation_resp_obj = response.json()
    image_field = recommendation_resp_obj[0]["product"]["image"]
    assert_that(image_field).starts_with('http://')
    