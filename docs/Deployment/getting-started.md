# Deployment Instructions

These instructions are valid whenever you just want to demo the Retail Demo Store or if you would like to contribute enhancements or features to the Retail Demo Store, please read on for instructions on how to develop and test your changes. 

Thanks for considering working with this project.

``` mermaid
graph TB
  B[Install the requirements];
  B -->|if you want to customize the demo| C[Fork this Repo];
  C --> D[Create a Github Personal Access Token]
  B --> E;
  D --> E[Create a Staging Bucket];
  E --> F[Stage the code to this bucket];
  F --> G[Deploy Cloudformation Template]
```

## Step 1 : Requirements

Let's review the requirements before deploying the demo store (this was tested on a fresh EC2 instance for the Retail Demo Store. These install prerequisites apply to the Ubuntu AMI.)

### Ensure the instance is up-to-date:
```
sudo apt update
sudo apt upgrade
```

## Verify Python:

```bash
python3 -V
```
You need Python 3.12.3 or higher
If not: ```sudo apt install python3```

## Install Git and clone repo:
```
sudo apt install git
mkdir RetailDemoStore
cd RetailDemoStore/
git clone https://github.com/aws-samples/retail-demo-store
```

!!! Note
    If you plan to customize the demo, we recommend using your fork instead of the aws-samples one (see [fork this repo](#optional-fork-this-repo))


## Packages required for building staging:

```
sudo apt install zip
sudo apt install python3-pip
sudo apt install python3.12-venv
sudo apt install nodejs
sudo apt install npm
```

## Install and configure the AWS CLI:

```
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip
sudo ./aws/install
aws configure
```


## (optional) Fork this Repo

We recommend to create a fork of the Retail Demo Store respository in your own GitHub account. That enables you to customize the code before deployment.

## (optional) Create a GitHub Personal Access Token

Create a [GitHub Personal Access Token](https://help.github.com/en/articles/creating-a-personal-access-token-for-the-command-line) in your GitHub account.

Make sure that your token has the "repo", "repo:status", and "admin:repo_hook" permission scopes.

Save your access token in a secure location, you will use it the CloudFormation parameters at deployment time.

## Step 2: Create a S3 Staging Bucket

Create a dedicated S3 bucket specifically for staging/deployment, and ensure that [**versioning is enabled**](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Versioning.html) for this bucket.

> [!IMPORTANT]  
> Your staging bucket must be in the **region** with in which you plan to deploy the Retail Demo Store.

### Enabling Event Notifications

Setting Up Event Notifications to Amazon EventBridge on an S3 Bucket

Follow these steps to configure your S3 bucket to send event notifications to Amazon EventBridge:

1. Navigate to your S3 bucket in the AWS Management Console. 
2. Click on the Properties tab.
3. Scroll down to the Amazon EventBridge section. 
4. Click the Edit button. 
5. Toggle the option Send notifications to Amazon EventBridge for all events in this bucket to On. 
6. Click Save changes.

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



## Step 3: Staging for Deployment

We recommend to use a Python 3 virtual environment. Current supported version of python is 3.12 (other versions may work but we haven't tested all versions)

```bash
python3.12 -m venv .venv/
source .venv/bin/activate
```

The ``stage.sh`` script at the root of the repository must be used to upload the deployment resources to your staging S3 bucket if you use this option. The shell uses the local AWS credentials to build and push resources to your custom bucket. 

Example on how to stage your project to a custom bucket and path (note the path is optional but, if specified, must end with '/'):

```bash
./stage.sh MY_CUSTOM_BUCKET S3_PATH/ --skip-virtualenv
```

## Step 4: Deploy the Cloudformation template

The stage script will output a path to your master deployment CloudFormation template.  You can use this link to your S3 bucket to start a new deployment via the CloudFormation console in your AWS Console. Please read and complete any required parameters. The mandatory parameters to fill up are:

* ResourceBucket
* ResourceBucketRelativePath
* CreateOpenSearchServiceLinkedRole

All the others will work by default, take the time to read and decide which parameters you want to use

!!!NOTE 

    You can also use the command line below.  (replace REGION, MY_CUSTOM_BUCKET and S3_PATH value).
    This script deploys the retail demo store with standard options, you cannot change any parameters directly
    
    ```bash
    ./scripts/deploy-cloudformation-stacks.sh DEPLOYMENT_S3_BUCKET REGION STACK_NAME
    ```
