
# About

A sample retail web application and workshop platform intended as an educational tool for demonstrating how AWS infrastructure and services can be used to build compelling customer experiences for eCommerce, retail, and digital marketing use-cases.

## Build Status

![Ruff](https://github.com/aws-samples/retail-demo-store/actions/workflows/ruff.yml/badge.svg?branch=master)
![UI Build](https://github.com/aws-samples/retail-demo-store/actions/workflows/build-ui.yml/badge.svg?branch=master)

**This project is intended for educational purposes only and not for production use.**

The Retail Demo Store is an eCommerce reference implementation designed to showcase how AWS services can be used to build compelling shopping experiences using modern architecture and design patterns.

At the heart of the Retail Demo Store is a collection of polyglot microservices hosted in [Amazon Elastic Container Service](https://aws.amazon.com/ecs/) ([AWS Fargate](https://aws.amazon.com/fargate/)) that represent domain constructs such as [products](src/products), [carts](src/carts), [orders](src/orders), and [users](src/users) as well as services for [search](src/search) and [recommendations](src/recommendations). While the [web user interface](src/web-ui) is served by Amazon CloudFront and Amazon S3.

The architecture is supported by several managed services including [Amazon Cognito](https://aws.amazon.com/cognito/), [Amazon Pinpoint](https://aws.amazon.com/pinpoint/), [Amazon Personalize](https://aws.amazon.com/personalize/), and [Amazon OpenSearch Service](https://aws.amazon.com/opensearch-service/) (successor to Amazon Elasticsearch Service). The [web user interface](../src/web-ui]) is built using the [Vue.js](https://vuejs.org/) framework with [AWS Amplify](https://aws.amazon.com/amplify/) to provide integrations with Cognito for registration/authentication and event streaming to Pinpoint and Personalize (Event Tracker). Finally, [AWS CodePipeline](https://aws.amazon.com/codepipeline/) is leveraged to demonstrate how AWS development services can be used to orchestrate the build and deployment process with the Retail Demo Store.

![Retail Demo Store Architecture](./assets/retaildemostore-architecture.png)

## Supported Regions

The Retail Demo Store has been tested in the AWS regions indicated in the deployment instructions below. Additional regions may be supported depending on [service availability](https://aws.amazon.com/about-aws/global-infrastructure/regional-product-services/) and having the Retail Demo Store's deployment resources staged to an S3 bucket in the targeted region.
