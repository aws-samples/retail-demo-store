# Retail Demo Store Products Service

The Products web service provides a RESTful API for retrieving product information. The [Web UI](../web-ui) makes calls to this service when a user is viewing products and categories.

When deployed to AWS, CodePipeline is used to build and deploy the Products service as a Docker container to Amazon ECS behind an Application Load Balancer. The Products service can also be run locally in a Docker container. This makes it easier to iterate on and test changes locally before commiting.

## Local Development

The Products service can be built and run locally (in Docker) using Docker Compose. See the [local development instructions](../) for details. **From the `../src` directory**, run the following command to build and deploy the service locally.

```console
foo@bar:~$ docker-compose up --build products
```

Once the container is up and running, you can access it in your browser or with a utility such as [Postman](https://www.postman.com/) at [http://localhost:8001](http://localhost:8001).
