
# Retail Demo Store 

A sample retail web application and workshop platform intended as an educational tool for demonstrating how AWS infrastructure and services can be used to build compelling customer experiences for eCommerce, retail, and digital marketing use-cases.

![Ruff](https://github.com/aws-samples/retail-demo-store/actions/workflows/ruff.yml/badge.svg?branch=master)
![UI Build](https://github.com/aws-samples/retail-demo-store/actions/workflows/build-ui.yml/badge.svg?branch=master)

**This project is intended for educational purposes only and not for production use.**

![Retail Demo Store Home Page](./assets/retaildemostore-home-devices.png)

The Retail Demo Store is an eCommerce reference implementation designed to showcase how AWS services can be used to build compelling shopping experiences using modern architecture and design patterns.

At the heart of the Retail Demo Store is a collection of polyglot microservices hosted in [Amazon Elastic Container Service](https://aws.amazon.com/ecs/) ([AWS Fargate](https://aws.amazon.com/fargate/)) that represent domain constructs such as [products](https://github.com/aws-samples/retail-demo-store/tree/master/src/products), [carts](https://github.com/aws-samples/retail-demo-store/tree/master/src/carts), [orders](https://github.com/aws-samples/retail-demo-store/tree/master/src/orders), and [users](https://github.com/aws-samples/retail-demo-store/tree/master/src/users) as well as services for [search](https://github.com/aws-samples/retail-demo-store/tree/master/src/search) and [recommendations](https://github.com/aws-samples/retail-demo-store/tree/master/src/recommendations). While the [web user interface](https://github.com/aws-samples/retail-demo-store/tree/master/src/web-ui) is served by Amazon CloudFront and Amazon S3.

The architecture is supported by several managed services including [Amazon Cognito](https://aws.amazon.com/cognito/), [Amazon Pinpoint](https://aws.amazon.com/pinpoint/), [Amazon Personalize](https://aws.amazon.com/personalize/), and [Amazon OpenSearch Service](https://aws.amazon.com/opensearch-service/) (successor to Amazon Elasticsearch Service). The [web user interface](https://github.com/aws-samples/retail-demo-store/tree/master/src/web-ui) is built using the [Vue.js](https://vuejs.org/) framework with [AWS Amplify](https://aws.amazon.com/amplify/) to provide integrations with Cognito for registration/authentication and event streaming to Pinpoint and Personalize (Event Tracker). Finally, [AWS CodePipeline](https://aws.amazon.com/codepipeline/) is leveraged to demonstrate how AWS development services can be used to orchestrate the build and deployment process with the Retail Demo Store.

![Retail Demo Store Architecture](./assets/retaildemostore-architecture.png)

## Supported Regions

The Retail Demo Store has been tested in the AWS regions indicated in the deployment instructions below.


| Region Name | Region | Supported |
| ------------- | ------------- | ------------- |
| US East (N. Virginia) | us-east-1 | Fully supported |
| US West (Oregon) | us-west-2 | Fully supported |
| Europe (Ireland) | eu-west-1 | Partial support (personalized product descriptions, thematic similar product descriptions and room makeover not supported) |
| Europe (Frankfurt) | eu-central-1 | Partial support (thematic similar product descriptions and room makeover not supported) |
| Asia Pacific (Tokyo) | ap-northeast-1 | Partial support (personalized product descriptions and room makeover not supported) |
| Asia Pacific (Sydney) | ap-southeast-2 | Partial support (personalized product descriptions and thematic similar product descriptions not supported) |

!!! Note

    Additional regions may be supported depending on [service availability](https://aws.amazon.com/about-aws/global-infrastructure/regional-product-services/) and having the Retail Demo Store's deployment resources staged to an S3 bucket in the targeted region.
