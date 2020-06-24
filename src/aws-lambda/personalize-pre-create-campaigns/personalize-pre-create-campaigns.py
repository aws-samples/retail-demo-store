# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

"""
Lambda function designed to be called on a recurring schedule ("rate(5 minutes)")
that will methodically work through the steps of creating Personalize campaigns 
for product and search personalization by completing the following steps.

1. Create schemas for items, users, and interactions.
2. Create dataset group and datasets for items, users, and interactions.
3. Create upload jobs for item, user, and interaction CSVs.
4. Create Event Tracker to receive real-time events from web-ui service.
5. Start execution of Web-UI service in CodePipeline so it picks up the Event 
   Tracker ID in its build-time configuration.
6. Create Solution and Solution Version for related items, item recommendations,
   and personalized reranking recipes.
7. Create Campaigns for related items, item recommendations, and personalized reranking.
8. Store Campaign ARNs in SSM parameters (which are used by Retail Demo Store services
   and workshops).

The function has logic to skip completed steps and pick up where it left off
to continue the overall process. It is useful in cases such as workshops that 
don't focus on or have time to train Personalize models but depend on them. 
For example, the Experimentation workshop.
"""

import json
import boto3
import botocore
import logging
import os

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
    
iam = boto3.client("iam")
ssm = boto3.client('ssm')
sts = boto3.client('sts')
personalize = boto3.client('personalize')
personalize_runtime = boto3.client('personalize-runtime')
cw_events = boto3.client('events')
codepipeline = boto3.client('codepipeline')

def create_schema(schema, name):
    """ Conditionally creates a personalize schema if it does not already exist """
    response=personalize.list_schemas()
    schemas=response["schemas"]
    schema_exists=False
    for s in schemas:
        if s['name'] == name:
            logger.info("Schema " + name + " already exists, not creating")
            schema_exists=True
            schema_arn = s['schemaArn']
            break
        
    if not schema_exists:
        logger.info('Creating schema ' + name)
        create_schema_response = personalize.create_schema(
            name = name,
            schema = json.dumps(schema)
        )
            
        schema_arn = create_schema_response['schemaArn']
        
    return schema_arn
    
def create_dataset(dataset_group_arn, dataset_name, dataset_type, schema_arn):
    """ Conditionally creates dataset if it doesn't already exist """
    response = personalize.list_datasets(datasetGroupArn = dataset_group_arn)
    datasets = response['datasets']
    dataset_exists = False
    for dataset in datasets:
        if dataset['name'] == dataset_name:
            logger.info("Dataset " + dataset_name + " already exists, not creating")
            dataset_exists=True
            dataset_arn = dataset['datasetArn']
            break
        
    if not dataset_exists:
        logger.info('Dataset ' + dataset_name + ' does NOT exist; creating')
        create_dataset_response = personalize.create_dataset(
            datasetType = dataset_type,
            datasetGroupArn = dataset_group_arn,
            schemaArn = schema_arn,
            name=dataset_name
        )
        dataset_arn = create_dataset_response['datasetArn']
        
    return dataset_arn

def create_import_job(job_name, dataset_arn, account_id, region, data_location, role_arn):
    import_job_exists=False
    response=str(personalize.list_dataset_import_jobs(datasetArn = dataset_arn))
    logger.info(response)
    if response.find(job_name) != -1:
        logger.info("Dataset import job "+job_name+" already exists, not creating")
        import_job_exists = True
        import_job_arn="arn:aws:personalize:"+region+":"+account_id+":dataset-import-job/"+job_name
        
    if not import_job_exists:
        logger.info('Creating dataset import job ' + job_name)
        create_dataset_import_job_response = personalize.create_dataset_import_job(
            jobName = job_name,
            datasetArn = dataset_arn,
            dataSource = {
                "dataLocation": data_location
            },
            roleArn = role_arn
        )
        import_job_arn = create_dataset_import_job_response['datasetImportJobArn']
        
    return import_job_arn
    
def is_import_job_active(import_job_arn):
    import_job_response = personalize.describe_dataset_import_job(
        datasetImportJobArn = import_job_arn
    )
    dataset_import_job = import_job_response["datasetImportJob"]
    if "latestDatasetImportJobRun" not in dataset_import_job:
        status = dataset_import_job["status"]
        logger.info("DatasetImportJob {}: {}".format(import_job_arn, status))
    else:
        status = dataset_import_job["latestDatasetImportJobRun"]["status"]
        logger.info("LatestDatasetImportJobRun {}: {}".format(import_job_arn, status))
    
    return status == "ACTIVE"

def is_ssm_parameter_set(parameter_name):
    try:
        response = ssm.get_parameter(Name = parameter_name)
        return response['Parameter']['Value'] != 'NONE'
    except ssm.exceptions.ParameterNotFound:
        return False

def create_personalize_role(role_name):
    role_arn = None

    try:
        response = iam.get_role(RoleName = role_name)
        role_arn = response['Role']['Arn']
    except iam.exceptions.NoSuchEntityException:
        logger.info('Creating IAM role ' + role_name)
        
        assume_role_policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                  "Effect": "Allow",
                  "Principal": {
                    "Service": "personalize.amazonaws.com"
                  },
                  "Action": "sts:AssumeRole"
                }
            ]
        }
        
        create_role_response = iam.create_role(
            RoleName = role_name,
            AssumeRolePolicyDocument = json.dumps(assume_role_policy_document)
        )
        
        iam.attach_role_policy(
            RoleName = role_name,
            PolicyArn = "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
        )
        
        # Just print role ARN and return None so we cycle back to check on next call.
        logger.info('Created IAM Role: {}'.format(create_role_response["Role"]["Arn"]))

    return role_arn

def delete_event_rule(rule_name):
    ''' Deletes CloudWatch event rule used to trigger this lambda function on a recurring schedule '''
    try:
        response = cw_events.list_targets_by_rule(Rule = rule_name)

        if len(response['Targets']) > 0:
            logger.info('Removing event targets from rule {}'.format(rule_name))

            target_ids = []

            for target in response['Targets']:
                target_ids.append(target['Id'])

            response = cw_events.remove_targets(
                Rule = rule_name,
                Ids = target_ids
            )

        logger.info('Deleting event rule {}'.format(rule_name))
        cw_events.delete_rule(Name = rule_name)

    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'ResourceNotFoundException':
            logger.warn('CloudWatch event rule to delete not found')
        else:
            logger.error(e)


def rebuild_webui_service(region, account_id):
    ''' Initiates a build/deploy of the Web UI service so that event tracker is picked up '''

    logger.info('Looking for pipeline with tag "RetailDemoStoreServiceName=web-ui" to initiate execution')

    restarted = False
    
    pipeline_iterator = codepipeline.get_paginator('list_pipelines').paginate()

    for pipelines in pipeline_iterator:
        for pipeline in pipelines['pipelines']:
            logger.debug('Checking pipeline {} for web-ui tag'.format(pipeline['name']))
            
            arn = 'arn:aws:codepipeline:{}:{}:{}'.format(region, account_id, pipeline['name'])
            
            response_tags = codepipeline.list_tags_for_resource(resourceArn=arn)
            
            for tag in response_tags['tags']:
                if tag['key'] == 'RetailDemoStoreServiceName' and tag['value'] == 'web-ui':
                    logger.info('Found web-ui pipeline; attempting to start execution')
                    
                    response_start = codepipeline.start_pipeline_execution(name=pipeline['name'])
                    
                    logger.info('Pipeline execution started with executionId: {}'.format(response_start['pipelineExecutionId']))
                    
                    restarted = True
                    
                if restarted:
                    break
                
            if restarted:
                break
            
        if restarted:
            break
            
    if not restarted:
        logger.warn('Pipeline with tag "RetailDemoStoreServiceName=web-ui" not restarted; does pipeline and/or tag exist?')

def create_recent_purchase_filter(dataset_group_arn, ssm_parameter_name):
    ''' Creates Personalize Filter that excludes recommendations for recently purchased products '''

    logger.info('Creating purchased product filter')

    response = personalize.create_filter(
        name = 'retaildemostore-filter-purchased-products',
        datasetGroupArn = dataset_group_arn,
        filterExpression = 'EXCLUDE itemId WHERE INTERACTIONS.event_type in ("OrderCompleted")'
    )
 
    filter_arn = response['filterArn']

    logger.info('Setting purchased product filter ARN as SSM parameter ' + ssm_parameter_name)

    ssm.put_parameter(
        Name=ssm_parameter_name,
        Description='Retail Demo Store Personalize Filter Purchased Products Arn Parameter',
        Value='{}'.format(filter_arn),
        Type='String',
        Overwrite=True
    )

def lambda_handler(event, context):
    logger.debug('## ENVIRONMENT VARIABLES')
    logger.debug(os.environ)
    logger.debug('## EVENT')
    logger.debug(event)

    bucket = os.environ['csv_bucket']
    bucket_path = os.environ.get('csv_path', '')

    items_filename = bucket_path + "items.csv"
    users_filename = bucket_path + "users.csv"
    interactions_filename = bucket_path + "interactions.csv"
    
    session = boto3.session.Session()
    region = session.region_name
    account_id = sts.get_caller_identity().get('Account')

    dataset_group_name = 'retaildemostore'
    
    related_product_campaign_arn_param = 'retaildemostore-related-products-campaign-arn'
    product_campaign_arn_param = 'retaildemostore-product-recommendation-campaign-arn'
    rerank_campaign_arn_param = 'retaildemostore-personalized-ranking-campaign-arn'
    role_name = "RetailDemoStorePersonalizeS3Role"
    event_tracking_id_param = 'retaildemostore-personalize-event-tracker-id'
    filter_purchased_arn_param = 'retaildemostore-personalize-filter-purchased-arn'

    # Info on CloudWatch event rule used to repeatedely call this function.
    lambda_event_rule_name = os.environ['lambda_event_rule_name']

    # If SSM parameters for campaign arns are already set, we are done.
    related_product_campaign_arn_set = is_ssm_parameter_set(related_product_campaign_arn_param)
    product_campaign_arn_set = is_ssm_parameter_set(product_campaign_arn_param)
    rerank_campaign_arn_set = is_ssm_parameter_set(rerank_campaign_arn_param)
    event_tracking_id_set = is_ssm_parameter_set(event_tracking_id_param)
    filter_purchased_arn_set = is_ssm_parameter_set(filter_purchased_arn_param)

    # Short-circuit rest of logic of all campaign ARNs are set as parameters. Means there's nothing to do.
    if (related_product_campaign_arn_set and 
            product_campaign_arn_set and 
            rerank_campaign_arn_set and 
            event_tracking_id_set and
            filter_purchased_arn_set):

        logger.info('ARNs for related products, user recommendations, reranking campaigns, recent purchase filter set as SSM parameters; nothing to do')

        # No need for this lambda function to be called anymore so delete CW event rule that has been calling us.
        delete_event_rule(lambda_event_rule_name)

        return {
            'statusCode': 200,
            'body': json.dumps('SSM parameters for related products, user recommendations, reranking campaign, and recent purchase filter ARNs already set; nothing to do')
        }

    if not related_product_campaign_arn_set:
        logger.info(related_product_campaign_arn_param + ' SSM parameter is not set yet; proceeding with step verification/completion process')

    if not product_campaign_arn_set:
        logger.info(product_campaign_arn_param + ' SSM parameter is not set yet; proceeding with step verification/completion process')

    if not rerank_campaign_arn_set:
        logger.info(rerank_campaign_arn_param + ' SSM parameter is not set yet; proceeding with step verification/completion process')

    if not filter_purchased_arn_set:
        logger.info(filter_purchased_arn_param + ' SSM parameter is not set yet; proceeding with step verification/completion process')

    # Create personalize role, if necessary.
    role_arn = create_personalize_role(role_name)
    if not role_arn:
        return {
            'statusCode': 200,
            'body': json.dumps('Waiting for IAM role to be consistent')
        }

    items_schema = {
        "type": "record",
        "name": "Items",
        "namespace": "com.amazonaws.personalize.schema",
        "fields": [
            {
                "name": "ITEM_ID",
                "type": "string"
            },
            {
                "name": "CATEGORY",
                "type": "string",
                "categorical": True
            },
            {
                "name": "STYLE",
                "type": "string",
                "categorical": True
            }
        ],
        "version": "1.0"
    }
    
    users_schema = {
        "type": "record",
        "name": "Users",
        "namespace": "com.amazonaws.personalize.schema",
        "fields": [
            {
                "name": "USER_ID",
                "type": "string"
            },
            {
                "name": "AGE",
                "type": "int"
            },
            {
                "name": "GENDER",
                "type": "string",
                "categorical": True
            }
        ],
        "version": "1.0"
    }
    
    interactions_schema = {
        "type": "record",
        "name": "Interactions",
        "namespace": "com.amazonaws.personalize.schema",
        "fields": [
            {
                "name": "ITEM_ID",
                "type": "string"
            },
            {
                "name": "USER_ID",
                "type": "string"
            },
            {
                "name": "EVENT_TYPE",
                "type": "string"
            },
            {
                "name": "TIMESTAMP",
                "type": "long"
            }
        ],
        "version": "1.0"
    }

    # Conditionally create schemas
    items_schema_arn = create_schema(items_schema, "retaildemostore-schema-items")
    users_schema_arn = create_schema(users_schema, "retaildemostore-schema-users")
    interactions_schema_arn = create_schema(interactions_schema, "retaildemostore-schema-interactions")
    
    # Create dataset group if it doesn't exist
    response=personalize.list_dataset_groups()
    datasetGroups=response['datasetGroups']
    group_exists=False
    
    for datasetGroup in datasetGroups:
        if datasetGroup['name'] == dataset_group_name:
            logger.info("Dataset group "+dataset_group_name+" already exists, not creating")
            group_exists=True
            dataset_group_arn = datasetGroup['datasetGroupArn']
            break
        
    if not group_exists:      
        create_dataset_group_response = personalize.create_dataset_group(name = dataset_group_name)
        dataset_group_arn = create_dataset_group_response['datasetGroupArn']

    describe_dataset_group_response = personalize.describe_dataset_group(
        datasetGroupArn = dataset_group_arn
    )

    status = describe_dataset_group_response["datasetGroup"]["status"]
    logger.info("DatasetGroup: {}".format(status))

    if status == "CREATE FAILED":
        logger.error('DatasetGroup {} create failed: {}'.format(dataset_group_name, json.dumps(describe_dataset_group_response)))
        return {
            'statusCode': 200,
            'body': json.dumps('DatasetGroup create failed! Campaign pre-create aborted.')
        }

    if status != "ACTIVE":
        return {
            'statusCode': 200,
            'body': json.dumps('DatasetGroup NOT active yet')
        }

    # Create datasets
    items_dataset_arn = create_dataset(dataset_group_arn, 'retaildemostore-dataset-items', 'ITEMS', items_schema_arn)
    users_dataset_arn = create_dataset(dataset_group_arn, 'retaildemostore-dataset-users', 'USERS', users_schema_arn)
    interactions_dataset_arn = create_dataset(dataset_group_arn, 'retaildemostore-dataset-interactions', 'INTERACTIONS', interactions_schema_arn)

    # Create dataset import jobs
    items_dataset_import_job_arn = create_import_job('retaildemostore-dataset-items-import-job', items_dataset_arn, account_id, region, "s3://{}/{}".format(bucket, items_filename), role_arn)
    users_dataset_import_job_arn = create_import_job('retaildemostore-dataset-users-import-job', users_dataset_arn, account_id, region, "s3://{}/{}".format(bucket, users_filename), role_arn)
    interactions_dataset_import_job_arn = create_import_job('retaildemostore-dataset-interactions-import-job', interactions_dataset_arn, account_id, region, "s3://{}/{}".format(bucket, interactions_filename), role_arn)

    # Make sure all import jobs are done/active before continuing
    if not is_import_job_active(items_dataset_import_job_arn):
        logger.info("Items import job is NOT active yet")
        return {
            'statusCode': 200,
            'body': json.dumps('Items import job is NOT active yet')
        }
        
    if not is_import_job_active(users_dataset_import_job_arn):
        logger.info("Users import job is NOT active yet")
        return {
            'statusCode': 200,
            'body': json.dumps('Users import job is NOT active yet')
        }
        
    if not is_import_job_active(interactions_dataset_import_job_arn):
        logger.info("Interactions import job is NOT active yet")
        return {
            'statusCode': 200,
            'body': json.dumps('Interactions import job is NOT active yet')
        }

    # Create event tracker, if necessary.
    if not event_tracking_id_set:
        # Either hasn't been created yet or isn't active yet.
        list_event_trackers_response = personalize.list_event_trackers(datasetGroupArn = dataset_group_arn)
        if len(list_event_trackers_response['eventTrackers']) == 0:
            logger.info('Event Tracker does not exist; creating')
            event_tracker = personalize.create_event_tracker(
                datasetGroupArn=dataset_group_arn,
                name='retaildemostore-event-tracker'
            )

            if event_tracker.get('trackingId'):
                event_tracking_id = event_tracker['trackingId']
                logger.info('Setting event tracking ID {} as SSM parameter'.format(event_tracking_id))

                ssm.put_parameter(
                    Name=event_tracking_id_param,
                    Description='Retail Demo Store Personalize Event Tracker ID Parameter',
                    Value='{}'.format(event_tracking_id),
                    Type='String',
                    Overwrite=True
                )

                event_tracking_id_set = True

                # Trigger rebuild of Web UI service so event tracker gets picked up.
                rebuild_webui_service(region, account_id)

            return {
                'statusCode': 200,
                'body': json.dumps('Event tracker created; waiting for it to become active')
            }
        else:
            event_tracker = list_event_trackers_response['eventTrackers'][0]
            logger.info("Event Tracker: {}".format(event_tracker['status']))

            if event_tracker['status'] == 'CREATE FAILED':
                logger.error('Event tracker create failed: {}'.format(json.dumps(event_tracker)))
                return {
                    'statusCode': 200,
                    'body': json.dumps('Event tracker CREATE_FAILED; aborting process')
                }

    # Create recent product purchase filter, if necessary
    if not filter_purchased_arn_set:
        create_recent_purchase_filter(dataset_group_arn, filter_purchased_arn_param)
        filter_purchased_arn_set = True

    # Create related product, product recommendation, and rerank solutions if they doesn't exist
    related_recipe_arn = "arn:aws:personalize:::recipe/aws-sims"
    related_solution_name = related_campaign_name = "retaildemostore-related-products"
    product_recipe_arn = "arn:aws:personalize:::recipe/aws-hrnn-metadata"
    product_solution_name = product_campaign_name = "retaildemostore-product-personalization"
    rerank_recipe_arn = "arn:aws:personalize:::recipe/aws-personalized-ranking"
    rerank_solution_name = rerank_campaign_name = "retaildemostore-personalized-ranking"

    solution_created = False
    list_solutions_response = str(personalize.list_solutions(datasetGroupArn=dataset_group_arn))

    if list_solutions_response.find(related_solution_name) != -1:
        logger.info("Related product solution "+related_solution_name+" already exists, not creating")
        related_solution_arn="arn:aws:personalize:"+region+":"+account_id+":solution/"+related_solution_name
    else:    
        create_solution_response = personalize.create_solution(
            name = related_solution_name,
            datasetGroupArn = dataset_group_arn,
            recipeArn = related_recipe_arn,
            performHPO = True,
            eventType = "ProductViewed"
        )

        logger.info("Product solution "+related_solution_name+" created")

        related_solution_arn = create_solution_response['solutionArn']
        solution_created = True

    if list_solutions_response.find(product_solution_name) != -1:
        logger.info("Product solution "+product_solution_name+" already exists, not creating")
        product_solution_arn="arn:aws:personalize:"+region+":"+account_id+":solution/"+product_solution_name
    else:    
        create_solution_response = personalize.create_solution(
            name = product_solution_name,
            datasetGroupArn = dataset_group_arn,
            recipeArn = product_recipe_arn,
            performHPO = True,
            eventType = "ProductViewed"
        )

        logger.info("Product solution "+product_solution_name+" created")

        product_solution_arn = create_solution_response['solutionArn']
        solution_created = True

    if list_solutions_response.find(rerank_solution_name) != -1:
        logger.info("Rerank solution "+rerank_solution_name+" already exists, not creating")
        rerank_solution_arn="arn:aws:personalize:"+region+":"+account_id+":solution/"+rerank_solution_name
    else:    
        create_solution_response = personalize.create_solution(
            name = rerank_solution_name,
            datasetGroupArn = dataset_group_arn,
            recipeArn = rerank_recipe_arn,
            performHPO = True,
            eventType = "ProductViewed"
        )

        logger.info("Product solution "+rerank_solution_name+" created")

        rerank_solution_arn = create_solution_response['solutionArn']
        solution_created = True

    if solution_created:
        logger.info("Solution(s) create initiated; waiting for next iteration to create versions")
        return {
            'statusCode': 200,
            'body': json.dumps('Solution(s) create initiated; waiting for next call to create versions')
        }

    # Create related product solution version if it doesn't exist
    response=personalize.list_solution_versions(solutionArn=related_solution_arn)
    if response['solutionVersions']:
        logger.info("Related product Solution Version for "+related_solution_name+" already exists, not creating")
        related_solution_version_arn = response['solutionVersions'][0]['solutionVersionArn']
    else:
        logger.info('Creating Related Product SolutionVersion')
        create_solution_version_response = personalize.create_solution_version(
            solutionArn = related_solution_arn)
        related_solution_version_arn = create_solution_version_response['solutionVersionArn']

    # Create product recommendation solution version if it doesn't exist
    response=personalize.list_solution_versions(solutionArn=product_solution_arn)
    if response['solutionVersions']:
        logger.info("Product Solution Version for "+product_solution_name+" already exists, not creating")
        product_solution_version_arn=response['solutionVersions'][0]['solutionVersionArn']
    else:
        logger.info('Creating Product Recommendation SolutionVersion')
        create_solution_version_response = personalize.create_solution_version(
            solutionArn = product_solution_arn)
        product_solution_version_arn = create_solution_version_response['solutionVersionArn']

    # Create search solution version if it doesn't exist
    response=personalize.list_solution_versions(solutionArn=rerank_solution_arn)
    if response['solutionVersions']:
        logger.info("Rerank Solution Version for "+rerank_solution_name+" already exists, not creating")
        rerank_solution_version_arn=response['solutionVersions'][0]['solutionVersionArn']
    else:
        logger.info('Creating Rerank SolutionVersion')
        create_solution_version_response = personalize.create_solution_version(
            solutionArn = rerank_solution_arn)
        rerank_solution_version_arn = create_solution_version_response['solutionVersionArn']

    # Make sure related product solution version is active
    describe_solution_version_response = personalize.describe_solution_version(
        solutionVersionArn = related_solution_version_arn
    )
    status = describe_solution_version_response["solutionVersion"]["status"]
    logger.info("Related product SolutionVersion Status is: {}".format(status))
    if status != "ACTIVE":
        logger.info("Related product solution version status is NOT active")
        return {
            'statusCode': 200,
            'body': json.dumps('Related product solution version status is NOT active')
        }

    # Create related product campaign if it doesn't exist    
    list_campaigns_response = personalize.list_campaigns(
        solutionArn = related_solution_arn
    )
    if list_campaigns_response['campaigns']:
        for campaign in list_campaigns_response['campaigns']:
            status = campaign['status']
            if status != 'ACTIVE':
                logger.info('Campaign ' + campaign['campaignArn'] + ' is NOT active; waiting')
                return {
                    'statusCode': 200,
                    'body': json.dumps('Related product campaign status is NOT active')
                }
                
            related_campaign_arn = campaign['campaignArn']

            # Finally, set the campaign arn as the system parameter expected by services
            logger.info("Setting related product campaignArn " + related_campaign_arn + " as system parameter")
            response = ssm.put_parameter(
                Name=related_product_campaign_arn_param,
                Description='Retail Demo Store Related Products Campaign Arn Parameter',
                Value='{}'.format(related_campaign_arn),
                Type='String',
                Overwrite=True
            )
    else:
        logger.info('Creating related product campaign')
        personalize.create_campaign(
            name = related_campaign_name,
            solutionVersionArn = related_solution_version_arn,
            minProvisionedTPS = 1
        )
        return {
            'statusCode': 200,
            'body': json.dumps('Initiated create related product campaign; will check back for status')
        }

    # Make sure product recommendation solution version is active
    describe_solution_version_response = personalize.describe_solution_version(
        solutionVersionArn = product_solution_version_arn
    )
    status = describe_solution_version_response["solutionVersion"]["status"]
    logger.info("Product recommendation SolutionVersion Status is: {}".format(status))
    if status != "ACTIVE":
        logger.info("Product recommendation solution version status is NOT active")
        return {
            'statusCode': 200,
            'body': json.dumps('Product recommendation solution version status is NOT active')
        }

    # Create product recommendation campaign if it doesn't exist    
    list_campaigns_response = personalize.list_campaigns(
        solutionArn = product_solution_arn
    )
    if list_campaigns_response['campaigns']:
        for campaign in list_campaigns_response['campaigns']:
            status = campaign['status']
            if status != 'ACTIVE':
                logger.info('Campaign ' + campaign['campaignArn'] + ' is NOT active; waiting')
                return {
                    'statusCode': 200,
                    'body': json.dumps('Product recommendation campaign status is NOT active')
                }
                
            product_campaign_arn = campaign['campaignArn']

            # Finally, set the campaign arn as the system parameter expected by services
            logger.info("Setting product campaignArn " + product_campaign_arn + " as system parameter")
            response = ssm.put_parameter(
                Name=product_campaign_arn_param,
                Description='Retail Demo Store Product Recommendation Campaign Arn Parameter',
                Value='{}'.format(product_campaign_arn),
                Type='String',
                Overwrite=True
            )
    else:
        logger.info('Creating product personalization campaign')
        personalize.create_campaign(
            name = product_campaign_name,
            solutionVersionArn = product_solution_version_arn,
            minProvisionedTPS = 1
        )
        return {
            'statusCode': 200,
            'body': json.dumps('Initiated create product campaign; will check back for status')
        }

    # Make sure reranking solution version is active
    describe_solution_version_response = personalize.describe_solution_version(
        solutionVersionArn = rerank_solution_version_arn
    )
    status = describe_solution_version_response["solutionVersion"]["status"]
    logger.info("Reranking SolutionVersion Status is: {}".format(status))
    if status != "ACTIVE":
        logger.info("Reranking solution version status is NOT active")
        return {
            'statusCode': 200,
            'body': json.dumps('Reranking solution version status is NOT active')
        }

    # Create reranking campaign if it doesn't exist    
    list_campaigns_response = personalize.list_campaigns(
        solutionArn = rerank_solution_arn
    )
    if list_campaigns_response['campaigns']:
        for campaign in list_campaigns_response['campaigns']:
            status = campaign['status']
            if status != 'ACTIVE':
                logger.info('Campaign ' + campaign['campaignArn'] + ' is NOT active; waiting')
                return {
                    'statusCode': 200,
                    'body': json.dumps('Rerank campaign status is NOT active')
                }
                
            rerank_arn = campaign['campaignArn']

            # Finally, set the campaign arn as the system parameter expected by services
            logger.info("Setting rerank campaignArn " + rerank_arn + " as system parameter")
            response = ssm.put_parameter(
                Name=rerank_campaign_arn_param,
                Description='Retail Demo Store Personalized Reranking Campaign Arn Parameter',
                Value='{}'.format(rerank_arn),
                Type='String',
                Overwrite=True
            )
    else:
        logger.info('Creating personalized reranking campaign')
        personalize.create_campaign(
            name = rerank_campaign_name,
            solutionVersionArn = rerank_solution_version_arn,
            minProvisionedTPS = 1
        )
        return {
            'statusCode': 200,
            'body': json.dumps('Initiated create personalized reranking campaign; will check back for status')
        }

    # If we get here... all campaigns have been successfully created!
    logger.info('Related product, Product recommendation, and Personalized reranking campaigns fully provisioned!')

    # No need for this lambda function to be called anymore so delete CW event rule that has been calling us.
    delete_event_rule(lambda_event_rule_name)

    return {
        'statusCode': 200,
        'body': json.dumps('Related product, Product recommendation, and Personalized reranking campaigns fully provisioned!')
    }