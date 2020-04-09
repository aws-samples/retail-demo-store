Overview > [1 - Creating the Account](1-Creating-account.md) > [2 - Personalization](2-Personalization.md)

# Overview

The Retail Demo Store is an eCommerce reference implementation designed to showcase how AWS services can be used to build compelling shopping experiences using modern architecture and design patterns.

![image.png](../workshop/images/retaildemostore-home-devices.png)

At the heart of the Retail Demo Store is a collection of polyglot microservices hosted in Amazon Elastic Container Service (AWS Fargate) that represent domain constructs such as products, carts, orders, and users as well as services for search, recommendations. While the web user interface is served by Amazon CloudFront and Amazon S3

The architecture is supported by several managed services including Amazon Cognito, Amazon Pinpoint, Amazon Personalize, and Amazon Elasticsearch. The web user interface is built using the Vue.js framework with AWS Amplify to provide integrations with Cognito for registration/authentication and event streaming to Pinpoint and Personalize (Event Tracker).
Finally, AWS CodePipeline is leveraged to show customers how AWS development services can be used to orchestrate the build and deployment process with the Retail Demo Store. Figure 2 depicts the system architecture.

![image.png](../workshop/images/retaildemostore-architecture.png)

Figure 2. The Retail Demo Store Architecture.

The intent of the Retail Demo Store is to 1) provide a tool to demonstrate the capabilities of key AWS services for retail/eCommerce use-cases and 2) provide a platform for AWS Solutions Architects and technical staff to deliver customer-facing workshops, Immersion Days, hackathons, and similar types of events. 

Bundled with the Retail Demo Store deployment are several pre-built workshops, implemented as Jupyter notebooks hosted in an Amazon SageMaker instance, that are designed to walk a technical audience through adding functionality to the base Retail Demo Store implementation. As of this writing there are workshops for:

* adding catalog search powered by Amazon Elasticsearch
* personalization powered by Amazon Personalize
* experimentation techniques (A/B testing, interleaving results testing, and multi-armed bandit testing)
* customer messaging using Amazon Pinpoint for welcome emails, abandoned cart emails, and personalized product recommendation emails


## Contributing

If you have any questions about the project or want to get involved, please refer to the [Contributing Guidelines](../CONTRIBUTING.md)

## Limitations and Known Issues

The Retail Demo Store project is still a work in progress. Therefore, there may be some unresolved bugs and usability issues. Please report any issues you find to either of the stakeholders referenced above.


# Next Steps

1) [Creating a Retail Demo Store account](1-Creating-account.md)
2) [Personalized Experience](2-Personalization.md)