# Retail Demo Store

A sample retail web application and workshop platform intended as an educational tool for demonstrating how AWS infrastructure and services can be used to build compelling customer experiences for eCommerce, retail, and digital marketing use-cases.

**This project is intended for education purposes only and not for production usage.**

![Retail Demo Store Home Page](./workshop/images/retaildemostore-home-devices.png)

The core of the Retail Demo Store is a polyglot microservice architecture deployed as a collection of RESTful web services in [Amazon Elastic Container Service](https://aws.amazon.com/ecs/) (ECS). Several AWS managed services are leveraged to provide build, deployment, authentication, messaging, search, and personalization capabilities. 

The web user interface is a [single page application](https://en.wikipedia.org/wiki/Single-page_application) built using [responsive web design](https://en.wikipedia.org/wiki/Responsive_web_design) frameworks and techniques, producing a native app-like experience tailored to the user's device. See the [workshops](./workshop/Welcome.ipynb) page for details.

![Retail Demo Store Architecture](./workshop/images/retaildemostore-architecture.png)

## Workshops

This project is designed to provide you with an environment in which you can learn to modify the behavior of the Retail Demo Store using self-paced workshops.  This can be done in a group setting or as an individual. Currently there are workshops for adding search, personalization, experimentation frameworks, a/b testing, analytics, CDPs, messaging, and more. 

AWS partners have developed workshop content that enables you to learn how to integrate their solutions with the AWS services that the Retail Demo Store uses.

For an overview of the Retail Demo Store, its architecture, and workshops, please see the [workshop welcome notebook](./workshop/Welcome.ipynb) page.

## Supported Regions

The Retail Demo Store has been tested in the AWS regions indicated in the deployment instructions below. Additional regions may be supported depending on [service availability](https://aws.amazon.com/about-aws/global-infrastructure/regional-product-services/) and having the Retail Demo Store's deployment resources staged to an S3 bucket in the targeted region.

# Getting Started

***IMPORTANT NOTE:** Deploying this demo application in your AWS account will create and consume AWS resources, which will cost money. In addition, some features such as account registration via Amazon Cognito and the messaging workshop for Amazon Pinpoint require users to provide a valid mobile phone number and email address to demonstrate completely. Therefore, to avoid ongoing charges and to clean up all data, be sure to follow all workshop clean up instructions and shutdown/remove all resources by deleting the CloudFormation stack once you are finished.*

If you are a developer looking to contribute to the Retail Demo Store, please see the Developer section below.

To get the Retail Demo Store running in your own AWS account, follow these instructions. If you are attending an AWS-led event where temporary AWS accounts are provided, this has likely already been done for you already.  Check with your event administrators.

## Step 1 - Get an AWS Account

If you do not have an AWS account, please see [How do I create and activate a new Amazon Web Services account?](https://aws.amazon.com/premiumsupport/knowledge-center/create-and-activate-aws-account/)

## Step 2 - Log into the AWS Console

Log into the [AWS console](https://console.aws.amazon.com/) if you are not already. 

Note: If you are logged in as an IAM user, ensure your account has permissions to create and manage the necessary resources and components for this application.

## Step 3 - Deploy to your AWS Account

The following CloudFormation launch options will set the deployment approach to "CodeCommit". You can ignore the GitHub related template parameters. After clicking one of the Launch Stack buttons below, follow the procedures to launch the template.

With this deployment option, the CloudFormation template will import the Retail Demo Store source code into a CodeCommit repository in your account and setup CodePipeline to build and deploy into ECS from that respository.

Region name | Region code | Launch
--- | --- | ---
US East (N. Virginia) | us-east-1 | [![Launch Stack](https://cdn.rawgit.com/buildkite/cloudformation-launch-stack-button-svg/master/launch-stack.svg)](https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/create/review?templateURL=https://s3.amazonaws.com/retail-demo-store-us-east-1/cloudformation-templates/template.yaml&stackName=retaildemostore&param_ResourceBucket=retail-demo-store-us-east-1&param_SourceDeploymentType=CodeCommit)
US West (Oregon) | us-west-2 | [![Launch Stack](https://cdn.rawgit.com/buildkite/cloudformation-launch-stack-button-svg/master/launch-stack.svg)](https://console.aws.amazon.com/cloudformation/home?region=us-west-2#/stacks/create/review?templateURL=https://s3-us-west-2.amazonaws.com/retail-demo-store-us-west-2/cloudformation-templates/template.yaml&stackName=retaildemostore&param_ResourceBucket=retail-demo-store-us-west-2&param_SourceDeploymentType=CodeCommit)
Europe (Ireland) | eu-west-1 | [![Launch Stack](https://cdn.rawgit.com/buildkite/cloudformation-launch-stack-button-svg/master/launch-stack.svg)](https://console.aws.amazon.com/cloudformation/home?region=eu-west-1#/stacks/create/review?templateURL=https://s3-eu-west-1.amazonaws.com/retail-demo-store-eu-west-1/cloudformation-templates/template.yaml&stackName=retaildemostore&param_ResourceBucket=retail-demo-store-eu-west-1&param_SourceDeploymentType=CodeCommit)

The CloudFormation deployment will take 20-30 minutes to complete. If you chose to have the Amazon Personalize campaigns automatically built post-deployment, this process will take an additional 2-2.5 hours. This process happens in the background so you don't have to wait for it to complete before exploring the Retail Demo Store application and architecture. Once the Personalize campaigns are created, they will be automatically activated in the [Web UI](src/web-ui) and [Recommendations](src/recommendations) service. You can monitor the progress in CloudWatch under the `/aws/lambda/RetailDemoStorePersonalizePreCreateCampaigns` log group.

## Using the Retail Demo Store Web Application

Once you launch the CloudFormation stack, all of the services will go through a build and deployment cycle and deploy the Retail Demo Store. 

Compiling and deploying the web UI application and the services it uses can take some time. You can monitor progress in CodePipeline. Until this completes, you may see a Sample Application when accessing the public WebUI URL.

You can find the URL for the Retail Demo Store Web UI in the Outputs of your main CloudFormation stack (called `retaildemostore` unless you changed that option in the steps above). 

Look for the "WebURL" output parameter.

You can read more detailed instructions on how to use this demo in the [demonstration documentation](documentation).

## Accessing Workshops

The Retail Demo Store environment is designed to provide an series of interactive workshops that progressively add functionality to the Retail Demo Store application environment.

The workshops are deployed in a SageMaker Jupyter environment that is deployed in your CloudFormation stack.  To access the Retail Demo Store workshops after the CloudFormation stack has completed, browse to Amazon SageMaker and then Notebook instances in the AWS console in your AWS account. 

You will see a running Notebook instance. Click "Open JupyterLab" for the Retail Demo Store notebook instance. 

Here you will find several workshops in a directory structure in the notebook instance. See the [workshops](./workshop/Welcome.ipynb) page for details.

# Developer Instructions

If you would like to contribute enhancements or features to the Retail Demo Store, please read on.  Thanks for considering working with this project.

## Step 1: Fork this Repo

To submit changes for review, you will need to create a fork of the Retail Demo Store respository in your own GitHub account.

## Step 2: Create a GitHub Personal Access Token

Create a [GitHub Personal Access Token](https://help.github.com/en/articles/creating-a-personal-access-token-for-the-command-line) in your GitHub account. 

Make sure that your token has the "repo", "repo:status", and "admin:repo_hook" permission scopes.

Save your access token in a secure location.

## Step 3: Decide on Deployment Options

The Retail Demo Store provides several options for managing deployments.  Here are the most common ones:

### Deploy via an S3 Staging Bucket

If you want to modify deployment templates and manage the whole deployment process yourself, you will need to configure an S3 bucket for staging Retail Demo Store deployment templates and resources prior to deployment in your own AWS account.  This bucket must be in the region in which you plan to deploy.  

***These instructions only apply if you wish to stage your own Retail Demo Store deployment resources. For example, if you want to test CloudFormation template changes or the deployment of Lambda code. These instructions are not necessary for the typical deployment scenarios described above.***

The launch options described above pull the CloudFormation templates from a shared S3 bucket. If you want to test changes to the templates or launch a custom variation of this project, you can do so by uploading your versions of the templates and other deployment resources to an S3 bucket in your account (i.e. staging), launching your version of the [root template](aws/cloudformation-templates/template.yaml) (i.e. upload the root template or specify an S3 URL pointing to the root template in your bucket), and override the "ResourceBucket" and "ResourceBucketRelativePath" template parameters to refer to your bucket and path. These parameters are used to load the nested templates from your bucket rather than the default shared bucket.

#### Bucket Region

Your staging bucket must be in the region in which you plan to deploy the Retail Demo Store.

#### Bucket Permissions

The default stage script requires the ability to set the resources it uploads to your bucket as public read.  Note that you do not need to set the bucket up to allow public listing of the resources in the bucket (this is not recommended).

You will also need to allow access for Amazon Personalize to your bucket, since this is required for the Personalize workshops to function:

```json
{
    "Version": "2012-10-17",
    "Id": "PersonalizeS3BucketAccessPolicy",
    "Statement": [
        {
            "Sid": "PersonalizeS3BucketAccessPolicy",
            "Effect": "Allow",
            "Principal": {
                "Service": "personalize.amazonaws.com"
            },
            "Action": [
                "s3:GetObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::<your bucket name>",
                "arn:aws:s3:::<your bucket name>/*"
            ]
        }
    ]
}
```

#### Staging for Deployment

The [stage.sh](stage.sh) script at the root of the repository must be used to upload the deployment resources to a staging S3 bucket if you use this option. The shell uses the local AWS credentials to build and push resources to your custom bucket. 

Example on how to stage your project to a custom bucket and path (note the path is optional but, if specified, must end with '/'):

```bash
./stage.sh mycustombucket path/
```

The stage script will output a path to your master deployment CloudFormation template.  You can use this link to your S3 bucket to start a new deployment via the CloudFormation console in your AWS Console.

### Deploy Infrastructure from the Main Repo, Deploy Application and Services via GitHub

If you only want to modify the web user interface, or the Retail Demo Store backend services, you can deploy Retail Demo Store using the options below, and issue commits in your own fork via Github to trigger a re-deploy.  This will allow you to push changes to the Retail Demo Store services and web user interface using a CodeDeploy pipeline.

To do that, select one of the CloudFormation launch options below. The deployment approach will be set to "GitHub". 

**All GitHub related template parameters are required.** Enter your GitHub username and deployment key from Step 2 in the CloudFormation UI after clicking one of the Launch Stack buttons below, and follow the procedures to launch the template.

Region name | Region code | Launch
--- | --- | ---
US East (N. Virginia) | us-east-1 | [![Launch Stack](https://cdn.rawgit.com/buildkite/cloudformation-launch-stack-button-svg/master/launch-stack.svg)](https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/create/review?templateURL=https://s3.amazonaws.com/retail-demo-store-us-east-1/cloudformation-templates/template.yaml&stackName=retaildemostore&param_ResourceBucket=retail-demo-store-us-east-1&param_SourceDeploymentType=GitHub)
US West (Oregon) | us-west-2 | [![Launch Stack](https://cdn.rawgit.com/buildkite/cloudformation-launch-stack-button-svg/master/launch-stack.svg)](https://console.aws.amazon.com/cloudformation/home?region=us-west-2#/stacks/create/review?templateURL=https://s3-us-west-2.amazonaws.com/retail-demo-store-us-west-2/cloudformation-templates/template.yaml&stackName=retaildemostore&param_ResourceBucket=retail-demo-store-us-west-2&param_SourceDeploymentType=GitHub)
Europe (Ireland) | eu-west-1 | [![Launch Stack](https://cdn.rawgit.com/buildkite/cloudformation-launch-stack-button-svg/master/launch-stack.svg)](https://console.aws.amazon.com/cloudformation/home?region=eu-west-1#/stacks/create/review?templateURL=https://s3-eu-west-1.amazonaws.com/retail-demo-store-eu-west-1/cloudformation-templates/template.yaml&stackName=retaildemostore&param_ResourceBucket=retail-demo-store-eu-west-1&param_SourceDeploymentType=GitHub)

The CloudFormation deployment will take 20-30 minutes to complete. If you chose to have the Amazon Personalize campaigns automatically built post-deployment, this process will take an additional 2-2.5 hours. This process happens in the background so you don't have to wait for it to complete before exploring the Retail Demo Store application and architecture. Once the Personalize campaigns are created, they will be automatically activated in the [Web UI](src/web-ui) and [Recommendations](src/recommendations) service. You can monitor the progress in CloudWatch under the `/aws/lambda/RetailDemoStorePersonalizePreCreateCampaigns` log group.

### Developing Services Locally

The Retail Demo Store also supports running the web user interface and backend services in a local container on your machine.  This may be a handy option while testing a fix or enhancement.

[Detailed instructions](./src) are available on how to get going with local development.  Note that you will still need to set up one of the development options described above, and have a working deployment in your AWS account as some of the services will need to access cloud-based services as part of deployment.

# Known Issues

* The application was written for demonstration purposes and not for production use.
* You currently cannot deploy this project multiple times in the same AWS account and the same region. However, you can deploy the project into separate regions within the same AWS account.
* Make sure your CloudFormation stack name uses all lowercase letters.
* Currently only tested in the AWS regions provided in the deployment instructions above. The only limitation for deploying into other regions is [availability of all required services](https://aws.amazon.com/about-aws/global-infrastructure/regional-product-services/).

# Reporting Bugs

If you encounter a bug, please create a new issue with as much detail as possible and steps for reproducing the bug. See the [Contributing Guidelines](./CONTRIBUTING.md) for more details.

# License

This sample code is made available under a modified MIT license. See the LICENSE file.
