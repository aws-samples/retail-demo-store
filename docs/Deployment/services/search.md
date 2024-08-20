# Search Service

The Search web service provides a RESTful API for retrieving product information based on a search term. The [Web UI](../local-development/0-local-development-instructions.md) makes calls to this service when a user performs a search. Internally, this service makes calls to an [OpenSearch](https://opensearch.org/) cluster for search results. When deployed on AWS, [Amazon OpenSearch Service](https://aws.amazon.com/opensearch-service/) is used. When deployed locally, a local OpenSearch node is used for searches.

When the Search service and Amazon OpenSearch are initially deployed to your AWS account, product information is not present in an index and therefore searches from the Web UI will not return results. There are two options for indexing products in OpenSearch when deploying to AWS. First, when deploying the Retail Demo Store project, the CloudFormation template has an option to index the product catalog in OpenSearch as part of the deployment process. The second option is to step through the [Search](https://github.com/aws-samples/retail-demo-store/tree/master/workshop/0-StartHere/Search.ipynb) workshop.

When deployed to AWS, CodePipeline is used to build and deploy the Search service as a Docker container to Amazon ECS behind an Application Load Balancer. The Search service can also be run locally in a Docker container. This makes it easier to iterate on and test changes locally before commiting.

## Local Development

The Search service can be built and run locally (in Docker) using Docker Compose. See the [local development instructions](../local-development/0-local-development-instructions.md) for details. **From the `../src` directory**, run the following command to build and deploy OpenSearch and the Search service locally.

```console
foo@bar:~$ docker compose up --build opensearch search
```

Once the container is up and running, you can access it in your browser or with a utility such as [Postman](https://www.postman.com/) at [http://localhost:8006](http://localhost:8006).

### Indexing Products Locally

As explained above, when the Search service and OpenSearch are deployed, the product information does not exist in an OpenSearch index. When deploying locally, you can use the [local_index_products.py](https://github.com/aws-samples/retail-demo-store/tree/master/src/search/local_index_products.py) script after starting the `opensearch` Docker container to create and load the products index.