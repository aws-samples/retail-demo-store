import os
import json
from assertpy import assert_that
from test_recommendations import get_request_assert, post_request_assert

CHOOSE_DISCOUNTED_API_PATH = "/choose_discounted"
COUPON_OFFER_API_PATH = "/coupon_offer"
cwd = os.path.dirname(os.path.abspath(__file__))

def read_file(path, api_path):
    filepath = os.path.join(cwd, path)
    with open(filepath) as f:
        body = json.loads(f.read())[api_path]
    return body

input_request_body = read_file("json_request_bodies.json", CHOOSE_DISCOUNTED_API_PATH)


def count_discounted(items):
    count = 0
    for item in items:
        if item['discounted']:
            count += 1
    return count


def test_post_choose_discounted_should_return_with_correct_schema():
    post_request_assert(CHOOSE_DISCOUNTED_API_PATH) 


def test_post_choose_discounted_should_return_two_items_with_discount():
    response = post_request_assert(CHOOSE_DISCOUNTED_API_PATH) 
    items = response.json()
    
    discounted = count_discounted(items)
    assert_that(discounted).is_equal_to(2)


def test_get_coupon_offer_should_return_with_correct_schema():
    get_request_assert(f'{COUPON_OFFER_API_PATH}?userID=5097')
