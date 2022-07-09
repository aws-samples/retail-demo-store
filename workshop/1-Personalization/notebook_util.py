# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

""" 
Utility functions for personalization notebooks.
"""

import boto3
import json

cfn = boto3.client('cloudformation')
sagemaker = boto3.client('sagemaker')

def lookup_resource_arn() -> str:
    """ Returns the resource ARN for the current notebook instance """
    with open('/opt/ml/metadata/resource-metadata.json') as f:
        data = json.load(f)
        return data["ResourceArn"]
    
def get_notebook_instance_tags() -> list:
    """ Returns the list of tags associated with the current notebook instance """
    resource_arn = lookup_resource_arn()
    response = sagemaker.list_tags(ResourceArn = resource_arn)
    return response['Tags']

def lookup_uid() -> str:
    """ Returns the value of the 'Uid' tag from the current notebook instance """
    for tag in get_notebook_instance_tags():
        if tag['Key'] == 'Uid':
            return tag['Value']
    return None

def lookup_resource_bucket_and_path() -> tuple:
    """ 
    Returns the resource bucket and relative path from the CloudFormation stack used to 
    launch the current notebook instance 
    """
    bucket_name = relative_path = None
    
    for tag in get_notebook_instance_tags():
        if tag['Key'] == 'aws:cloudformation:stack-name':
            stack_name = tag['Value']

            stack_response = cfn.describe_stacks(StackName = stack_name)
            if stack_response['Stacks']:
                for param in stack_response['Stacks'][0]['Parameters']:
                    if param['ParameterKey'] == 'ResourceBucketRelativePath':
                        relative_path = param['ParameterValue']
                    elif param['ParameterKey'] == 'ResourceBucket':
                        bucket_name = param['ParameterValue']

    return bucket_name, relative_path