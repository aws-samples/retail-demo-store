# Local Development Instructions

The Retail Demo Store's web services such as [users](./users), [carts](./carts), [orders](./orders), [products](./products), and others can be run locally on your development system using [Docker Compose](https://docs.docker.com/compose/). You can choose to run them all locally or just one or two locally and the rest running in your AWS account. For example, suppose you're working on an enhancement or fix in the [products](./products) service. You can run just that service locally to test your changes while all of the other services are running in your AWS account. If your changes require UI testing, you can run the [web-ui](./web-ui) in a local container as well configured to connect to your local product service instance while still having both of them connect to the other services running in your AWS account.

Before you can run the Retail Demo Store web services locally, you must first deploy the Retail Demo Store project to your AWS account and then clone this repository to your local machine. The instructions below provide additional details on configuration and how to setup the services to run locally. The [docker-compose.yml](./docker-compose.yml) file includes the configuration used by Docker Compose. Note that there are some dependencies between services which are noted.

## Configuring your Environment

Besides cloning this repository to your local system, you also need to have the AWS CLI [installed](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html) and [configured](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html) locally.

Docker Compose will load the [.env](./.env) file to resolve environment variables referenced in the [docker-compose.yml](./docker-compose.yml) file. This is where you can customize variables to match your desired configuration.

### AWS credentials

Some services, such as the [products](./products) and [recommendations](./recommendations) services, need to access AWS services running in your AWS account from your local machine. Given the differences between these container setups, different approaches are needed to pass in the AWS credentials needed to make these connections. For example, for the recommendations service we can map your local `~./.aws` configuration directory into the container's `/root` directory so the AWS SDK in the container can pick up the credentials it needs. Alternatively, since the products service is packaged from a [scratch image](https://hub.docker.com/_/scratch), credentials must be passed using the `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_SESSION_TOKEN` environment variables. In this case, rather than setting these variables in `.env` and risk exposing these values, consider setting these three variables in your shell environment. The following command can be used to obtain a session token which can be used to set your environment variables in your shell.

```console
foo@bar:~$ aws sts get-session-token
```

Docker compose will still pick variables set in your shell when building and launching the services.

## Run All Services

The following command will build and launch all Retail Demo Store web services in your local Docker engine.

```console
foo@bar:~$ docker-compose up --build
```

## Run Specific Services

You can also choose to run specific services locally by appending the service names to the above command. For example, the following command builds and launches the [products](./products) and [web-ui](./web-ui) services only. Note that some configuration of the [web-ui](./web-ui) environment will likely be needed to match your configuration.

```console
foo@bar:~$ docker-compose up --build products web-ui
```

For instructions specific to each Retail Demo Store web service, view the README page in each service sub-directory.

## Web UI Service

When deployed to AWS, the Web UI is hosted in an S3 bucket and served by CloudFront. For local development, you can deploy the Web UI in a Docker container. Since the Web UI makes REST API calls to all of the other services, you can configure the [Web UI's .env](./web-ui/.env) file to point to services running either locally or deployed on AWS or a combination. Just update the appropiate environment variables to match your desired configuration.
