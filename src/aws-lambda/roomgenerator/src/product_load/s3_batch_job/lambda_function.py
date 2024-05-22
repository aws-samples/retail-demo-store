from aws_lambda_powertools import Logger
from crhelper import CfnResource
from pathlib import PurePath
import boto3
from botocore.exceptions import ClientError

client = boto3.client('s3control')
logger = Logger(utc=True)
helper = CfnResource()

def create_job(image_prefix: str, account_id: str, bucket: str, lambda_function_arn: str, role_arn: str) -> str:
    try:
        response = client.create_job(
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
                    'EnableManifestOutput': False,
                    'SourceBucket': bucket,                
                    'Filter': {
                        'KeyNameConstraint': {
                            'MatchAnyPrefix': [image_prefix]
                        }
                    }                    
                }                
            },
            RoleArn=role_arn,
            Description='Resize product images',
            Priority=99
        )        
    except ClientError as error:
        logger.exception(f"Unable to create S3 control job for: {image_prefix}")
        raise error
    else:
        return response['JobId']

@helper.create  
def create(event, _):
    prefixes =  event['ResourceProperties']['ImagePrefixes'].split(',')
    params = {        
        'account_id': event['ResourceProperties']['AccountId'],
        'bucket': event['ResourceProperties']['Bucket'],
        'lambda_function_arn': event['ResourceProperties']['S3BatchJobLambdaFunctionArn'],
        'role_arn': event['ResourceProperties']['RoleArn']
    }

    for image_prefix in prefixes:
        job_id = create_job(image_prefix.strip(), **params)
        path = PurePath(image_prefix)
        helper.Data.update({path.name: job_id})

def lambda_handler(event, context):
    """
    S3 Batch Operations Job launcher function.
    For each image prefix, launch an S3 Batch Operations Job    
    """
    helper(event, context)    