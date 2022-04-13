import testhelpers.integ as integhelpers
import time
import requests
import os

cwd = os.path.dirname(os.path.abspath(__file__))
request_bodies_path = integhelpers.absolute_file_path(cwd, "json_request_bodies.json")
schemas_path = integhelpers.absolute_file_path(cwd, "json_schemas.json")
users_api_url = os.getenv('USERS_API_URL')


def test_get_users_all():

    endpoint = "/users/all"
    integhelpers.get_request_assert(users_api_url, endpoint, schemas_path)


def test_get_users_id():

    endpoint = "/users/id/:user_id"
    params = {":user_id": os.getenv('TEST_USER_ID')}
    integhelpers.get_request_assert(users_api_url, endpoint, schemas_path, params)


def test_put_users_id():

    endpoint = "/users/id/:user_id"
    params = {":user_id": os.getenv('TEST_USER_ID')}
    integhelpers.put_request_assert(users_api_url, endpoint, request_bodies_path, schemas_path, params)


def test_put_users_id_claim():

    endpoint = "/users/id/:user_id/claim"
    params = {":user_id": os.getenv('TEST_USER_ID')}
    r = requests.put(integhelpers.full_request_url(users_api_url, endpoint, params))

    assert str(r.status_code).startswith("2")
    assert 'true' in r.text


# Test disabled until known issue with this endpoint is resolved
# def test_put_users_id_verify_phone():
#
#     endpoint = "/users/id/:user_id/verifyphone"
#     params = {":user_id": os.getenv('TEST_USER_ID')}
#     integhelpers.put_request_assert(users_api_url, endpoint, request_bodies_path, schemas_path, params)


def test_post_users():

    endpoint = "/users"
    id = str(time.time())
    params = {":user_id": id, ":username": "user" + id}
    integhelpers.post_request_assert(users_api_url, endpoint, request_bodies_path, schemas_path, params)


def test_get_users_username():

    endpoint = "/users/username/:username"
    params = {":username": os.getenv('TEST_USERNAME')}
    integhelpers.get_request_assert(users_api_url, endpoint, schemas_path, params)


def test_get_users_identity_id():

    endpoint = "/users/identityid/:identity_id"
    params = {":identity_id": os.getenv('TEST_IDENTITY_ID')}
    integhelpers.get_request_assert(users_api_url, endpoint, schemas_path, params)


def test_get_users_unclaimed():

    endpoint = "/users/unclaimed?primaryPersona=:primary_persona&ageRange=:age_range"
    params = {":primary_persona": os.getenv('TEST_PRIMARY_PERSONA'), ":age_range": os.getenv("TEST_AGE_RANGE")}
    integhelpers.get_request_assert(users_api_url, endpoint, schemas_path, params)


def test_get_users_random():

    endpoint = "/users/random"
    integhelpers.get_request_assert(users_api_url, endpoint, schemas_path)
