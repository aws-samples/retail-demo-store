# Developer Instructions

If you would like to contribute enhancements or features to the Retail Demo Store, please read on for instructions on how to develop and test your changes. Thanks for considering working with this project.

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

***These instructions only apply if you wish to stage your own Retail Demo Store deployment resources. For example, if you want to test CloudFormation template changes or the deployment of Lambda code. These instructions are not necessary for the typical deployment scenarios described in the main [README](./README.md).***

The launch options described in the main [README](./README.md) pull the CloudFormation templates from an S3 bucket designed to support deployments of what is in the upstream master branch. If you want to test changes to the templates or launch a custom variation of this project, you can do so by uploading your versions of the templates and other deployment resources to an S3 bucket in your account (i.e. staging bucket), launching your version of the [root template](aws/cloudformation-templates/template.yaml) (i.e. upload the root template or specify an S3 URL pointing to the root template in your bucket), and override the `ResourceBucket` and `ResourceBucketRelativePath` template parameters to refer to your bucket and path. These parameters are used to load the nested templates from your bucket rather than the default shared bucket.

#### Bucket Region

Your staging bucket must be in the region in which you plan to deploy the Retail Demo Store.

#### Bucket Permissions

The default stage script requires the ability to set the resources it uploads to your bucket as public read.  Note that you do not need to set the bucket up to allow public listing of the resources in the bucket (this is not recommended).

If you plan to enable the automated Personalize campaign creation process at deployment time, you must allow access for Amazon Personalize to your bucket. Add the following bucket policy to your staging bucket.

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

It is advisable to use a Python 3 virtual environment to do this and the scripts assume that the executable pip is the Python 3 version of pip so if necessary you may need to install pip into that virtual environment (if your system defaults to a Python 2 version of pip).

There are also some Golang dependencies that need to be installed before staging:

```bash
go get github.com/aws/aws-lambda-go/lambda
go get github.com/aws/aws-lambda-go/cfn
go get github.com/aws/aws-sdk-go
go get gopkg.in/yaml.v2
```

The [stage.sh](stage.sh) script at the root of the repository must be used to upload the deployment resources to your staging S3 bucket if you use this option. The shell uses the local AWS credentials to build and push resources to your custom bucket.

Example on how to stage your project to a custom bucket and path (note the path is optional but, if specified, must end with '/'):

```bash
./stage.sh mycustombucket path/
```

The stage script will output a path to your master deployment CloudFormation template.  You can use this link to your S3 bucket to start a new deployment via the CloudFormation console in your AWS Console.

### Deploy Infrastructure from the Main Repo, Deploy Application and Services via GitHub

If you only want to modify the web user interface, or the Retail Demo Store backend services, you can deploy Retail Demo Store using the options below, and issue commits in your own fork via GitHub to trigger a re-deploy.  This will allow you to push changes to the Retail Demo Store services and web user interface using a CodeDeploy pipeline.

To do that, select one of the CloudFormation launch options below. The deployment approach will be set to "GitHub".

**All GitHub related template parameters are required.** Enter your GitHub username and deployment key from Step 2 in the CloudFormation UI after clicking one of the Launch Stack buttons below, and follow the procedures to launch the template.

Region name | Region code | Launch
--- | --- | ---
US East (N. Virginia) | us-east-1 | [![Launch Stack](https://cdn.rawgit.com/buildkite/cloudformation-launch-stack-button-svg/master/launch-stack.svg)](https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/create/review?templateURL=https://s3.amazonaws.com/retail-demo-store-us-east-1/cloudformation-templates/template.yaml&stackName=retaildemostore&param_ResourceBucket=retail-demo-store-us-east-1&param_SourceDeploymentType=GitHub)
US West (Oregon) | us-west-2 | [![Launch Stack](https://cdn.rawgit.com/buildkite/cloudformation-launch-stack-button-svg/master/launch-stack.svg)](https://console.aws.amazon.com/cloudformation/home?region=us-west-2#/stacks/create/review?templateURL=https://s3-us-west-2.amazonaws.com/retail-demo-store-us-west-2/cloudformation-templates/template.yaml&stackName=retaildemostore&param_ResourceBucket=retail-demo-store-us-west-2&param_SourceDeploymentType=GitHub)
Europe (Ireland) | eu-west-1 | [![Launch Stack](https://cdn.rawgit.com/buildkite/cloudformation-launch-stack-button-svg/master/launch-stack.svg)](https://console.aws.amazon.com/cloudformation/home?region=eu-west-1#/stacks/create/review?templateURL=https://s3-eu-west-1.amazonaws.com/retail-demo-store-eu-west-1/cloudformation-templates/template.yaml&stackName=retaildemostore&param_ResourceBucket=retail-demo-store-eu-west-1&param_SourceDeploymentType=GitHub)
Asia Pacific (Tokyo) | ap-northeast-1 | [![Launch Stack](https://cdn.rawgit.com/buildkite/cloudformation-launch-stack-button-svg/master/launch-stack.svg)](https://console.aws.amazon.com/cloudformation/home?region=ap-northeast-1#/stacks/create/review?templateURL=https://s3.amazonaws.com/retail-demo-store-ap-northeast-1/cloudformation-templates/template.yaml&stackName=retaildemostore&param_ResourceBucket=retail-demo-store-ap-northeast-1&param_SourceDeploymentType=GitHub)
Asia Pacific (Sydney) | ap-southeast-2 | [![Launch Stack](https://cdn.rawgit.com/buildkite/cloudformation-launch-stack-button-svg/master/launch-stack.svg)](https://console.aws.amazon.com/cloudformation/home?region=ap-southeast-2#/stacks/create/review?templateURL=https://s3.amazonaws.com/retail-demo-store-ap-southeast-2/cloudformation-templates/template.yaml&stackName=retaildemostore&param_ResourceBucket=retail-demo-store-ap-southeast-2&param_SourceDeploymentType=GitHub)


The CloudFormation deployment will take 20-30 minutes to complete. If you chose to have the Amazon Personalize campaigns automatically built post-deployment, this process will take an additional 2-2.5 hours. This process happens in the background so you don't have to wait for it to complete before exploring the Retail Demo Store application and architecture. Once the Personalize campaigns are created, they will be automatically activated in the [Web UI](src/web-ui) and [Recommendations](src/recommendations) service. You can monitor the progress in CloudWatch under the `/aws/lambda/RetailDemoStorePersonalizePreCreateCampaigns` log group.

### Developing Services Locally

The Retail Demo Store also supports running the web user interface and backend services in a local container on your machine.  This may be a handy option while testing a fix or enhancement.

[Detailed instructions](./src) are available on how to get going with local development.  Note that you will still need to set up one of the development options described above, and have a working deployment in your AWS account as some of the services will need to access cloud-based services as part of deployment.
