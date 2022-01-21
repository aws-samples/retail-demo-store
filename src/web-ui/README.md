# Retail Demo Store Web UI

When deployed to AWS, CodePipeline is used to build and deploy the Retail Demo Store's Web UI to a private S3 bucket and a CloudFront distribution is used to serve the Web UI to end users. The Web UI can also be run locally in a Docker container. This makes it easier to iterate on and test changes locally before commiting.

## Local Development

The Web UI service can be built and run locally (in Docker) using Docker Compose. See the [local development instructions](../) for details. Note that you still must first deploy the Retail Demo Store project to AWS to satisfy resource dependencies.

To get your local Web UI container to make calls to other Retail Demo Store web services (either running locally in Docker or in ECS on AWS or a combination of the two) and AWS resources such as Cognito, Pinpoint, or a Personalize Event Tracker, you will need to copy the environment variables in the [.env](./env) file on your local system to match your desired configuration. If you want your local instance of web-ui to connect to resources running in your AWS account, follow these steps to get up and running quickly.

1. Sign in to the AWS account where the Retail Demo Store is deployed.
2. Browse to the CodePipeline service. Make sure you're in the right region.
3. Under Pipelines, find the pipeline with "WebUIPipeline" in the name and click on its name.
4. You should now see the stages for the "WebUIPipeline" listed: Source and Build. For the "Build" stage, click on the "Details" link in the "Build" box.
5. In the "Build logs" tab, scroll down through the build log output until you see the output for the `cat .env` command. You should see a block of several lines that start with `VUE_APP_...`. These lines represent the environment variables used when building the Web UI assets when deployed to S3. Select all of these lines (except the variables with `***` as their values--these are resolved as system parameters) with your mouse and copy them to your clipboard. Alternatively, if you only want to connect to some Retail Demo Store services in ECS and others running locally, just copy the lines that you need for remote services.
6. Open your local `.env` file and paste over the top of the lines you selected. There is already a [.env.template](.env.template) file with examples of what this would look like.

Once your `.env` is setup, run Docker Compose **from the `../src` directory** as described in the [local development instructions](../) to build and run the Web UI container locally.

```console
foo@bar:~$ docker-compose up --build web-ui
```

Once the container is up and running, you can access it in your browser at [http://localhost:8080](http://localhost:8080).

# Site Optimization with Layer0

- Layer0 documentation: https://docs.layer0.co
- AWS Retail Store on Layer0 demo: https://layer0-docs-layer0-aws-store-example-default.layer0-limelight.link
- Layer0 example app: https://github.com/layer0-docs/layer0-aws-store-example

## Prerequisites

Make sure you have Retail Demo Store (RDS) deployed in your AWS account before proceeding. These instructions will allow you to run a Layer0 enabled version of the `web-ui` on local or Layer0 as infratructure for the RDS front-end, connecting to the APIs deployed in your account.

Layer0 application works with the Vue application production build files.

To create it, follow the next steps.

1. Make sure your terminal is open in `%project_root%/src/web-ui` folder
2. Set NodeJS version to 14 (to check your version use `node -v`)
3. Install packages: run `npm install` (or just `npm i`)
4. Run `./gen_env.sh` to generate the `.env` file.
5. Set `VUE_APP_LAYER0_ENABLED` environment variable to `true` in `.env` file
6. Build Vue application: `npm run build` (build files will appear in `dist` folder)

## Development

Run Layer0 locally using one of the following modes:

1. `npm run layer0:start` - default run
2. `npm run layer0:start:cache` - run with cache
3. `npm run layer0:start:prod` - serve production files (requires Layer0 build before, see next section)

For local development, API endpoints set via your `.env` file should be pointed to the localhost Docker container instances.

An example is as follows:

````
VUE_APP_PRODUCTS_SERVICE_DOMAIN=http://localhost
VUE_APP_PRODUCTS_SERVICE_PORT=8001
VUE_APP_USERS_SERVICE_DOMAIN=http://localhost
VUE_APP_USERS_SERVICE_PORT=8002
VUE_APP_CARTS_SERVICE_DOMAIN=http://localhost
VUE_APP_CARTS_SERVICE_PORT=8003
VUE_APP_ORDERS_SERVICE_DOMAIN=http://localhost
VUE_APP_ORDERS_SERVICE_PORT=8004
VUE_APP_RECOMMENDATIONS_SERVICE_DOMAIN=http://localhost
VUE_APP_RECOMMENDATIONS_SERVICE_PORT=8005
VUE_APP_SEARCH_SERVICE_DOMAIN=http://localhost
VUE_APP_SEARCH_SERVICE_PORT=8006
VUE_APP_VIDEOS_SERVICE_DOMAIN=http://localhost
VUE_APP_VIDEOS_SERVICE_PORT=8007
VUE_APP_LOCATION_SERVICE_DOMAIN=http://localhost
VUE_APP_LOCATION_SERVICE_PORT=8009
AWS_IMAGE_SERVICE_DOMAIN=d28z1nhxyoq0l5.cloudfront.net # change to your deployed RDS
```

## Build

Make sure all the steps of [Prerequisites](#Prerequisites) section are done before building Layer0 files!

Update your `.env` file to point to the deployed RDS instance urls. For instance

To build Layer0 production files run `npm run layer0:build` (Layer0 build files will appear in `.layer0` & `dist-layer0` folders, main app build files appear in `dist`).

You will need to set up your deployed RDS instance with a few tweaks:

* Enable [HTTPs](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/create-https-listener.html) traffic on all ELBs as Layer0 enforces HTTPs on all calls
* Configure the local `.env` file with urls and paths set to the deployed RDS instance.

These point to the example Layer0 RDS deployment. Change to your own RDS links.

```
VUE_APP_PRODUCTS_SERVICE_DOMAIN=https://layer0-docs-layer0-aws-store-example-default.layer0-limelight.link
AWS_PRODUCTS_SERVICE_DOMAIN=retai-loadb-1riqp3qcaf983-1507012174.us-east-1.elb.amazonaws.com
VUE_APP_PRODUCTS_SERVICE_PATH=/products-service

VUE_APP_USERS_SERVICE_DOMAIN=https://layer0-docs-layer0-aws-store-example-default.layer0-limelight.link
AWS_USERS_SERVICE_DOMAIN=retai-loadb-eyuieam5ifpn-1823664657.us-east-1.elb.amazonaws.com
VUE_APP_USERS_SERVICE_PATH=/users-service

VUE_APP_CARTS_SERVICE_DOMAIN=https://layer0-docs-layer0-aws-store-example-default.layer0-limelight.link
AWS_CARTS_SERVICE_DOMAIN=retai-loadb-10bjeuwdanbi-1224031705.us-east-1.elb.amazonaws.com
VUE_APP_CARTS_SERVICE_PATH=/

VUE_APP_ORDERS_SERVICE_DOMAIN=https://layer0-docs-layer0-aws-store-example-default.layer0-limelight.link
AWS_ORDERS_SERVICE_DOMAIN=retai-LoadB-1U6KE7LXOQ5VU-1311015454.us-east-1.elb.amazonaws.com
VUE_APP_ORDERS_SERVICE_PATH=/orders-service

VUE_APP_RECOMMENDATIONS_SERVICE_DOMAIN=https://layer0-docs-layer0-aws-store-example-default.layer0-limelight.link
AWS_RECOMMENDATIONS_SERVICE_DOMAIN=retai-LoadB-1USGZMQVWHN1T-2000232934.us-east-1.elb.amazonaws.com
VUE_APP_RECOMMENDATIONS_SERVICE_PATH=/recommendations-service

VUE_APP_VIDEOS_SERVICE_DOMAIN=https://layer0-docs-layer0-aws-store-example-default.layer0-limelight.link
AWS_VIDEOS_SERVICE_DOMAIN=retai-LoadB-F2U2MQ3CXPD8-471493329.us-east-1.elb.amazonaws.com
VUE_APP_VIDEOS_SERVICE_SERVICE_PATH=/videos-service

VUE_APP_SEARCH_SERVICE_DOMAIN=https://layer0-docs-layer0-aws-store-example-default.layer0-limelight.link
AWS_SEARCH_SERVICE_DOMAIN=retai-LoadB-18LUF1ATZNQNH-1395658750.us-east-1.elb.amazonaws.com
VUE_APP_SEARCH_SERVICE_PATH=/search-service

VUE_APP_LOCATION_SERVICE_DOMAIN=https://layer0-docs-layer0-aws-store-example-default.layer0-limelight.link
AWS_LOCATION_SERVICE_DOMAIN=retai-loadb-do2tp4pr6ejv-357775208.us-east-1.elb.amazonaws.com
VUE_APP_LOCATION_SERVICE_PATH=/location-service

AWS_IMAGE_SERVICE_DOMAIN=d28z1nhxyoq0l5.cloudfront.net
```

## Deployment

Make sure all the steps of [Build](#Build) section are done before deployment!

To check if everything is OK you can try running production build via `npm run layer0:start:prod`.

To deploy files on Layer0 run `npm run layer0:deploy`

To summarize, make sure all of these commands are run to ensure all changes are picked up.

```bash
# Build app
npm run build

# Build Layer0 configurations
npm run layer0:build

# Deploy to Layer0
npm run layer0:deploy
```
````
