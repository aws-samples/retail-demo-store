import os
from assertpy import assert_that
from testhelpers.integ import (
    absolute_file_path,
    get_request_assert,
    post_request_assert,
    read_file
)
from dotenv import load_dotenv

load_dotenv()

DEFAULT_LOCAL_API = 'http://localhost:8005'

cwd = os.path.dirname(os.path.abspath(__file__))
request_bodies_path = absolute_file_path(cwd, "json_request_bodies.json")
schemas_path = absolute_file_path(cwd, "json_schemas.json")
recommendations_api_url = os.getenv("RECOMMENDATIONS_API_URL", DEFAULT_LOCAL_API)

input_request_body = read_file(request_bodies_path, "/choose_discounted")


def count_discounted(items):
    count = 0
    for item in items:
        if item["discounted"]:
            count += 1
    return count


def test_post_choose_discounted_should_return_with_correct_schema():
    endpoint = "/choose_discounted"
    post_request_assert(
        recommendations_api_url, endpoint, request_bodies_path, schemas_path
    )


def test_post_choose_discounted_should_return_two_items_with_discount():
    endpoint = "/choose_discounted"
    response = post_request_assert(
        recommendations_api_url, endpoint, request_bodies_path, schemas_path
    )
    items = response.json()

    discounted = count_discounted(items)
    assert_that(discounted).is_equal_to(2)


def test_get_coupon_offer_should_return_with_correct_schema():
    endpoint = "/coupon_offer?userID=:userID"
    params = {":userID": "5097"}
    get_request_assert(recommendations_api_url, endpoint, schemas_path, params)
