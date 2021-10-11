# Retail Demo Store Orders Service

The Orders web service provides a RESTful API for creating and retrieving orders. The [Web UI](../web-ui) makes calls to this service when a user goes through the checkout process or when viewing their orders.

When deployed to AWS, CodePipeline is used to build and deploy the Orders service as a Docker container to Amazon ECS behind an Application Load Balancer. The Orders service can also be run locally in a Docker container. This makes it easier to iterate on and test changes locally before commiting.

## Local Development

The Orders service can be built and run locally (in Docker) using Docker Compose. See the [local development instructions](../) for details. Since the Orders service has a dependency on DynamoDB as its datastore, you can either connect to DynamoDB in your AWS account or run DynamoDB [locally](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.html) (default). The [docker-compose.yml](../docker-compose.yml) and template `.env` ([.env.template](../.env.template)) is already setup to run DynamoDB locally in Docker. If you want to connect to the real DynamoDB instead, you will need to configure your AWS credentials and comment the `DDB_ENDPOINT_OVERRIDE` environment variable since it is checked first. **From the `../src` directory**, run the following command to build and deploy the service locally.

```console
foo@bar:~$ docker-compose up --build orders
```

Once the container is up and running, you can access it in your browser or with a utility such as [Postman](https://www.postman.com/) at [http://localhost:8004](http://localhost:8004).
