# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
import os
import time
import logging
import boto3
import botocore

from crhelper import CfnResource
from packaging import version
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

min_botocore_version = '1.16.24'

# Check if Lambda runtime needs to be patched with more recent Personalize SDK
# This must be done before creating Personalize clients from boto3.
if version.parse(botocore.__version__) < version.parse(min_botocore_version):
    logger.info('Patching botocore SDK libraries for Personalize')

    dir_path = os.path.dirname(os.path.realpath(__file__))
    models_path = os.path.join(dir_path, 'models')
    
    aws_data_path = set(os.environ.get('AWS_DATA_PATH', '').split(os.pathsep))
    aws_data_path.add(models_path)
    
    os.environ.update({
        'AWS_DATA_PATH': os.pathsep.join(aws_data_path)
    })

    logger.info(os.environ)
else:
    logger.info('Patching botocore SDK for Personalize not required')    

helper = CfnResource()

# Setup Clients
personalize = boto3.client('personalize')
ssm = boto3.client('ssm')
iam = boto3.client('iam')

schemas_to_delete = [ 
    'retaildemostore-schema-users', 
    'retaildemostore-schema-items', 
    'retaildemostore-schema-interactions', 
    'retaildemostore-event-schema' 
]

def get_dataset_arn(dataset_group_name):
    dataset_group_arn = None

    dataset_groups_paginator = personalize.get_paginator('list_dataset_groups')
    for dataset_groups_page in dataset_groups_paginator.paginate():
        for dataset_group in dataset_groups_page['datasetGroups']:
            if dataset_group['name'] == dataset_group_name:
                dataset_group_arn = dataset_group['datasetGroupArn']
                break

    return dataset_group_arn

def delete_filters(dataset_group_arn):
    filters_response = personalize.list_filters(datasetGroupArn = dataset_group_arn, maxResults = 100)
    for filter in filters_response['Filters']:
        logger.info('Deleting filter: ' + filter['filterArn'])
        personalize.delete_filter(filterArn = filter['filterArn'])

    return True
   
def get_solutions(dataset_group_arn):
    solution_arns = []

    solutions_response = personalize.list_solutions(datasetGroupArn = dataset_group_arn, maxResults = 100)
    if 'solutions' in solutions_response:
        for solution in solutions_response['solutions']:
            solution_arns.append(solution['solutionArn'])
            
    logger.info('Solutions found: ' + str(solution_arns))

    return solution_arns

def delete_campaigns(solution_arns):
    logger.info('Clearing related products campaign arn SSM parameter')
    ssm.put_parameter(
        Name='retaildemostore-related-products-campaign-arn',
        Description='Retail Demo Store Related Products Campaign Arn Parameter',
        Value='NONE',
        Type='String',
        Overwrite=True
    )
    logger.info('Clearing product recommendation campaign arn SSM parameter')
    ssm.put_parameter(
        Name='retaildemostore-product-recommendation-campaign-arn',
        Description='Retail Demo Store Product Recommendation Campaign Arn Parameter',
        Value='NONE',
        Type='String',
        Overwrite=True
    )
    logger.info('Clearing personalized ranking campaign arn SSM parameter')
    response = ssm.put_parameter(
        Name='retaildemostore-personalized-ranking-campaign-arn',
        Description='Retail Demo Store Personalized Ranking Campaign Arn Parameter',
        Value='NONE',
        Type='String',
        Overwrite=True
    )

    campaign_count = 0

    for solution_arn in solution_arns:
        campaigns_response = personalize.list_campaigns(solutionArn = solution_arn, maxResults = 100)
        
        if 'campaigns' in campaigns_response:
            for campaign in campaigns_response['campaigns']:
                campaign_count += 1
                if campaign['status'] == 'ACTIVE':
                    logger.info('Deleting campaign: ' + campaign['campaignArn'])
                    
                    personalize.delete_campaign(campaignArn = campaign['campaignArn'])

    return campaign_count == 0

def delete_solutions(dataset_group_arn):
    solution_count = 0

    solutions_response = personalize.list_solutions(datasetGroupArn = dataset_group_arn, maxResults = 100)
    if 'solutions' in solutions_response:
        for solution in solutions_response['solutions']:
            solution_count += 1
            solution_arn = solution['solutionArn']
            if solution['status'] == 'ACTIVE':
                logger.info('Deleting solution: ' + solution_arn)
                personalize.delete_solution(solutionArn = solution_arn)

    return solution_count == 0

def delete_event_trackers(dataset_group_arn):
    ssm.put_parameter(
        Name='retaildemostore-personalize-event-tracker-id',
        Description='Retail Demo Store Personalize Event Tracker ID Parameter',
        Value='NONE',
        Type='String',
        Overwrite=True
    )

    logger.info('Deleting event trackers for dataset group')
    event_tracker_count = 0
    event_trackers_paginator = personalize.get_paginator('list_event_trackers')
    for event_tracker_page in event_trackers_paginator.paginate(datasetGroupArn = dataset_group_arn):
        for event_tracker in event_tracker_page['eventTrackers']:
            event_tracker_count += 1
            if event_tracker['status'] == 'ACTIVE':
                logger.info('Deleting event tracker {}'.format(event_tracker['eventTrackerArn']))
                personalize.delete_event_tracker(eventTrackerArn = event_tracker['eventTrackerArn'])
            
    return event_tracker_count == 0

def delete_datasets(dataset_group_arn):
    logger.info('Deleting datasets for dataset group')
    dataset_count = 0
    dataset_paginator = personalize.get_paginator('list_datasets')

    for dataset_page in dataset_paginator.paginate(datasetGroupArn = dataset_group_arn):
        for dataset in dataset_page['datasets']:
            dataset_count += 1
            if dataset['status'] == 'ACTIVE':
                logger.info('Deleting dataset {}'.format(dataset['datasetArn']))
                personalize.delete_dataset(datasetArn = dataset['datasetArn'])

    return dataset_count == 0            

def delete_dataset_group(dataset_group_arn):
    try:
        logger.info('Deleting dataset group')
        personalize.delete_dataset_group(datasetGroupArn = dataset_group_arn)
        return False
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'ResourceNotFoundException':
            logger.info("Dataset group does not exist")

    return True

def delete_schemas(schemas_to_delete):
    schema_paginator = personalize.get_paginator('list_schemas')
    for schema_page in schema_paginator.paginate():
        for schema in schema_page['schemas']:
            if schema['name'] in schemas_to_delete:
                try:
                    logger.info('Deleting schema {}'.format(schema['schemaArn']))
                    personalize.delete_schema(schemaArn = schema['schemaArn'])
                except ClientError as e:
                    error_code = e.response['Error']['Code']
                    if error_code == 'ResourceNotFoundException':
                        logger.info("Schema does not exist")
                
    logger.info('Done deleting schemas')

    return True

def delete_role():
    try:
        response = iam.detach_role_policy(
            RoleName='RetailDemoStorePersonalizeS3Role',
            PolicyArn='arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess'
        )
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code != 'NoSuchEntity':
            logger.error(e)

    try:
        response = iam.delete_role(
            RoleName='RetailDemoStorePersonalizeS3Role'
        )
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code != 'NoSuchEntity':
            logger.error(e)

    return True

@helper.create
@helper.update
def no_op(_, __):
    # we only delete things here.
    pass

@helper.poll_delete
def poll_delete(event, _):
    ''' Deletes resources one call at a time

    The crhelper will keep calling this function every 2 minutes until we return True. This 
    will ensure we complete the delete process if it takes longer than usual timeout period.
    In practice, the delete process occurs pretty quickly, though.
    '''
    # Name of dataset group that was created in the Personalize workshop notebook or by pre-create Lambda.
    dataset_group_name = event['ResourceProperties'].get('DatasetGroupName', 'retaildemostore')
    logger.info('Deleting resources for Personalize dataset group: ' + dataset_group_name)

    dataset_group_arn = get_dataset_arn(dataset_group_name)

    done = dataset_group_arn is None
    
    if dataset_group_arn:
        # Other than the dataset group, no deps on filters so delete them first.
        delete_filters(dataset_group_arn)

        # Delete rest of dataset group resources from inside out.
        solution_arns = get_solutions(dataset_group_arn)

        if delete_campaigns(solution_arns):
            logger.info('Campaigns fully deleted')
            if delete_solutions(dataset_group_arn):
                logger.info('Solutions and SolutionVersions fully deleted')
                if delete_event_trackers(dataset_group_arn):
                    logger.info('EventTrackers fully deleted')
                    if delete_datasets(dataset_group_arn):
                        logger.info('Datasets fully deleted')
                        if delete_dataset_group(dataset_group_arn):
                            logger.info('DatasetGroup fully deleted')

    # These resources aren't children of a dataset group so are deleted 
    # when the dataset group is done being deleted (or doesn't exist).
    if done and delete_schemas(schemas_to_delete):
        logger.info('Schemas fully deleted')
        delete_role()

        logger.info('IAM Role fully deleted')

        logger.info('All Personalize resources for dataset group {} deleted'.format(dataset_group_name))

        helper.Data['Output'] = 'All Personalize resources for dataset group {} deleted'.format(dataset_group_name)

    # By returning False, we'll get called back in 2 mins. Otherwise returning True completes delete process.
    return done

def lambda_handler(event, context):
    helper(event, context)
