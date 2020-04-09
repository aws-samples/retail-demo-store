# Retail Demo Store Recommendations Service

The Recommendations web service provides a RESTful API for retrieving personalized product recommendations and related products (powered by Amazon Personalize). The [Web UI](../web-ui) makes calls to this service when a user is viewing the home view (recommended products), product detail view (related products), or the category view (personalized ranking of products). If Amazon Personalize campaigns have been created for these use-cases (either by the deployment Lambda option or by stepping through the [Personalization](../../workshop/1-Personalization/1.1-Personalize.ipynb) workshop), then those campaigns will be called by the Recommendations service. Otherwise, the service will call the [Products](../products) service to provide a suitable default behavior such as displaying featured products or products from the same category as the displayed product.

This service also provides support for running experiments for personalization approaches using techniques such as A/B testing, interleaving results testing, and multi-armed bandit testing. The [Experimentation](../../workshop/3-Experimentation/3.1-Overview.ipynb) workshops are designed to walk you through how to setup, run, and evaluate experiments.

When deployed to AWS, CodePipeline is used to build and deploy the Recommendations service as a Docker container to Amazon ECS behind an Application Load Balancer. The Recommendations service can also be run locally in a Docker container. This makes it easier to iterate on and test changes locally before commiting.

## Local Development

The Recommendations service can be built and run locally (in Docker) using Docker Compose. See the [local development instructions](../) for details. **From the `../src` directory**, run the following command to build and deploy the service locally.

```console
foo@bar:~$ docker-compose up --build recommendations
```

Once the container is up and running, you can access it in your browser or with a utility such as [Postman](https://www.postman.com/) at [http://localhost:8005](http://localhost:8005).
