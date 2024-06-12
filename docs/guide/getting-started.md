# Getting Started

***IMPORTANT NOTE:** Deploying this demo application in your AWS account will create and consume AWS resources, which will cost money. In addition, some features such as account registration via Amazon Cognito and the messaging workshop for Amazon Pinpoint require users to provide a valid email address and optionally a phone number to demonstrate completely. Therefore, to avoid ongoing charges and to clean up all data, be sure to follow all workshop clean up instructions and shutdown/remove all resources by deleting the CloudFormation stack once you are finished.*

**The Retail Demo Store experience is for demonstration purposes only. You must comply with all applicable laws and regulations, including any laws and regulations related to email or text marketing, in any applicable country or region.**

**If you are a developer looking to contribute to the Retail Demo Store, please see the Developer section below.**

To get the Retail Demo Store running in your own AWS account, follow these instructions. If you are attending an AWS-led event where temporary AWS accounts are provided, this has likely already been done for you. Check with your event administrators.

## Step 1 - Get an AWS Account

If you do not have an AWS account, please see [How do I create and activate a new Amazon Web Services account?](https://aws.amazon.com/premiumsupport/knowledge-center/create-and-activate-aws-account/)

## Step 2 - Log into the AWS Console

Log into the [AWS console](https://console.aws.amazon.com/) if you are not already.

Note: If you are logged in as an IAM user, ensure your account has permissions to create and manage the necessary resources and components for this application.

## Step 3 - Deploy to your AWS Account

The following CloudFormation launch options will set the deployment approach to "CodeCommit". You can ignore the GitHub related template parameters. After clicking one of the Launch Stack buttons below, follow the procedures to launch the template. **Be sure to enter a CloudFront stack name in lowercase letters (numbers and hyphens are okay too).**

With this deployment option, the CloudFormation template will import the Retail Demo Store source code into a CodeCommit repository in your account and setup CodePipeline to build and deploy into ECS from that respository.

Region name | Region code | Launch
--- | --- | ---
US East (N. Virginia) | us-east-1 | [![Launch Stack](https://cdn.rawgit.com/buildkite/cloudformation-launch-stack-button-svg/master/launch-stack.svg)](https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/create/review?templateURL=https://s3.amazonaws.com/retail-demo-store-us-east-1/cloudformation-templates/template.yaml&stackName=retaildemostore&param_ResourceBucket=retail-demo-store-us-east-1&param_SourceDeploymentType=CodeCommit)
US West (Oregon) | us-west-2 | [![Launch Stack](https://cdn.rawgit.com/buildkite/cloudformation-launch-stack-button-svg/master/launch-stack.svg)](https://console.aws.amazon.com/cloudformation/home?region=us-west-2#/stacks/create/review?templateURL=https://s3-us-west-2.amazonaws.com/retail-demo-store-us-west-2/cloudformation-templates/template.yaml&stackName=retaildemostore&param_ResourceBucket=retail-demo-store-us-west-2&param_SourceDeploymentType=CodeCommit)
Europe (Ireland) | eu-west-1 | [![Launch Stack](https://cdn.rawgit.com/buildkite/cloudformation-launch-stack-button-svg/master/launch-stack.svg)](https://console.aws.amazon.com/cloudformation/home?region=eu-west-1#/stacks/create/review?templateURL=https://s3-eu-west-1.amazonaws.com/retail-demo-store-eu-west-1/cloudformation-templates/template.yaml&stackName=retaildemostore&param_ResourceBucket=retail-demo-store-eu-west-1&param_SourceDeploymentType=CodeCommit)
Asia Pacific (Tokyo) | ap-northeast-1 | [![Launch Stack](https://cdn.rawgit.com/buildkite/cloudformation-launch-stack-button-svg/master/launch-stack.svg)](https://console.aws.amazon.com/cloudformation/home?region=ap-northeast-1#/stacks/create/review?templateURL=https://s3.amazonaws.com/retail-demo-store-ap-northeast-1/cloudformation-templates/template.yaml&stackName=retaildemostore&param_ResourceBucket=retail-demo-store-ap-northeast-1&param_SourceDeploymentType=CodeCommit)
Asia Pacific (Sydney) | ap-southeast-2 | [![Launch Stack](https://cdn.rawgit.com/buildkite/cloudformation-launch-stack-button-svg/master/launch-stack.svg)](https://console.aws.amazon.com/cloudformation/home?region=ap-southeast-2#/stacks/create/review?templateURL=https://s3.amazonaws.com/retail-demo-store-ap-southeast-2/cloudformation-templates/template.yaml&stackName=retaildemostore&param_ResourceBucket=retail-demo-store-ap-southeast-2&param_SourceDeploymentType=CodeCommit)

The CloudFormation deployment will take approximately 40 minutes to complete.

### Notes:

#### Amazon Personalize Campaigns

If you chose to have the Amazon Personalize campaigns automatically built post-deployment, this process will take an additional 2-2.5 hours. This process happens in the background so you don't have to wait for it to complete before exploring the Retail Demo Store application and architecture. Once the Personalize campaigns are created, they will be automatically activated in the [Web UI](src/web-ui) and [Recommendations](src/recommendations) service. You can monitor the progress in CloudWatch under the `/aws/lambda/RetailDemoStorePersonalizePreCreateCampaigns` log group.

#### Amazon Pinpoint Campaigns
If you chose to have the Amazon Pinpoint campaigns automatically built (‘Auto-Configure Pinpoint’ is set to ‘Yes’ in the CloudFormation template), this process will take an additional 20-30 minutes.
Once the Pinpoint campaigns are created, they will be automatically visbile in the [Web UI](src/web-ui). However, there are some manual steps described below that are required for enabling the Pinpoint channels.

##### Pinpoint Emails:

*PinpointEmailFromAddress:*
By Default, AWS Accounts have  [emails set up in a sandbox environement](https://docs.aws.amazon.com/pinpoint/latest/userguide/channels-email.html). To enable the functionality, you need to complete either of the following manual steps.
* Verifying the email addresses you want to send and receive emails from. More info [here](https://docs.aws.amazon.com/pinpoint/latest/userguide/channels-email-manage-verify.html). This is the easiest and recommended approach for demos and workshops.
* Request to be removed from the sandbox environment. More info [here](https://docs.aws.amazon.com/pinpoint/latest/userguide/channels-email-setup-production-access.html). This is recommended only for production workloads and the Retail Demo Store is intended to be used for demonstration purposes only.

##### Pinpoint SMS
*PinpointSMSLongCode:*
A dedicated [long code](https://docs.aws.amazon.com/pinpoint/latest/userguide/channels-sms-awssupport-long-code.html) (i.e. a phone number) obtained for Amazon Pinpoint to send and receive messages at. You also need to enable [two way SMS](https://docs.aws.amazon.com/pinpoint/latest/userguide/channels-sms-two-way.html) for this long code using Pinpoint. Follow steps 2 and 3 in the *Enable Pinpoint SMS Channel & Obtain Dedicated Long Code* section of the [Pinpoint workshop](https://github.com/aws-samples/retail-demo-store/blob/master/workshop/4-Messaging/4.1-Pinpoint.ipynb) to get a long code and enable two way SMS for it.
When deploying Retail Demo Store, enter the number as a parameter. The number should be formatted along with the country code and without any spaces or brackets. For Example: enter “+1XXXXXXXXXX” for a long code based in the United States.

## Step 4 - Using the Retail Demo Store Web Application

Once you launch the CloudFormation stack, all of the services will go through a build and deployment cycle and deploy the Retail Demo Store.

Compiling and deploying the web UI application and the services it uses can take some time. You can monitor progress in CodePipeline. Until this completes, you may see a Sample Application when accessing the public WebUI URL.

You can find the URL for the Retail Demo Store Web UI in the Outputs of your main CloudFormation stack (called `retaildemostore` unless you changed that option in the steps above).

Look for the "WebURL" output parameter.

You can read more [detailed instructions on how to demo the Retail Demo Store in the Demo section at the end of this document](#delivering-a-demo-of-the-retail-demo-store).
