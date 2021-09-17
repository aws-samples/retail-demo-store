# Retail Demo Store Products Service

The Products web service provides a RESTful API for retrieving product information. The [Web UI](../web-ui) makes calls to this service when a user is viewing products and categories and the Personalize workshop connects to this service to retrieve product information for building the items dataset.

When deployed to AWS, CodePipeline is used to build and deploy the Products service as a Docker container in Amazon ECS behind an Application Load Balancer. The Products service can also be run locally in a Docker container. This makes it easier to iterate on and test changes locally before commiting.

## Local Development

The Products service can be built and run locally (in Docker) using Docker Compose. See the [local development instructions](../) for details. Since the Products service has a dependency on DynamoDB as its datastore, you can either connect to DynamoDB in your AWS account or run DynamoDB [locally](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.html) (default). The [docker-compose.yml](../docker-compose.yml) and template `.env` ([.env.template](../.env.template)) is already setup to run DynamoDB locally in Docker. If you want to connect to the real DynamoDB instead, you will need to configure your AWS credentials and comment the `DDB_ENDPOINT_OVERRIDE` environment variable since it is checked first. **From the `../src` directory**, run the following command to build and deploy the service locally.

```console
foo@bar:~$ docker-compose up --build products
```

Once the container is up and running, you can access it in your browser or with a utility such as [Postman](https://www.postman.com/) at [http://localhost:8001](http://localhost:8001).

## Products API
The following entrypoints are supported by the Products service

### GET /
Displays the service welcome page.

### GET /products/all
Returns details on all products.
### GET /products/id/{productIDs}
Returns details on the product(s) identified by `{productIDs}`. Multiple product IDs can be specified by separating each product ID by a comma. If a single product ID is specified, a single product will be returned. Otherwise, if multiple product IDs are specified, an array of products will be returned.
### GET /products/featured
Returns details on all featured products. Featured products are those with featured attribute equal to true.
### GET /products/category/{categoryName}
Returns details on all products within the category with the name `{categoryName}`.
### PUT /products/id/{productID}
Updates the product identified by `{productID}`.
### DELETE /products/id/{productID}
Deletes the product identified by `{productID}`.
### POST /products
Creates a new product.
### PUT /products/id/{productID}/inventory
Updates the current inventory value for the product identified by `{productID}`.
### GET /categories/all
Returns details on all categories.
### GET /categories/id/{categoryID}
Returns details on the category identified by `{categoryID}`.
