from aws_lambda_powertools import Logger
from crhelper import CfnResource
import boto3
from botocore.exceptions import ClientError

client = boto3.client('s3control')
logger = Logger(utc=True)
helper = CfnResource()

def create_job(image_prefix: str, account_id: str, bucket: str, lambda_function_arn) -> None:
    try:
        client.client.create_job(
            AccountId=account_id,
            ConfirmationRequired=False,
            Operation={
                'LambdaInvoke': {
                    'FunctionArn': lambda_function_arn,
                }
            },
            Report={
                'Enabled': False
            },
            ManifestGenerator={
                'S3JobManifestGenerator': {
                    'SourceBucket': bucket,
                    'Filter': {
                        'KeyNameConstraint': {
                            'MatchAnyPrefix': [image_prefix]
                        }
                    }
                }
            }
        )
    except ClientError as error:
        logger.exception(f"Unable to create S3 control job for: {image_prefix}")
        raise error

@helper.create  
def create(event, _):
    prefixes=event['ResourceProperties']['ImagePrefixes'].split(',')
    account_id=event['ResourceProperties']['AccountId']
    bucket=event['ResourceProperties']['Bucket']
    lambda_function_arn=event['ResourceProperties']['S3BatchJobLambdaFunctionArn']
    for image_prefix in prefixes:
        create_job(image_prefix.strip(), account_id, bucket, lambda_function_arn)

def lambda_handler(event, context):
    """
    S3 Batch Operations Job launcher function.
    For each image prefix, launch an S3 Batch Operations Job    
    """
    helper(event, context)    