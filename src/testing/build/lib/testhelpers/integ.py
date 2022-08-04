import jsonschema
import requests
import json
import os


def full_request_url(base, text, wildcards={}):
    """
    Build a full request URL from the API URL and endpoint.
    Any URL parameters will be replaced with the value set in the environment variables.
    """
    for key in wildcards.keys():
        text = text.replace(key, str(wildcards[key]))
    print(f'########')
    print(str(base) + str(text))
    return str(base) + str(text)


def absolute_file_path(cwd, filename):
    """
    Join a filename in the same directory as this function with the current working directory for the absolute path.
    """
    return os.path.join(cwd, filename)


def read_file(path, key):
    """
    Read a json file and return the part of the body linked to a key
    """
    with open(path) as f:
        body = json.loads(f.read())[key]
    return body


def get_request_assert(base, endpoint, validation_file, endpoint_params={}):
    """
    Send a GET request and assert response meets expectations.
    """
    r = requests.get(full_request_url(base, endpoint, endpoint_params))
    assertions(r, endpoint, validation_file)
    return r


def put_request_assert(base, endpoint, request_file, validation_file, endpoint_params={}):
    """
    Send a PUT request and assert response meets expectations.
    """
    body = read_file(request_file, endpoint)
    r = requests.put(full_request_url(base, endpoint, endpoint_params), data=json.dumps(body))
    assertions(r, endpoint, validation_file)
    return r


def post_request_assert(base, endpoint, request_file, validation_file, endpoint_params={}):
    """
    Send a POST request and assert response meets expectations.
    """
    body = read_file(request_file, endpoint)
    r = requests.post(full_request_url(base, endpoint, endpoint_params), data=json.dumps(body),
                      headers={"Content-Type": "application/json", "Accept": "appllication/json"})
    assertions(r, endpoint, validation_file)
    return r


def delete_request_assert(base, endpoint, validation_file, endpoint_params={}):
    """
    Send a DELETE request and assert response meets expectations.
    """
    r = requests.delete(full_request_url(base, endpoint, endpoint_params))
    assertions(r, endpoint, validation_file)
    return r


def assertions(r, endpoint, schemas_path):
    """
    Assert response is successful and validate response body when applicable.
    """
    assert str(r.status_code).startswith("2")
    if r.headers["Content-Type"].startswith("application/json") or r.headers["Content-Type"].startswith("text/plain"):
        assert validate_schema(r.text, endpoint, schemas_path) is True
    else:
        assert False


def validate_schema(json_str, endpoint, validation_file):
    """
    Validate a JSON response body against a schema.
    """
    schema = read_file(validation_file, endpoint.split('?', 1)[0])
    jsonschema.validate(json.loads(json_str), schema)
    return True
