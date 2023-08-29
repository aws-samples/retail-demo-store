# Retail Demo Store Orders Service

The Orders web service provides a RESTful API for creating and retrieving orders. The [Web UI](../web-ui) makes calls to this service when a user goes through the checkout process or when viewing their orders.

When deployed to AWS, CodePipeline is used to build and deploy the Orders service as a Docker container to Amazon ECS behind an Application Load Balancer. The Orders service can also be run locally in a Docker container. This makes it easier to iterate on and test changes locally before commiting.

## Local Development

The Orders service can be built and run locally (in Docker) using Docker Compose. See the [local development instructions](../) for details. **From the `../src` directory**, run the following command to build and deploy the service locally.

```console
foo@bar:~$ docker-compose up --build orders
```

Once the container is up and running, you can access it in your browser or with a utility such as [Postman](https://www.postman.com/) at [http://localhost:8004](http://localhost:8004).

## Testing
To run integration tests for the Orders service a Python virtual environment is required. You must have Python 3.8+ installed on your system to run the commands below. The commands are written to be ran from the test directory of the orders service (`src/orders/test`).

The following command will create a virtual environment. 
```console
python3 -m venv .venv
```

Some environment variables are required to run the tests and need to be added to the virtual environment. The example below will work for local development. Change as required depending on environment.
```console
echo '
export ORDERS_API_URL="http://localhost:8004"
export TEST_ORDER_ID="1"
export TEST_USERNAME="user1344"' >> .venv/bin/activate
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
pytest integ/test-orders.py
```

You can exit the virtual environment with `deactivate`.

If you want to edit the request bodies for any of the `PUT` or `POST` request tests you can do so in `json_request_bodies.json`