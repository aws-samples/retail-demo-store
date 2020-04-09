# Retail Demo Store Carts Service

The Carts web service provides a RESTful API for adding, changing, and deleting shopping carts. The [Web UI](../web-ui) makes calls to this service as a user adds and removes products to their cart and during checkout.

When deployed to AWS, CodePipeline is used to build and deploy the Carts service as a Docker container to Amazon ECS behind an Application Load Balancer. The Carts service can also be run locally in a Docker container. This makes it easier to iterate on and test changes locally before commiting.

## Local Development

The Carts service can be built and run locally (in Docker) using Docker Compose. See the [local development instructions](../) for details. **From the `../src` directory**, run the following command to build and deploy the service locally.

```console
foo@bar:~$ docker-compose up --build carts
```

Once the container is up and running, you can access it in your browser or with a utility such as [Postman](https://www.postman.com/) at [http://localhost:8003](http://localhost:8003).
