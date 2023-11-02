# Retail Demo Store Offers Service

The Offers web service provides a RESTful API for retrieving coupons. 

To see this used, see "Retail Geofencing and Location-aware Personalization"
in the in-app Demo Guide. 

When deployed to AWS, CodePipeline is used to build and deploy the Offers service as a Docker container to Amazon ECS behind an Application Load Balancer. The Offers service can also be run locally in a Docker container. This makes it easier to iterate on and test changes locally before commiting.

## Local Development

The Offers service can be built and run locally (in Docker) using Docker Compose. See the [local development instructions](../) for details. **From the `../src` directory**, run the following command to build and deploy the service locally.

```console
foo@bar:~$ docker compose up --build offers
```

Once the container is up and running, you can access it in your browser or with a utility such as [Postman](https://www.postman.com/) at [http://localhost:8008](http://localhost:8008).
