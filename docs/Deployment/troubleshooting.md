# Troubleshoot

## Known Issues/Limitations

* The application was written for demonstration and education purposes and not for production use.
* You currently cannot deploy this project multiple times in the same AWS account and the same AWS region. However, you can deploy the project into separate supported regions within the same AWS account.
* Make sure your CloudFormation stack name uses all lowercase letters.
* Currently only tested in the AWS regions provided in the deployment instructions above. The only limitation for deploying into other regions is [availability of all required services](https://aws.amazon.com/about-aws/global-infrastructure/regional-product-services/).
    - Amazon IVS is currently only supported in the N. Virginia (us-east-1), Oregon (us-west-2), and Ireland (eu-west-1) regions. Therefore, to deploy the Retail Demo Store in a region that does not support IVS, be sure to select to use the Default IVS Streams CloudFormation template parameter.

## Troubleshooting / FAQs

***Q: When accessing the Retail Demo Store web application after deploying the project, a CloudFront error is displayed. What's wrong?***

***A:*** Sign in to the AWS account/region where the project was deployed and browse to CodePipeline. Verify that the pipeline with "WebUIPipeline" in the name has successfully been built. If it failed, inspect the details of the Build stage to diagnose the root cause.

***Q: When accessing the Retail Demo Store web application after deploying the project, the home page shows spinning icons and products are never loaded. What's wrong?***

***A:*** The most likely cause is an error building or deploying one or more of the microservices. Sign in to the AWS account/region where the project was deployed and browse to CodePipeline. Verify that all of the Retail Demo Store pipelines have completed successfully. Inspect the details for any that have failed to determine the root cause. Sometimes just manually triggering a build/deploy will resolve the issue.

***Q: This project is expensive to run (or keep running). How can I reduce the running cost of a deployment?***

***A:*** The most costly service in the project for an idle deployment is Amazon Personalize. You can eliminate Personalize idle costs by stopping all Amazon Personalize recommenders and deleting all campaigns in the Retail Demo Store dataset group for Personalize. This just shuts down the real-time inference endpoints; the datasets and ML models will remain. You should also change all of the recommender and campaign ARN parameter values in the AWS Systems Manager Parameter Store to `NONE`, leaving the parameter values for filters and the event tracker alone. These parameter names start with `/retaildemostore/personalize/` (e.g., `/retaildemostore/personalize/recommended-for-you-arn`). Once you complete these steps, the storefront will fall back to default behavior for recommending products from the catalog. To reactive Personalize, start the recommenders and create campaigns and then set the recommender and/or campaign ARNs back in the Systems Manager Parameter Store. The storefront will automatically start showing recommendations from Personalize again.

## Reporting Bugs

If you encounter a bug, please create a new issue with as much detail as possible and steps for reproducing the bug. See the [Contributing Guidelines](https://github.com/aws-samples/retail-demo-store/blob/master/CONTRIBUTING.md) for more details.
