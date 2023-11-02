# Retail Demo Store Carts Service

The Carts web service provides a RESTful API for adding, changing, and deleting shopping carts. The [Web UI](../web-ui) makes calls to this service as a user adds and removes items from their cart and during checkout.

When deployed to AWS, CodePipeline is used to build and deploy the Carts service as a Docker container to Amazon ECS behind an Application Load Balancer. The Carts service can also be run locally in a Docker container. This makes it easier to iterate on and test changes locally before commiting.

## Local Development


```console
foo@bar:~$ docker compose up --build -d carts
```

Once the container is up and running, you can access it in your browser or with a utility such as [Postman](https://www.postman.com/) at [http://localhost:8003](http://localhost:8003).

## Testing
To run integration tests for the carts service a Python virtual environment and local dynamodb is required. You must have Python 3.8+ installed on your system to run the commands below. The commands are written to be ran from the test directory of the carts service (`src/carts/test`).

### Run Tests
To run integration tests for the carts service a Python virtual environment is required. You must have Python 3.8+ installed on your system to run the commands below. The commands are written to be ran from the test directory of the carts service (`src/carts/test`).

The following command will create a virtual environment. 
```console
python3 -m venv .venv
```

Some environment variables are required to run the tests and need to be added to the virtual environment. The example below will work for local development. Change as required depending on environment.
```console
echo '
export CARTS_API_URL="http://localhost:8003"
export TEST_USERNAME="user1344"'>> .venv/bin/activate
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
pytest integ/test_carts.py
```

You can exit the virtual environment with `deactivate`.

If you want to edit the request bodies for any of the `PUT` or `POST` request tests you can do so in `json_request_bodies.json`
