# Local Development Instructions

The Retail Demo Store's web services such as [users](https://github.com/aws-samples/retail-demo-store/tree/master/src/users), [carts](https://github.com/aws-samples/retail-demo-store/tree/master/src/carts), [orders](https://github.com/aws-samples/retail-demo-store/tree/master/src/orders), [products](https://github.com/aws-samples/retail-demo-store/tree/master/src/products), and others can be run locally on your development system using [Docker Compose](https://docs.docker.com/compose/). You can choose to run them all locally or just one or two locally and the rest running in your AWS account. For example, suppose you're working on an enhancement or fix in the [products](https://github.com/aws-samples/retail-demo-store/tree/master/src/products) service. You can run just that service locally to test your changes while all of the other services are running in your AWS account. If your changes require UI testing, you can run the [web-ui](https://github.com/aws-samples/retail-demo-store/tree/master/src/web-ui) in a local container as well configured to connect to your local product service instance while still having both of them connect to the other services running in your AWS account.

Before you can run the Retail Demo Store web services locally, you must first deploy the Retail Demo Store project to your AWS account and then clone this repository to your local machine. The instructions below provide additional details on configuration and how to setup the services to run locally. The [docker-compose.yml](https://github.com/aws-samples/retail-demo-store/tree/master/src/docker-compose.yml) file includes the configuration used by Docker Compose. Note that there are some dependencies between services which are noted.

## Configuring your Environment

Besides cloning this repository to your local system, you also need to have the AWS CLI [installed](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html) and [configured](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html) locally.

Docker Compose will load the `.env` file to resolve environment variables referenced in the [docker-compose.yml](https://github.com/aws-samples/retail-demo-store/tree/master/src/docker-compose.yml) file. You can copy the [.env.template](https://github.com/aws-samples/retail-demo-store/tree/master/src/.env.template) file to .env
as a starting point. This is where you can customize variables to match your desired configuration.

You can find the common environment variables from your deployed stack in the CloudFormation output name `ExportEnvVarScript`. Use this CLI to get the output in a proper format.

```sh
aws cloudformation describe-stacks --stack-name retaildemostore \
  --region REGION \
  --query "Stacks[0].Outputs[?OutputKey=='ExportEnvVarScript'].OutputValue" \
  --output text
```

Then you can copy and override variables for each service in your .env file.


### Amazon ECR authorization

Since some of the Docker images are hosted in Amazon ECR, you must authenticate your shell session before running docker-compose. Otherwise, the images will not be able to be downloaded. Run the following command to authenticate before running docker-compose. You should only have to do this once per shell session.

```sh
aws ecr-public get-login-password --region us-east-1 | docker login --username AWS --password-stdin public.ecr.aws
```

### AWS credentials

Docker compose will pick variables set in your shell when building and launching the services. Make sure you set the correct environement variables in your shell before doing the docker compose up command. You can find more information about all the different ways of setting aws credentials in this [documentation](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html)

```
export AWS_ACCESS_KEY_ID=xxx
export AWS_SECRET_ACCESS_KEY=xxx
export AWS_SESSION_TOKEN=xxx
```


## Run All Services

The following command will build and launch all Retail Demo Store web services in your local Docker engine.

```console
docker compose up --build
```

## Run Specific Services

You can also choose to run specific services locally by appending the service names to the above command. For example, the following command builds and launches the [products](https://github.com/aws-samples/retail-demo-store/tree/master/src/products) and [web-ui](https://github.com/aws-samples/retail-demo-store/tree/master/src/web-ui) services only. Note that some configuration of the [web-ui](https://github.com/aws-samples/retail-demo-store/tree/master/src/web-ui) environment will likely be needed to match your configuration.

```console
docker compose up --build products web-ui
```

For instructions specific to each Retail Demo Store web service, view the README page in each service sub-directory.

## Web UI Service

When deployed to AWS, the Web UI is hosted in an S3 bucket and served by CloudFront. For local development, you can deploy the Web UI in a Docker container. Since the Web UI makes REST API calls to all of the other services, you can configure the `web-ui/.env` file for which there is an example at ``web-ui/.env.template`` to point to services running either locally or deployed on AWS or a combination. Just update the appropiate environment variables to match your desired configuration.

!!! Note
    If you are going to work on frontend updates, instead of using docker you can run:
    ```
    npm install
    npm run dev
    ```
    Which makes frontend development easier


## Swagger UI

There is a `swagger-ui` service in the `docker-compose.yml`. You can access it via [localhost:8081](http://localhost:8081). From there, you can select which service you want to check and send request against the service via Swagger UI.

The `Dockerfile` of `swagger-ui` copies OpenAPI spec from each service (located at `<serviceName>/openapi/spec.yaml`). If you add a new service, please ensure that you write the OpenAPI spec and update the `Dockerfile` to copy yours.