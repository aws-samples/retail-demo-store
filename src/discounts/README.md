# Retail Demo Store Discounts Service

The Discounts web service provides a RESTful API for retrieving discount coupons. The [Web UI](../web-ui) makes calls to this service when a user performs a search. Internally, this service makes calls to an [Elasticsearch](https://www.elastic.co/) cluster for search results. When deployed on AWS, [Amazon Elasticsearch Service](https://aws.amazon.com/elasticsearch-service/) is used. When deployed locally, a local Elasticsearch node is used for searches.

When deployed to AWS, CodePipeline is used to build and deploy the Search service as a Docker container to Amazon ECS behind an Application Load Balancer. The Search service can also be run locally in a Docker container. This makes it easier to iterate on and test changes locally before commiting.

## Local Development

The Discounts service can be built and run locally (in Docker) using Docker Compose. See the [local development instructions](../) for details. **From the `../src` directory**, run the following command to build and deploy the service locally.

```console
foo@bar:~$ docker-compose up --build discounts
```

Once the container is up and running, you can access it in your browser or with a utility such as [Postman](https://www.postman.com/) at [http://localhost:8006](http://localhost:8006).
