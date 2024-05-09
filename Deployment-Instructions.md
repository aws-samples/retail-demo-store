# Deployment Instructions

These instructions are valid whenever you just want to demo the Retail Demo Store or if you would like to contribute enhancements or features to the Retail Demo Store, please read on for instructions on how to develop and test your changes. Thanks for considering working with this project.

## Step 1: Fork this Repo

We highly recommend to create a fork of the Retail Demo Store respository in your own GitHub account. That enables you to customize the code before deployment.

## Step 2: Create a GitHub Personal Access Token

Create a [GitHub Personal Access Token](https://help.github.com/en/articles/creating-a-personal-access-token-for-the-command-line) in your GitHub account.

Make sure that your token has the "repo", "repo:status", and "admin:repo_hook" permission scopes.

Save your access token in a secure location, you will use it the CloudFormation parameters at deployment time.

## Step 3: Create a S3 Staging Bucket

We recommend to create a dedicated bucket for deployment.

### Bucket Region

Your staging bucket must be in the region in which you plan to deploy the Retail Demo Store.

### Bucket Permissions

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

## Step 4: Staging for Deployment

We recommend to use a Python 3 virtual environment. Current supported version of python is 3.12 (other versions may work but we haven't tested all versions)

```bash
python3.12 -m venv .venv/
source .venv/bin/activate
```

The [stage.sh](stage.sh) script at the root of the repository must be used to upload the deployment resources to your staging S3 bucket if you use this option. The shell uses the local AWS credentials to build and push resources to your custom bucket. 

Example on how to stage your project to a custom bucket and path (note the path is optional but, if specified, must end with '/'):

```bash
./stage.sh MY_CUSTOM_BUCKET S3_PATH/ --skip-virtualenv
```

## Step 5: Deploy the Cloudformation template

The stage script will output a path to your master deployment CloudFormation template.  You can use this link to your S3 bucket to start a new deployment via the CloudFormation console in your AWS Console. Please read and complete any required parameters. The mandatory parameters to fill up are:

* ResourceBucket
* ResourceBucketRelativePath
* CreateOpenSearchServiceLinkedRole

All the others will work by default, take the time to read and decide which parameters you want to use

> [!NOTE] 
> You can also use the command line below.  (replace REGION, MY_CUSTOM_BUCKET and S3_PATH value)
> 
> ```bash
> ./scripts/deploy-cloudformation-stacks.sh DEPLOYMENT_S3_BUCKET REGION STACK_NAME
> ```

## (optional) Developing Services Locally

The Retail Demo Store also supports running the web user interface and backend services in a local container on your machine.  This may be a handy option while testing a fix or enhancement.

[Detailed instructions](./src) are available on how to get going with local development.  Note that you will still need to set up one of the development options described above, and have a working deployment in your AWS account as some of the services will need to access cloud-based services as part of deployment.

## (optional) Integration tests

Integration tests can be run on either

1. Local development (via Docker Compose)
2. Actual (deployed) AWS environment

You can find more information about the running the integration tests in `src/run-tests/README.md`.
