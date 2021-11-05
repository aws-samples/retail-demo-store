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
import uuid
from crhelper import CfnResource
import urllib3

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
personalize = boto3.client('personalize')
personalize_runtime = boto3.client('personalize-runtime')
cw_events = boto3.client('events')
codepipeline = boto3.client('codepipeline')
cloudformation_helper = CfnResource()

sts = boto3.client('sts')

# Where our data is for training
bucket = os.environ['csv_bucket']
bucket_path = os.environ.get('csv_path', '')

items_filename = bucket_path + f"items.csv"
users_filename = bucket_path + f"users.csv"
interactions_filename = bucket_path + f"interactions.csv"
offer_interactions_filename = bucket_path + f"offer_interactions.csv"

session = boto3.session.Session()
region = session.region_name
account_id = sts.get_caller_identity().get('Account')

# Dataset group names are dynamically generated
dataset_group_name_root_products = 'retaildemoproducts-'
dataset_group_name_root_offers = 'retaildemooffers-'

# Exactly what we want train is stored in this SS parameter - or we generate it ourselves with a default
# if it does not exist.
training_config_param_name = 'retaildemostore-training-config'  # ParameterPersonalizeTrainConfig
training_state_param_name = 'retaildemostore-training-state'

role_name = os.environ.get('Uid') + '-PersonalizeS3'
event_tracking_id_param = 'retaildemostore-personalize-event-tracker-id'
do_deploy_offers_campaign = os.environ['DeployPersonalizedOffersCampaign'].strip().lower() in ['yes', 'true', '1']

filters_config = [
     {'arn_param': 'retaildemostore-personalize-filter-purchased-arn',
      'filter_name': 'retaildemostore-filter-purchased-products',
      'filter_expression': 'EXCLUDE itemId WHERE INTERACTIONS.event_type IN ("OrderCompleted")'},
      {'arn_param': 'retaildemostore-personalize-filter-cstore-arn',
       'filter_name': 'retaildemostore-filter-cstore-products',
       'filter_expression': 'EXCLUDE itemId WHERE ITEMS.CATEGORY NOT IN ("hot drinks", "salty snacks", "hot dispensed", "food service")'}
     ]

datasetgroup_name_param = 'retaildemostore-personalize-datasetgroup-name'

all_campaign_types_products = ['retaildemostore-related-products',
                               'retaildemostore-product-personalization',
                               'retaildemostore-personalized-ranking']

all_campaign_types_offers = ['retaildemostore-personalized-offers']

campaign_type_to_event_type = {
    "retaildemostore-related-products": "ProductViewed",
    "retaildemostore-product-personalization": "ProductViewed",
    "retaildemostore-personalized-ranking": "ProductViewed",
    "retaildemostore-personalized-offers": "OfferConverted",
}

campaign_type_to_recipe_arn = {
    "retaildemostore-related-products": "arn:aws:personalize:::recipe/aws-sims",
    "retaildemostore-product-personalization": "arn:aws:personalize:::recipe/aws-user-personalization",
    "retaildemostore-personalized-ranking": "arn:aws:personalize:::recipe/aws-personalized-ranking",
    "retaildemostore-personalized-offers": "arn:aws:personalize:::recipe/aws-user-personalization"
}

campaign_type_to_ssm_param = {
    "retaildemostore-related-products": "retaildemostore-related-products-campaign-arn",
    "retaildemostore-product-personalization": "retaildemostore-product-recommendation-campaign-arn",
    "retaildemostore-personalized-ranking": "retaildemostore-personalized-ranking-campaign-arn",
    "retaildemostore-personalized-offers": "retaildemostore-personalized-offers-campaign-arn"
}

# Info on CloudWatch event rule used to repeatedely call this function.
lambda_event_rule_name = os.environ['lambda_event_rule_name']

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
        },
        {
            "name": "DESCRIPTION",
            "type": "string",
            "textual": True
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

interactions_schema_products = {
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
        },
        {
            "name": "DISCOUNT",  # This is the contextual metadata - "Yes" or "No".
            "type": "string",
            "categorical": True
        }
    ],
    "version": "1.0"
}

interactions_schema_offers = {
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

dataset_type_to_detail_products = {
    'ITEMS': {'schema': {'name': 'retaildemostore-schema-items',
                         'avro': items_schema},
              'filename': items_filename},
    'USERS': {'schema': {'name': 'retaildemostore-schema-users',
                         'avro': users_schema},
              'filename': users_filename},
    'INTERACTIONS': {'schema': {'name': 'retaildemostore-schema-interactions-products',
                                'avro': interactions_schema_products},
                     'filename': interactions_filename}}

dataset_type_to_detail_offers = {
    'INTERACTIONS': {'schema': {'name': 'retaildemostore-schema-interactions-offers',
                                'avro': interactions_schema_offers},
                     'filename': offer_interactions_filename}}


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
        response = ssm.get_parameter(Name=parameter_name)
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


def delete_personalize_role():
    try:
        response = iam.detach_role_policy(
            RoleName=os.environ.get('Uid')+'-PersonalizeS3',
            PolicyArn='arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess'
        )
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code != 'NoSuchEntity':
            logger.error(e)

    try:
        response = iam.delete_role(
            RoleName=os.environ.get('Uid')+'-PersonalizeS3'
        )
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code != 'NoSuchEntity':
            logger.error(e)

    return True


def enable_event_rule(rule_name):
    try:
        logger.info('Enabling event rule {}'.format(rule_name))
        cw_events.enable_rule(Name=rule_name)

    except cw_events.exceptions.ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'ResourceNotFoundException':
            logger.error('CloudWatch event rule to enable not found')
            raise
        else:
            logger.error(e)
            raise

def disable_event_rule(rule_name):
    """
    Disables the CloudWatch event rule used to trigger this lambda function on a recurring schedule.
    Can be preferrable to deleting the rule because it is then easy to re-instate exactly the same rule by
    simply enabling it.
    Args:
        rule_name (str): Rule to disable
    """
    try:
        logger.info('Disabling event rule {}'.format(rule_name))
        cw_events.disable_rule(Name=rule_name)

    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'ResourceNotFoundException':
            logger.warning('CloudWatch event rule to disable not found')
        else:
            logger.error(e)


def delete_personalize_schemas(schemas_to_delete):
    schema_paginator = personalize.get_paginator('list_schemas')
    for schema_page in schema_paginator.paginate():
        for schema in schema_page['schemas']:
            if schema['name'] in schemas_to_delete:
                try:
                    logger.info('Deleting schema {}'.format(schema['schemaArn']))
                    personalize.delete_schema(schemaArn=schema['schemaArn'])
                except ClientError as e:
                    error_code = e.response['Error']['Code']
                    if error_code == 'ResourceNotFoundException':
                        logger.info("Schema does not exist")

    logger.info('Done deleting schemas')

    return True


def delete_event_rule(rule_name):
    """Deletes CloudWatch event rule used to trigger this lambda function on a recurring schedule """
    try:
        response = cw_events.list_targets_by_rule(Rule = rule_name)

        if len(response['Targets']) > 0:
            logger.info('Removing event targets from rule {}'.format(rule_name))

            target_ids = []

            for target in response['Targets']:
                target_ids.append(target['Id'])

            response = cw_events.remove_targets(
                Rule=rule_name,
                Ids=target_ids
            )

        logger.info('Deleting event rule {}'.format(rule_name))
        cw_events.delete_rule(Name=rule_name)

    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'ResourceNotFoundException':
            logger.warning('CloudWatch event rule to delete not found')
        else:
            logger.error(e)


def rebuild_webui_service(region, account_id):
    """ Initiates a build/deploy of the Web UI service so that event tracker is picked up """

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
        logger.warning('Pipeline with tag "RetailDemoStoreServiceName=web-ui" not restarted; does pipeline and/or tag exist?')


def create_campaign_polling(dataset_group_arn, recipe_arn,
                            campaign_solution_name, event_type,
                            **kwargs):
    """
    For a particular campaign name (which also serves as the solution name), build the solution, one solution version
    and one campaign. This function is meant to be called repeatedly (polling) till it returns the campaign Arn.
    Args:
        dataset_group_arn: Where to build the campaign
        recipe_arn: Which recipe to build
        campaign_solution_name: What name to build it under
        event_type: Which event type to build it with (see Amazon Personalize docs for details of how that works).
        kwargs: Other arguments which are ignored. This is to allow training configs to be passed around.

    Returns:
        Arn if desired campaign has been created or failed.
        None otherwise.
    """

    # We grab the below to reconstruct Arns. There are other ways to do this but it is tested and working, so
    # we do it this way.
    session = boto3.session.Session()
    region = session.region_name
    account_id = sts.get_caller_identity().get('Account')

    # We see if the solution name is created by looking through the string of all solutions
    # - this is slightly unsafe but it has been tested and is working in this codebase.
    list_solutions_response = str(personalize.list_solutions(datasetGroupArn=dataset_group_arn))

    if list_solutions_response.find(campaign_solution_name) != -1:
        solution_arn="arn:aws:personalize:"+region+":"+account_id+":solution/"+campaign_solution_name
    else:
        logger.info("Solution " + campaign_solution_name + " to be created.")
        create_solution_response = personalize.create_solution(
            name=campaign_solution_name,
            datasetGroupArn=dataset_group_arn,
            recipeArn=recipe_arn,
            eventType=event_type,
            performHPO=True
        )

        solution_arn = create_solution_response['solutionArn']
        logger.info(f"Product solution {campaign_solution_name} create initiated with Arn {solution_arn}")

        return None

    # Create product solution version if it doesn't exist
    response = personalize.list_solution_versions(solutionArn=solution_arn)
    if response['solutionVersions']:
        logger.info("Solution Version for "+campaign_solution_name+" already exists, not creating")
        solution_version_arn = response['solutionVersions'][0]['solutionVersionArn']
    else:
        logger.info('Creating SolutionVersion')
        create_solution_version_response = personalize.create_solution_version(
            solutionArn=solution_arn)
        solution_version_arn = create_solution_version_response['solutionVersionArn']

    # Make sure product recommendation solution version is active, otherwise force a re-poll
    describe_solution_version_response = personalize.describe_solution_version(
        solutionVersionArn=solution_version_arn
    )
    status = describe_solution_version_response["solutionVersion"]["status"]
    logger.info(f"SolutionVersion Status for {campaign_solution_name} is: {status}")
    if status != "ACTIVE":
        return None

    # Create related product campaign if it doesn't exist
    list_campaigns_response = personalize.list_campaigns(
        solutionArn=solution_arn
    )
    if list_campaigns_response['campaigns']:
        for campaign in list_campaigns_response['campaigns']:
            status = campaign['status']
            if status != 'ACTIVE':
                logger.info(f"Campaign {campaign['campaignArn']} is NOT active - status {status} - repoll later")
                return None

            logger.info('Campaign ' + campaign['campaignArn'] + ' is active.')
            campaign_arn = campaign['campaignArn']
            return campaign_arn
    else:
        logger.info('Creating campaign - will poll')
        personalize.create_campaign(
            name=campaign_solution_name,
            solutionVersionArn=solution_version_arn,
            minProvisionedTPS=1
        )
        return None


def delete_campaign_polling(dataset_group_arn, solution_arn, **kwargs):
    """
    For a particular solution Arn, remove the solution and all campaigns attached to it.
    This function is meant to be called repeatedly (polling) till it returns True.
    Args:
        dataset_group_arn: Where to delete the campaign+solution
        solution_arn: What solution to remove
        kwargs: Other arguments which are ignored. This is to allow training configs to be passed around.

    Returns:
        Tuple - 1st item:
            True if desired campaign has been deleted, or failed.
            False otherwise.
        2nd item:
            Campaign Arn if a campaign has been scheduled for deletion
            None otherwise
    """

    finished = True
    list_solutions_response = personalize.list_solutions(datasetGroupArn=dataset_group_arn)
    list_campaigns_response = personalize.list_campaigns(solutionArn=solution_arn)

    for campaign in list_campaigns_response['campaigns']:
        finished = False
        try:
            logger.info(f"We are signalling that we do not want campaign with Arn {campaign['campaignArn']}")
            personalize.delete_campaign(campaignArn=campaign['campaignArn'])

            # Delete the SSM parameter if we have deleted a campaign
            for ssm_param in campaign_type_to_ssm_param.values():
                try:
                    test_campaign_arn = ssm.get_parameter(Name=ssm_param)['Parameter']['Value']
                    if campaign['campaignArn'].strip() == test_campaign_arn.strip():
                        logger.info(f"As campaign with Arn {campaign['campaignArn']} was configured in SSM parameter"
                                    f" {ssm_param} but is to be deleted, we are removing it from SSM.")
                        response = ssm.put_parameter(
                            Name=ssm_param,
                            Description='Retail Demo Store Campaign Arn Parameter',
                            Value='NONE',
                            Type='String',
                            Overwrite=True
                        )
                except ssm.exceptions.ParameterNotFound:
                    logger.info(f"No campaign recorded at {ssm_param}")

        except personalize.exceptions.ResourceInUseException as ex:
            logger.info(f"Campaign with Arn {campaign['campaignArn']} is still alive - waiting for it to change status "
                        f"so it can disappear")

    if not finished:
        return False

    for solution in list_solutions_response['solutions']:
        if solution['solutionArn'] == solution_arn:
            finished = False
            try:
                logger.info(f"We are signalling that we do not want solution with Arn {solution_arn}")
                personalize.delete_solution(solutionArn=solution_arn)
            except personalize.exceptions.ResourceInUseException as ex:
                logger.info(f"Campaign with Arn {solution['solutionArn']} is still alive "
                            f"- waiting for it to change status so it can disappear")

    return finished


def create_filter(dataset_group_arn, arn_param, filter_name, filter_expression):
    """
    Creates Personalize Filter for e.g. excluding recommendations for recently purchased products or
    restricting products to certain sets of categories.
    It is possible to do this exclusion for each call to GetRecommendations but much easier to pass
    around the filter.
    If already made, returns without doing anything.
    Args:
        dataset_group_arn: Where to make the filter
        arn_param: Where to put the SSM parameter to store the Arn of the resulting filter
        filter_name: Usually ends up in the Arn
        filter_expression: See https://docs.aws.amazon.com/personalize/latest/dg/filter-expressions.html

    Returns:
        Nothing.
    """

    """"""
    logger.info(f"Making filter with name {filter_name}, SSM arn {arn_param} and expression {filter_expression}")

    try:
        response = personalize.create_filter(
                name=filter_name,
            datasetGroupArn = dataset_group_arn,
                filterExpression=filter_expression
        )

        filter_arn = response['filterArn']

        logger.info('Setting purchased product filter ARN as SSM parameter ' + arn_param)

        ssm.put_parameter(
            Name=arn_param,
            Description=f'Retail Demo Store Personalize Filter - {filter_name}',
            Value='{}'.format(filter_arn),
            Type='String',
            Overwrite=True
        )

    except personalize.exceptions.ResourceAlreadyExistsException:
        logger.info("Filter already exists - skipping creation")


def delete_datasets(dataset_group_arn):
    """Delete all datasets in a dataset group in a polling fashion and return the number still around."""
    logger.info('Deleting datasets for dataset group')
    dataset_count = 0
    dataset_paginator = personalize.get_paginator('list_datasets')

    for dataset_page in dataset_paginator.paginate(datasetGroupArn = dataset_group_arn):
        for dataset in dataset_page['datasets']:
            dataset_count += 1
            if dataset['status'] == 'ACTIVE':
                logger.info('Deleting dataset {}'.format(dataset['datasetArn']))
                try:
                    personalize.delete_dataset(datasetArn = dataset['datasetArn'])
                except personalize.exceptions.ResourceInUseException as ex:
                    logger.info('Cannot yet delete it.')

    return dataset_count == 0


def delete_dataset_group(dataset_group_arn):
    """Delete dataset group in a polling fashion and return the True if gone."""
    try:
        logger.info('Deleting dataset group')
        try:
            personalize.delete_dataset_group(datasetGroupArn = dataset_group_arn)
            return False
        except personalize.exceptions.ResourceInUseException as ex:
            logger.info('Cannot yet delete it.')
            return False
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'ResourceNotFoundException':
            logger.info("Dataset group does not exist")

    return True


def delete_event_trackers(dataset_group_arn):
    """Delete all event trackers in a dataset group in a polling fashion and return the number still around."""
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
    for event_tracker_page in event_trackers_paginator.paginate(datasetGroupArn=dataset_group_arn):
        for event_tracker in event_tracker_page['eventTrackers']:
            event_tracker_count += 1
            if event_tracker['status'] == 'ACTIVE':
                logger.info('Deleting event tracker {}'.format(event_tracker['eventTrackerArn']))
                try:
                    personalize.delete_event_tracker(eventTrackerArn=event_tracker['eventTrackerArn'])
                except personalize.exceptions.ResourceInUseException as ex:
                    logger.info('Could not yet delete it')

    return event_tracker_count == 0


def delete_filters(dataset_group_arn):
    """Delete all filters in a dataset group in a polling fashion and return the number still around."""
    filters_response = personalize.list_filters(datasetGroupArn = dataset_group_arn, maxResults = 100)

    for filter in filters_response['Filters']:
        logger.info('Deleting filter: ' + filter['filterArn'])
        try:
            personalize.delete_filter(filterArn = filter['filterArn'])
        except personalize.exceptions.ResourceInUseException as ex:
            logger.info('Could not yet delete it')

    return len(filters_response['Filters'])==0

def update():
    """
    According to the contents of the SSM variable retaildemostore-training-config build and delete
    dataset groups, datasets, solutions and campaigns to reach the desired state.

    The function runs off the training config which has the following JSON structure:
        - Dictionary with one key "steps" which represent sequential configurations to be achieved.
        - Its value is a list of dictionaries each representing a Personalize config to aspire to.
          Once the step is finished the system mover on to the next step.
        - Each step Personalize config dictionary has a set of keys as the name of dataset group
          to create and the value the config for that dataset group.
        - Each dataset group config consists of a single key: "campaigns" with its value a dictionary
          with key campaign type (there are 4 campaign types: user-item, item-item, reranking)
          and value campaign config for that campaign type.
        - The campaign config consists of a dictionary with 3 keys:
            - "desired_campaign_suffixes" - a list of numerical version numbers of solutions and campaigns to create.
              For example, if the campaign_type is "retaildemostore-related-products" and the desired version nums is
              [3], it will attempt to create a related products campaign with name retaildemostore-related-products-3
            - "desired_active_version_suffixes" - an int showing which of these version numbers should be activated in the UI
              This is achieved by putting the SSM parameter for this campaign into the right parameter so that it is
              picked up by the recommendations endpoint.
            - "minimum_available_campaigns" - if 0 then campaigns can get deleted even if it means there will be
              no active campaigns. If 1 then this campaign is preserved till there is another campaign of this type.

        See the poll_create function below for how the default training configuration is constrcuted.

        As another example, the following config requests a full teardown
        followed by creation of a dataset group with two campaigns:

            {
                "steps": [
                    {
                        "dataset_groups": null
                    },
                    {
                        "dataset_groups": {
                            "retaildemostore-MYDATASETGROUP": {
                                "campaigns": {
                                    "retaildemostore-related-products": {
                                        "desired_campaign_suffixes": [0],
                                        "desired_active_version_suffixes": 0
                                    },
                                    "retaildemostore-product-personalization": {
                                        "desired_campaign_suffixes": [0],
                                        "desired_active_version_suffixes": 0
                                    }
                                }
                            }
                        }
                    }
                ]
            }
    """

    # Already configured - grab that config - see it documented in the poll_create function below.
    train_configs = ssm.get_parameter(Name=training_config_param_name)
    train_configs = json.loads(train_configs['Parameter']['Value'])

    trainstep_config = train_configs['steps'][0]
    logger.info(f"Got train config: {json.dumps(trainstep_config, indent=2)}")

    try:
        train_state = ssm.get_parameter(Name=training_state_param_name)
        train_state = json.loads(train_state['Parameter']['Value'])
    except (ssm.exceptions.ParameterNotFound, json.JSONDecodeError) as e:
        train_state = {'dataset_groups': [], 'schema': []}
    logger.info(f"Current train state: {json.dumps(train_state, indent=2)}")

    # Find all dataset groups in region
    response = personalize.list_dataset_groups()
    datasetGroups = response['datasetGroups']
    dataset_group_name_to_arn = {datasetGroup['name']: datasetGroup['datasetGroupArn'] for datasetGroup in
                                 datasetGroups}

    # Find dataset group names I control
    all_dataset_group_names = train_state['dataset_groups']

    # group them into ones we want and ones we do not want
    desired_dataset_group_names = [] if trainstep_config['dataset_groups'] is None else list(trainstep_config['dataset_groups'].keys())
    undesired_dataset_group_names = [name for name in all_dataset_group_names if name not in desired_dataset_group_names]

    all_deleted = True
    all_created = True

    schemas = {}

    if len(desired_dataset_group_names) > 0:
        #  We want to create some dataset groups so we'll be needing the schema and the role
        role_arn = create_personalize_role(role_name)
        if not role_arn:
            logger.info('Waiting for IAM role to be consistent')
            return False

    for dataset_group_name in desired_dataset_group_names:

        all_created_dataset_group = True
        dataset_group_arn = dataset_group_name_to_arn.get(dataset_group_name, None)

        # Create dataset group if it doesn't exist and save the name in an SSM param
        if dataset_group_arn is None:

            # take ownership of this dataset group
            train_state['dataset_groups'] = list(set(train_state['dataset_groups']) | {dataset_group_name})
            response = ssm.put_parameter(
                Name=training_state_param_name,
                Description='Retail Demo Store Train State (controlled dataset groups)',
                Value=json.dumps(train_state),
                Type='String',
                Overwrite=True
            )
            logger.info(f'New train state: {json.dumps(train_state)}')

            logger.info(f'Generating a dataset group with unique name {dataset_group_name}')
            create_dataset_group_response = personalize.create_dataset_group(name=dataset_group_name)
            dataset_group_arn = create_dataset_group_response['datasetGroupArn']

            # take ownership of the dataset group's event schema
            train_state['schema'] = list(set(train_state['schema']) | {dataset_group_name+'-event-schema'})
            response = ssm.put_parameter(
                Name=training_state_param_name,
                Description='Retail Demo Store Train State (controlled dataset groups)',
                Value=json.dumps(train_state),
                Type='String',
                Overwrite=True
            )

        describe_dataset_group_response = personalize.describe_dataset_group(
            datasetGroupArn=dataset_group_arn
        )

        status = describe_dataset_group_response["datasetGroup"]["status"]
        logger.info("DatasetGroup: {}".format(status))

        if status == "CREATE FAILED":
            logger.error(f'DatasetGroup {dataset_group_name} '
                         f'create failed: {json.dumps(describe_dataset_group_response)}')
            return False  # Everything will hang on this step

        # Go away for another poll till dataset group active.
        if status != "ACTIVE":
            logger.info(f'DatasetGroup {dataset_group_name} not active yet')
            all_created = False
            continue

        datasets_config = trainstep_config['dataset_groups'][dataset_group_name]['datasets']

        dataset_arns = {}
        import_job_arns = {}

        for dataset_type, dataset_detail in datasets_config.items():

            dataset_filename = dataset_detail['filename']

            # Conditionally create schemas
            schemas[dataset_type] = create_schema(dataset_detail['schema']['avro'],
                                                  dataset_detail['schema']['name'])

            # take ownership of this schema (interactions, items or users)
            train_state['schema'] = list(set(train_state['schema']) | {dataset_detail['schema']['name']})
            response = ssm.put_parameter(
                Name=training_state_param_name,
                Description='Retail Demo Store Train State (controlled dataset groups)',
                Value=json.dumps(train_state),
                Type='String',
                Overwrite=True
            )

            dataset_name = dataset_group_name + '-' + dataset_type
            dataset_arns[dataset_type] = create_dataset(dataset_group_arn, dataset_name,
                                                        dataset_type, schemas[dataset_type])

            dataset_import_job_name = dataset_name+'-import'
            s3_filename = "s3://{}/{}".format(bucket, dataset_filename)
            import_job_arns[dataset_type] = create_import_job(dataset_import_job_name,
                                                             dataset_arns[dataset_type], account_id, region,
                                                             s3_filename, role_arn)

        # Make sure all import jobs are done/active before continuing
        for arn in import_job_arns.values():

            if not is_import_job_active(arn):
                logger.info(f"Import job {arn} is NOT active yet")
                all_created = False
                all_created_dataset_group = False
                continue

        if not all_created_dataset_group:
            continue

        # Create related product, product recommendation, and rerank solutions if they doesn't exist
        # Start by calculating what recipes, with what names, event types, and whether we want activated first.
        campaigns_config = trainstep_config['dataset_groups'][dataset_group_name]['campaigns']
        augmented_train_config = []
        for campaign_type, campaign_train_config in campaigns_config.items():

            for campaign_no in campaign_train_config['desired_campaign_suffixes']:

                config_for_campaign = dict(
                    recipe_arn=campaign_type_to_recipe_arn[campaign_type],
                    campaign_solution_name=campaign_type + '-' + str(campaign_no),
                    event_type=campaign_type_to_event_type[campaign_type],
                    activate_please=campaign_no == campaign_train_config['desired_active_version_suffixes'],
                    active_arn_param_name=campaign_type_to_ssm_param[campaign_type],
                    campaign_type=campaign_type)

                augmented_train_config += [config_for_campaign]

        # Train up any campaigns that may be missing and set their SSMs
        logger.info(f"Set up to train with augmented training config: {json.dumps(augmented_train_config, indent=4)}")
        for train_job in augmented_train_config:
            logger.info(f'Polling training job {train_job}')
            campaign_arn = create_campaign_polling(dataset_group_arn=dataset_group_arn,
                                                   **train_job)
            if campaign_arn is not None and train_job['activate_please']:
                logger.info(f"Setting campaignArn {campaign_arn} as system parameter"
                            f" for {train_job['active_arn_param_name']} which has finished")
                # Finally, set the campaign arn as the system parameter expected by services
                response = ssm.put_parameter(
                    Name=train_job['active_arn_param_name'],
                    Description='Retail Demo Store Campaign Arn Parameter',
                    Value='{}'.format(campaign_arn),
                    Type='String',
                    Overwrite=True
                )
            all_created_dataset_group = all_created_dataset_group and campaign_arn is not None
            all_created = all_created and all_created_dataset_group

        # Now we will go through the existing solutions and remove any we don't want
        list_solutions_response = personalize.list_solutions(datasetGroupArn=dataset_group_arn)
        all_desired_solution_names = [d['campaign_solution_name'] for d in augmented_train_config]

        # We go through the existing solutions and delete ones that are not in the list of desired solutions
        for solution in sorted(list_solutions_response['solutions'], key=lambda x:x['name']):
            if solution['name'] in all_desired_solution_names:
                pass  # We can keep this one because we have been configured to build it
            else:
                logger.info(f"Solution {solution['name']} with Arn {solution['solutionArn']} is unwanted. "
                            "We will try to remove it.")

                deleted_one = delete_campaign_polling(
                    dataset_group_arn=dataset_group_arn,
                    solution_arn=solution['solutionArn'])
                all_deleted = all_deleted and deleted_one

        # Create recent product purchase and category filter, if necessary
        # (or whatever filters have been configured)
        filters_config = trainstep_config['dataset_groups'][dataset_group_name]['filters']
        if filters_config is not None:
            for filter_config in filters_config:
                create_filter(dataset_group_arn=dataset_group_arn,
                              arn_param=filter_config['arn_param'],
                              filter_name=filter_config['filter_name'],
                              filter_expression=filter_config['filter_expression'])

        tracker_config = trainstep_config['dataset_groups'][dataset_group_name]['tracker']
        if tracker_config:
            list_event_trackers_response = personalize.list_event_trackers(datasetGroupArn=dataset_group_arn)
            if len(list_event_trackers_response['eventTrackers']) == 0 and all_created:

                # Either hasn't been created yet or isn't active yet.
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
                        # Trigger rebuild of Web UI service so event tracker gets picked up.
                        rebuild_webui_service(region, account_id)

                    return False  # Give event tracker a moment to get ready
                else:
                    event_tracker = list_event_trackers_response['eventTrackers'][0]
                    logger.info("Event Tracker: {}".format(event_tracker['status']))

                    if event_tracker['status'] == 'CREATE FAILED':
                        logger.error('Event tracker create failed: {}'.format(json.dumps(event_tracker)))
                        return False

    # Now go through dataset groups getting rid of any we do not need.
    for dataset_group_name in undesired_dataset_group_names:

        dataset_group_arn = dataset_group_name_to_arn.get(dataset_group_name, None)

        if dataset_group_arn is not None:

            all_deleted = False
            # Note that it may not pull down if there are campaigns and solutions attached to it.
            # So we can try to remove them
            list_solutions_response = personalize.list_solutions(datasetGroupArn=dataset_group_arn)
            for solution in list_solutions_response['solutions']:
                _ = delete_campaign_polling(
                        dataset_group_arn=dataset_group_arn,
                        solution_arn=solution['solutionArn'])

            if len(list_solutions_response['solutions'])>0:
                logger.info(f"We do not need this dataset group {dataset_group_arn} but it still has solutions.")
            else:
                logger.info(f"We do not need this dataset group {dataset_group_arn}. Let us take it down.")
                # Other than the dataset group, no deps on filters so delete them first.
                delete_filters(dataset_group_arn)
                if delete_event_trackers(dataset_group_arn):
                    logger.info('EventTrackers fully deleted')
                    if delete_datasets(dataset_group_arn):
                        logger.info('Datasets fully deleted')
                        if delete_dataset_group(dataset_group_arn):
                            logger.info('DatasetGroup fully deleted')

    if len(desired_dataset_group_names) == 0:
        all_deleted = all_deleted and delete_personalize_schemas(train_state['schema'])
        all_deleted = all_deleted and delete_personalize_role()

    if all_created and all_deleted:
        # No need for this lambda function to be called anymore so disable CW event rule that has been calling us.
        # If somethihng wants this functionality, they just enable the rule.
        # Alternatively, if we have been configured with multi-step config, move on to the next step.
        msg = ('Related product, Product recommendation, Personalized reranking, '
               'fully provisioned '
               'and unwanted campaigns removed.')
        logger.info(msg)
        if len(train_configs['steps'])>1:
            train_configs['steps'] = train_configs['steps'][1:]
            ssm.put_parameter(
                Name=training_config_param_name,
                Description='Retail Demo Store Training Config',
                Value=json.dumps(train_configs, indent=3),
                Type='String',
                Overwrite=True
            )
            logger.info(f" - Popping the training config that just succeded. "
                        f"New training config: {json.dumps(train_configs, indent=2)}")
            logger.info(msg)
            return False
        else:
            logger.info("Finished polling.")
            return True
    else:
        if all_created:
            msg = 'Still trying to clean up some things.'
        elif all_deleted:
            msg = "Still trying to provision something."
        else:
            msg = "Still trying to provision and delete things."
        logger.info(msg)
        return False


@cloudformation_helper.poll_create
def poll_create(event, context):
    """
    Called on creation by CloudFormation. Polled till creation is done.
    Sets up the default training configuration and calls update() which tries to pull everything in shape to match the
    training config. By default we train up one version of each of thge campaign types (user-item, item-item,
    reranking).
    How the config is generated can be examined below but there is more documentation in update()
    Args:
        event: We ignore this - we know what we want to build
        context: We ignore this

    Returns:
        True if polling is finished.
    """

    if not is_ssm_parameter_set(training_config_param_name):

        # Default training config - build one of each campaign in one dataset group and leave it at that
        campaigns_to_build_products = {}
        for campaign_type in all_campaign_types_products:
            campaigns_to_build_products[campaign_type] = {
                'desired_campaign_suffixes': [0],  # We want a single campaign with suffix -0 for each campaign type
                'desired_active_version_suffixes': 0,  # We want the campaign with suffix -0 to be activated in SSM
                'minimum_available_campaigns': 0}  # We want at least zero campaigns to be available at all times

        campaigns_to_build_offers = {}
        for campaign_type in all_campaign_types_offers:
            campaigns_to_build_offers[campaign_type] = {
                'desired_campaign_suffixes': [0],  # We want a single campaign with suffix -0 for each campaign type
                'desired_active_version_suffixes': 0,  # We want the campaign with suffix -0 to be activated in SSM
                'minimum_available_campaigns': 0}  # We want at least zero campaigns to be available at all times

        dataset_group_name_unique_products = dataset_group_name_root_products + str(uuid.uuid4())[:8]
        dataset_group_name_unique_offers = dataset_group_name_root_offers + str(uuid.uuid4())[:8]

        dataset_groups = {}
        dataset_groups[dataset_group_name_unique_products]= {
                            'datasets': dataset_type_to_detail_products,
                            'campaigns': campaigns_to_build_products,
                            'filters': filters_config,
                            'tracker': True
                        }

        if do_deploy_offers_campaign:
            dataset_groups[dataset_group_name_unique_offers] = {
                            'datasets': dataset_type_to_detail_offers,
                            'campaigns': campaigns_to_build_offers,
                            'filters': {},
                            'tracker': False
                        }

        train_configs = {
            "steps": [
                {
                    "dataset_groups": dataset_groups
                }
            ]
        }

        ssm.put_parameter(
            Name=training_config_param_name,
            Description='Retail Demo Store Training Config',
            Value=json.dumps(train_configs, indent=3),
            Type='String',
            Overwrite=True
        )

    # We enable the rule to carry on working but return to CloudFormation because CloudFormation does time out
    # while waiting, otherwise. If it had not we could have done return update() here.
    enable_event_rule(lambda_event_rule_name)
    return True


@cloudformation_helper.poll_delete
def poll_delete(event, context):
    """
     Called on deletion by CloudFormation.
     Sets up the training configuration to pull down everything and calls update()
     How the config is generated for tear-down can be examined below but there is more documentation in update()
     Args:
         event: We ignore this - we know what we want to build
         context: We ignore this

     Returns:
         True if polling is finished.
     """

    # Empty the training config of dataset groups to pull it all down.
    train_configs = {"steps": [{"dataset_groups": None}]}
    ssm.put_parameter(
        Name=training_config_param_name,
        Description='Retail Demo Store Training Config',
        Value=json.dumps(train_configs, indent=3),
        Type='String',
        Overwrite=True
    )
    done = update()
    return done


@cloudformation_helper.poll_update
def poll_update(event, _):
    done = update()
    return done


def lambda_handler(event, context):
    """According to the contents of the SSM variable retaildemostore-training-config build and delete
    dataset groups, datasets, solutions and campaigns to reach the desired state."""
    logger.debug('## ENVIRONMENT VARIABLES')
    logger.debug(os.environ)
    logger.debug('## EVENT')
    logger.debug(event)

    ## Inspect the event - if it is coming from EventBridge then it is polling after reset
    ## If it is coming from CloudFormation then use the helper to create or tear down
    if "source" in event and event["source"] == "aws.events":
        done = update()  # Will pick up desired behaviour from training_config
        if done:
            disable_event_rule(lambda_event_rule_name)
            return {
                'statusCode': 200,
                'body': json.dumps("Event rule disabled")
            }
        else:
            return {
                'statusCode': 200,
                'body': json.dumps("Polled Personalize Create Update")
            }

    else:
        # We have a Cloud Formation Event - the event contains info about whether it wants to update, create or delete
        cloudformation_helper(event, context)
