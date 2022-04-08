# Retail Demo Store Users Service

The Users web service provides a RESTful API for creating, updating, and retrieving users. The [Web UI](../web-ui) makes calls to this service when a user signs up or updates their profile.

When deployed to AWS, CodePipeline is used to build and deploy the Users service as a Docker container to Amazon ECS behind an Application Load Balancer. The Users service can also be run locally in a Docker container. This makes it easier to iterate on and test changes locally before commiting.

## User Test Data

The Users service comes preloaded with 5,000 fake user profiles. The [generate_users_json.py](../../generators/generate_users_json.py) script was used to create these profiles. The resulting profiles data file is bundled with the Retail Demo Store deployment. Therefore, you should not need to run the generate users script under normal conditions.

> The reason why so many profiles are preloaded is to support the sample sizes needed to simulate experiements in the [Experimentation](../../workshop/3-Experimentation/3.1-Overview.ipynb) workshops.

## Local Development

The Users service can be built and run locally (in Docker) using Docker Compose. See the [local development instructions](../) for details. **From the `../src` directory**, run the following command to build and deploy the service locally.

```console
foo@bar:~$ docker-compose up --build users
```

Once the container is up and running, you can access it in your browser or with a utility such as [Postman](https://www.postman.com/) at [http://localhost:8002](http://localhost:8002).

## Testing
To run integration tests for the Users service a Python virtual environment is required. You must have Python 3.8+ installed on your system to run the commands below. The commands are written to be ran from the test directory of the Users service (`src/users/test`).

The following command will create a virtual environment. 
```console
python3 -m venv .venv
```

Some environment variables are required to run the tests and need to be added to the virtual environment. The example below will work for local development. Change as required depending on environment.
```console
echo '
export USERS_API_URL="http://localhost:8002"
export TEST_USER_ID="1"
export TEST_USERNAME="user1"
export TEST_IDENTITY_ID="eu-west-1:12345678-1234-1234-1234-c777c9720775"
export TEST_PRIMARY_PERSONA="tools"
export TEST_AGE_RANGE="18-24"' >> .venv/bin/activate
```

To activate and enter the virtual environment.
```console
source .venv/bin/activate
```

To install requirements for the integration tests.
```console
pip install -r integ/requirements.txt
```

To run the tests.
```console
pytest integ/test-users.py
```

You can exit the virtual environment with `deactivate`.

If you want to edit the request bodies for any of the `PUT` or `POST` request tests you can do so in `json_request_bodies.json`