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
import urllib
import boto3
import logging
import os
import requests
import time
import yaml
from typing import Dict, List, Tuple
from crhelper import CfnResource
from botocore.exceptions import ClientError
from delete_dataset_groups import delete_dataset_groups, ResourcePending

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ssm = boto3.client('ssm')
personalize = boto3.client('personalize')
cw_events = boto3.client('events')
codepipeline = boto3.client('codepipeline')
servicediscovery = boto3.client('servicediscovery')
s3 = boto3.client('s3')
sts = boto3.client('sts')

cloudformation_helper = CfnResource()

# Where our data is for training
bucket = os.environ['bucket']
csv_path = os.environ.get('csv_path', '')

# Default value : https://code.retaildemostore.retail.aws.dev/
base_url = os.environ['base_url']

items_key = csv_path + "items.csv"
users_filename = csv_path + "users.csv"
interactions_key = csv_path + "interactions.csv"
offer_interactions_key = csv_path + "offer_interactions.csv"

session = boto3.session.Session()
region = session.region_name
account_id = sts.get_caller_identity().get('Account')

dataset_group_name_products = 'retaildemostore-products'
dataset_group_name_offers = 'retaildemostore-offers'

role_arn = os.environ['PersonalizeRoleArn']
create_personalize_resources = os.environ.get('PreCreatePersonalizeResources', 'no').strip().lower() in ['yes', 'true', '1']
create_deploy_offers_campaign = os.environ['DeployPersonalizedOffersCampaign'].strip().lower() in ['yes', 'true', '1']

datasetgroup_name_param = 'retaildemostore-personalize-datasetgroup-name'

# Info on CloudWatch event rule used to repeatedely call this function.
lambda_event_rule_name = os.environ['lambda_event_rule_name']

# Currently supported regions for Personalize Content Generator: https://docs.aws.amazon.com/personalize/latest/dg/themed-batch-recommendations.html#themes-regions
CONTENT_GENERATOR_REGIONS = [ "us-east-1", "us-west-2", "ap-northeast-1" ]

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
            "name": "PRICE",
            "type": "float"
        },
        {
            "name": "CATEGORY_L1",
            "type": "string",
            "categorical": True
        },
        {
            "name": "CATEGORY_L2",
            "type": "string",
            "categorical": True
        },
        {
            "name": "PRODUCT_NAME",
            "type": "string"
        },
        {
            "name": "PRODUCT_DESCRIPTION",
            "type": "string",
            "textual": True
        },
        {
            "name": "GENDER",
            "type": "string",
            "categorical": True
        },
        {
            "name": "PROMOTED",
            "type": "string"
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

dataset_group_confs = [
    {
        'name': dataset_group_name_products,
        'domain': 'ECOMMERCE',
        'datasets': [
            {
                'type': 'INTERACTIONS',
                'name': 'retaildemostore-products-interactions',
                'schema': interactions_schema_products,
                's3Key': interactions_key
            },
            {
                'type': 'ITEMS',
                'name': 'retaildemostore-products-items',
                'schema': items_schema,
                's3Key': items_key
            },
            {
                'type': 'USERS',
                'name': 'retaildemostore-products-users',
                'schema': users_schema,
                's3Key': users_filename
            }
        ],
        'eventTracker': {
            'name': 'retaildemostore-event-tracker',
            'param': '/retaildemostore/personalize/event-tracker-id',
            'paramDescription': 'Retail Demo Store Personalize Event Tracker ID Parameter'
        },
        'filters': [
            {
                'name': 'retaildemostore-filter-exclude-purchased-products',
                'expression': 'EXCLUDE ItemID WHERE INTERACTIONS.event_type IN ("Purchase")',
                'param': '/retaildemostore/personalize/filters/filter-purchased-arn',
                'paramDescription': 'Retail Demo Store Filter Purchased Product Arn Parameter'
            },
            {
                'name': 'retaildemostore-filter-cstore-products',
                'expression': 'EXCLUDE ItemID WHERE ITEMS.CATEGORY_L1 NOT IN ("cold dispensed", "hot dispensed", "salty snacks", "food service")',
                'param': '/retaildemostore/personalize/filters/filter-cstore-arn',
                'paramDescription': 'Retail Demo Store Filter C-Store Products Arn Parameter'
            },
            {
                'name': 'retaildemostore-filter-exclude-purchased-cstore-products',
                'expression': 'EXCLUDE ItemID WHERE INTERACTIONS.event_type IN ("Purchase") | EXCLUDE ItemID WHERE ITEMS.CATEGORY_L1 IN ("cold dispensed", "hot dispensed", "salty snacks", "food service")',
                'param': '/retaildemostore/personalize/filters/filter-purchased-and-cstore-arn',
                'paramDescription': 'Retail Demo Store Filter Purchased and C-Store Products Arn Parameter'
            },
            {
                'name': 'retaildemostore-filter-same-categories',
                'expression': 'INCLUDE ItemID WHERE ITEMS.CATEGORY_L1 IN CurrentItem.CATEGORY_L1',
                'param': '/retaildemostore/personalize/filters/filter-same-categories-arn',
                'paramDescription': 'Retail Demo Store Filter to Include Same Categories Arn Parameter'
            },
            {
                'name': 'retaildemostore-filter-exclude-purchased-include-categories',
                'expression': 'EXCLUDE ItemID WHERE INTERACTIONS.event_type IN ("Purchase") | INCLUDE ItemID WHERE ITEMS.CATEGORY_L1 IN CurrentItem.CATEGORY_L1',
                'param': '/retaildemostore/personalize/filters/filter-exclude-purchased-include-categories-arn',
                'paramDescription': 'Retail Demo Store Filter to Exclude Purchased and Include Same Categories Arn Parameter'
            },
            {
                'name': 'retaildemostore-filter-promoted-items',
                'expression': 'EXCLUDE ItemID WHERE INTERACTIONS.event_type IN ("Purchase") | INCLUDE ItemID WHERE ITEMS.PROMOTED IN ("Y")',
                'param': '/retaildemostore/personalize/filters/promoted-items-filter-arn',
                'paramDescription': 'Retail Demo Store Promotional Filter to Include Promoted Items Arn Parameter'
            },
            {
                'name': 'retaildemostore-filter-promoted-items-no-cstore',
                'expression': 'EXCLUDE ItemID WHERE INTERACTIONS.event_type IN ("Purchase") | INCLUDE ItemID WHERE ITEMS.PROMOTED IN ("Y") AND ITEMS.CATEGORY_L1 NOT IN ("cold dispensed", "hot dispensed", "salty snacks", "food service")',
                'param': '/retaildemostore/personalize/filters/promoted-items-no-cstore-filter-arn',
                'paramDescription': 'Retail Demo Store Promotional Filter to Include Promoted Non-CStore Items Arn Parameter'
            }
        ],
        'recommenders': [
            {
                'name': 'retaildemostore-recommended-for-you',
                'recipe': 'arn:aws:personalize:::recipe/aws-ecomm-recommended-for-you',
                'recommenderConfig': {
                    'trainingDataConfig': {
                        'excludedDatasetColumns': {
                            'ITEMS': [ 'PRODUCT_NAME', 'PROMOTED' ]
                        }
                    }
                },
                'param': '/retaildemostore/personalize/recommended-for-you-arn',
                'paramDescription': 'Retail Demo Store Recommended For You Campaign/Recommender Arn Parameter'
            },
            {
                'name': 'retaildemostore-popular-items',
                'recipe': 'arn:aws:personalize:::recipe/aws-ecomm-popular-items-by-views',
                'recommenderConfig': {
                    'trainingDataConfig': {
                        'excludedDatasetColumns': {
                            'ITEMS': [ 'PRODUCT_NAME', 'PROMOTED' ]
                        }
                    }
                },
                'param': '/retaildemostore/personalize/popular-items-arn',
                'paramDescription': 'Retail Demo Store Popular Items Campaign/Recommender Arn Parameter'
            }
        ],
        'solutions': [
            {
                'name': 'retaildemostore-related-items',
                'recipe': 'arn:aws:personalize:::recipe/aws-similar-items',
                'eventType': 'View',
                'solutionConfig': {
                    'trainingDataConfig': {
                        'excludedDatasetColumns': {
                            'ITEMS': [ 'PRODUCT_NAME', 'PROMOTED' ]
                        }
                    }
                },
                'campaign': {
                    'name': 'retaildemostore-related-items',
                    'param': '/retaildemostore/personalize/related-items-arn',
                    'paramDescription': 'Retail Demo Store Related Items Campaign/Recommender Arn Parameter'
                },
                'generateFeaturedProductThemes': True
            },
            {
                'name': 'retaildemostore-personalized-ranking',
                'recipe': 'arn:aws:personalize:::recipe/aws-personalized-ranking',
                'eventType': 'View',
                'solutionConfig': {
                    'trainingDataConfig': {
                        'excludedDatasetColumns': {
                            'ITEMS': [ 'PRODUCT_NAME', 'PROMOTED' ]
                        }
                    }
                },
                'campaign': {
                    'name': 'retaildemostore-personalized-ranking',
                    'param': '/retaildemostore/personalize/personalized-ranking-arn',
                    'paramDescription': 'Retail Demo Store Personalized Ranking Campaign/Recommender Arn Parameter'
                }
            },
            {
                'name': 'retaildemostore-item-attribute-affinity',
                'recipe': 'arn:aws:personalize:::recipe/aws-item-attribute-affinity',
                'solutionConfig': {
                    'trainingDataConfig': {
                        'excludedDatasetColumns': {
                            'ITEMS': [ 'PRODUCT_NAME', 'PROMOTED' ]
                        }
                    }
                }
            }
        ]
    }
]

if create_deploy_offers_campaign:
    dataset_group_confs.append({
        'name': dataset_group_name_offers,
        'datasets': [
            {
                'type': 'INTERACTIONS',
                'name': 'retaildemostore-offers-interactions',
                'schema': interactions_schema_offers,
                's3Key': offer_interactions_key
            }
        ],
        'solutions': [
            {
                'name': 'retaildemostore-personalized-offers',
                'recipe': 'arn:aws:personalize:::recipe/aws-user-personalization',
                'eventType': 'OfferConverted',
                'campaign': {
                    'name': 'retaildemostore-personalized-offers',
                    'param': '/retaildemostore/personalize/personalized-offers-arn',
                    'paramDescription': 'Retail Demo Store Personalized Offers Campaign/Recommender Arn Parameter'
                }
            }
        ]
    })

def s3_key_exists(bucket, prefix) -> bool:
    response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
    return 'Contents' in response

def stage_s3_file(bucket, key):
    if not s3_key_exists(bucket, key):
        source_url = base_url + key
        logger.info("Staged file s3://%s/%s does not exist; downloading from %s and staging in bucket", bucket, key, source_url)
        # Download file from URL
        temp_file = "/tmp/" + key
        os.makedirs(os.path.dirname(temp_file), exist_ok=True)
        local_filename, _ = urllib.request.urlretrieve(source_url, temp_file)
        # Upload to bucket
        s3.upload_file(local_filename, bucket, key)

def create_schema(dataset_group_conf: Dict, dataset_conf: Dict) -> Tuple[str, bool]:
    """ Conditionally creates a personalize schema if it does not already exist """
    schema_exists=False
    paginator = personalize.get_paginator('list_schemas')
    for paginate_result in paginator.paginate():
        for schema in paginate_result['schemas']:
            if schema['name'] == dataset_conf['name']:
                logger.info("Schema %s already exists, verifying that schema definition matches", dataset_conf['name'])

                # Since it's possible for a schema with the same name to exist from a prior deployment that wasn't
                # cleaned up properly, let's check that the schema definition matches what we want to create.
                response = personalize.describe_schema(schemaArn = schema["schemaArn"])
                schema_def = json.loads(response["schema"]["schema"])

                if dataset_conf['schema'] != schema_def:
                    logger.warning("Definition for existing schema does not match target schema; attempting to delete existing schema")
                    personalize.delete_schema(schemaArn = schema["schemaArn"])
                else:
                    logger.info("Schema %s definition matches expected definition; using existing definition", dataset_conf['name'])
                    schema_exists=True
                    dataset_conf['schemaArn'] = schema['schemaArn']
                break

        if schema_exists:
            break

    if not schema_exists:
        logger.info('Creating schema %s for domain %s', dataset_conf['name'], dataset_group_conf.get('domain'))

        params = {
            'name': dataset_conf['name'],
            'schema': json.dumps(dataset_conf['schema'])
        }
        if dataset_group_conf.get('domain'):
            params['domain'] = dataset_group_conf['domain']

        create_schema_response = personalize.create_schema(**params)

        dataset_conf['schemaArn'] = create_schema_response['schemaArn']

    return dataset_conf['schemaArn'], not schema_exists

def create_recommender(dataset_group_arn: str, recommender_conf: Dict) -> Tuple[str, bool]:
    recommender_exists = False
    paginator = personalize.get_paginator('list_recommenders')
    for paginate_result in paginator.paginate(datasetGroupArn=dataset_group_arn):
        for recommender in paginate_result['recommenders']:
            if recommender['name'] == recommender_conf['name']:
                logger.info('Found recommender %s with status of %s', recommender['recommenderArn'], recommender['status'])
                recommender_exists = True
                recommender_conf['arn'] = recommender['recommenderArn']
                recommender_conf['status'] = recommender['status']
                break

    if not recommender_exists:
        logger.info('Creating recommender %s', recommender_conf['name'])

        params = {
            'datasetGroupArn': dataset_group_arn,
            'name': recommender_conf['name'],
            'recipeArn': recommender_conf['recipe']
        }

        if recommender_conf.get('recommenderConfig'):
            params['recommenderConfig'] = recommender_conf['recommenderConfig']

        response = personalize.create_recommender(**params)

        recommender_conf['arn'] = response['recommenderArn']

    return recommender_conf['arn'], not recommender_exists

def create_filter(dataset_group_arn: str, filter_conf: Dict) -> Tuple[str, bool]:
    filter_exists = False
    paginator = personalize.get_paginator('list_filters')
    for paginate_result in paginator.paginate(datasetGroupArn=dataset_group_arn):
        for filter in paginate_result['Filters']:
            if filter['name'] == filter_conf['name']:
                logger.info('Found filter %s with status of %s', filter['filterArn'], filter['status'])
                filter_exists = True
                filter_conf['arn'] = filter['filterArn']
                filter_conf['status'] = filter['status']
                break

    if not filter_exists:
        logger.info('Creating filter %s', filter_conf['name'])
        response = personalize.create_filter(
            datasetGroupArn = dataset_group_arn,
            name = filter_conf['name'],
            filterExpression = filter_conf['expression']
        )

        filter_conf['arn'] = response['filterArn']

    return filter_conf['arn'], not filter_exists

def create_solution_version(dataset_group_arn: str, solution_conf: Dict) -> Tuple[str, bool]:
    solution_exists = False
    paginator = personalize.get_paginator('list_solutions')
    for paginate_result in paginator.paginate(datasetGroupArn=dataset_group_arn):
        for solution in paginate_result['solutions']:
            if solution['name'] == solution_conf['name']:
                logger.info('Found solution %s with status of %s', solution['solutionArn'], solution['status'])
                solution_exists = True
                solution_conf['arn'] = solution['solutionArn']
                solution_conf['status'] = solution['status']
                break

    if not solution_exists:
        logger.info('Solution %s not found; creating', solution_conf['name'])
        params = {
            'datasetGroupArn': dataset_group_arn,
            'name': solution_conf['name'],
            'recipeArn': solution_conf['recipe']
        }

        if solution_conf.get('eventType'):
            params['eventType'] = solution_conf['eventType']

        if solution_conf.get('solutionConfig'):
            params['solutionConfig'] = solution_conf['solutionConfig']

        response = personalize.create_solution(**params)
        solution_conf['arn'] = response['solutionArn']
        time.sleep(5)

        logger.info('Creating solution version for %s', solution_conf['arn'])
        response = personalize.create_solution_version(
            solutionArn = solution_conf['arn'],
            trainingMode = 'FULL'
        )
        solution_conf['solutionVersionArn'] = response['solutionVersionArn']
    else:
        # Load solution versions into dictionary keyed by status.
        solution_versions_by_status = {}
        paginator = personalize.get_paginator('list_solution_versions')
        for paginate_result in paginator.paginate(solutionArn=solution_conf['arn']):
            for solution_version in paginate_result['solutionVersions']:
                svs = solution_versions_by_status.setdefault(solution_version['status'], [])
                svs.append(solution_version)

        if len(solution_versions_by_status) == 0:
            logger.info('Creating solution version for %s', solution_conf['arn'])
            response = personalize.create_solution_version(
                solutionArn = solution_conf['arn'],
                trainingMode = 'FULL'
            )
            solution_conf['solutionVersionArn'] = response['solutionVersionArn']
        else:
            # Find first solution version matching the status in the following order.
            statuses = [ 'ACTIVE', 'CREATE PENDING', 'CREATE IN_PROGRESS', 'CREATE FAILED' ]
            for status in statuses:
                if status in solution_versions_by_status and len(solution_versions_by_status.get(status)) > 0:
                    solution_version = solution_versions_by_status[status][0]
                    logger.info('Using %s as solutionVersionArn with status of %s for solution %s', solution_version['solutionVersionArn'], solution_version['status'], solution_conf['arn'])
                    solution_conf['solutionVersionArn'] = solution_version['solutionVersionArn']
                    solution_conf['solutionVersionStatus'] = solution_version['status']
                    break

    return solution_conf['solutionVersionArn'], not solution_exists

def create_campaign(solution_conf: Dict, campaign_conf: Dict) -> Tuple[str, bool]:
    campaign_exists = False
    paginator = personalize.get_paginator('list_campaigns')
    for paginate_result in paginator.paginate(solutionArn=solution_conf['arn']):
        for campaign in paginate_result['campaigns']:
            if campaign['name'] == campaign_conf['name']:
                logger.info('Campaign %s found with status of %s', campaign['campaignArn'], campaign['status'])
                campaign_exists = True
                campaign_conf['arn'] = campaign['campaignArn']
                campaign_conf['status'] = campaign['status']
                break

    if not campaign_exists:
        logger.info('Campaign %s not found; creating', campaign_conf['name'])
        response = personalize.create_campaign(
            name = campaign_conf['name'],
            solutionVersionArn = solution_conf['solutionVersionArn']
        )

        campaign_conf['arn'] = response['campaignArn']

    return campaign_conf['arn'], not campaign_exists

def create_event_tracker(dataset_group_arn: str, event_tracker_conf: Dict) -> Tuple[str, bool]:
    tracker_exists = False
    paginator = personalize.get_paginator('list_event_trackers')
    for paginate_result in paginator.paginate(datasetGroupArn=dataset_group_arn):
        for tracker in paginate_result['eventTrackers']:
            if tracker['name'] == event_tracker_conf['name']:
                logger.info('Event tracker %s found with status of %s', tracker['eventTrackerArn'], tracker['status'])
                tracker_exists = True
                event_tracker_conf['arn'] = tracker['eventTrackerArn']
                event_tracker_conf['status'] = tracker['status']
                break

    if not tracker_exists:
        logger.info('Event tracker %s not found; creating', event_tracker_conf['name'])

        response = personalize.create_event_tracker(
            name = event_tracker_conf['name'],
            datasetGroupArn = dataset_group_arn
        )

        event_tracker_conf['arn'] = response['eventTrackerArn']
        event_tracker_conf['trackingId'] = response['trackingId']

        # Go ahead and set SSM param here since the trackingId is conveniently available
        if event_tracker_conf.get('param'):
            logger.info('Setting SSM parameter %s to trackingId %s', event_tracker_conf['param'], event_tracker_conf['trackingId'])
            ssm.put_parameter(
                Name=event_tracker_conf['param'],
                Description=event_tracker_conf['paramDescription'],
                Value='{}'.format(event_tracker_conf['trackingId']),
                Type='String',
                Overwrite=True
            )

    return event_tracker_conf['arn'], not tracker_exists

def create_dataset(dataset_group_arn: str, dataset_conf: Dict) -> Tuple[str, bool]:
    """ Conditionally creates dataset if it doesn't already exist """
    response = personalize.list_datasets(datasetGroupArn = dataset_group_arn)
    datasets = response['datasets']
    dataset_exists = False
    for dataset in datasets:
        if dataset['name'] == dataset_conf['name']:
            logger.info("Dataset %s already exists, not creating", dataset_conf['name'])
            dataset_exists=True
            dataset_conf['arn'] = dataset['datasetArn']
            dataset_conf['status'] = dataset['status']
            break

    if not dataset_exists:
        logger.info('Dataset %s does NOT exist; creating', dataset_conf['name'])
        create_dataset_response = personalize.create_dataset(
            datasetType = dataset_conf['type'],
            datasetGroupArn = dataset_group_arn,
            schemaArn = dataset_conf['schemaArn'],
            name=dataset_conf['name']
        )
        dataset_conf['arn'] = create_dataset_response['datasetArn']

    return dataset_conf['arn'], not dataset_exists

def create_import_job(dataset_conf: Dict) -> Tuple[str, bool]:
    import_job_exists=False

    job_name = dataset_conf['name']+'-import'
    data_location = "s3://{}/{}".format(bucket, dataset_conf['s3Key'])

    paginator = personalize.get_paginator('list_dataset_import_jobs')
    for paginate_result in paginator.paginate(datasetArn = dataset_conf['arn']):
        for job in paginate_result['datasetImportJobs']:
            if job['jobName'] == job_name:
                logger.info("Dataset import job %s already exists with status %s, not creating", job_name, job.get('status'))
                import_job_exists = True
                dataset_conf['importJobArn'] = job['datasetImportJobArn']
                dataset_conf['importJobStatus'] = job.get('status')
                break

        if import_job_exists:
            break

    if not import_job_exists:
        logger.info('Creating dataset import job %s', job_name)

        stage_s3_file(bucket, dataset_conf['s3Key'])

        response = personalize.create_dataset_import_job(
            jobName = job_name,
            datasetArn = dataset_conf['arn'],
            dataSource = {
                "dataLocation": data_location
            },
            roleArn = role_arn
        )
        dataset_conf['importJobArn'] = response['datasetImportJobArn']

    return dataset_conf['importJobArn'], not import_job_exists

def get_featured_product_ids() -> List[str]:
    logger.info("Downloading products.yaml to extract featured products")
    filename_products, _ = urllib.request.urlretrieve(base_url + 'data/products.yaml', '/tmp/products.yaml')

    with open(filename_products) as file:
        logger.info('Loading products.yaml...')
        products_list = yaml.safe_load(file)

        item_ids = []

        for product in products_list:
            if product.get("featured", False):
                item_ids.append(product["id"])

        return item_ids

def create_theme_generation_job(solution_conf: Dict, include_category_filter_arn: str) -> Tuple[str, bool]:
    theme_job_exists = False

    similar_items_solution_version_arn = solution_conf["solutionVersionArn"]

    solution_version_name = similar_items_solution_version_arn.split('/')[-1]
    # Create job name that incudes the SV name so avoid name colisions with old batch inference jobs
    job_name = f"retaildemostore-related-items-theme-job-{solution_version_name}"

    paginator = personalize.get_paginator('list_batch_inference_jobs')
    for paginate_result in paginator.paginate(solutionVersionArn = similar_items_solution_version_arn):
        for job in paginate_result['batchInferenceJobs']:
            if job['jobName'] == job_name:
                logger.info("Content generator batch inference theme job %s already exists with status %s, not creating", job_name, job.get('status'))
                theme_job_exists = True
                solution_conf['themeJobArn'] = job['batchInferenceJobArn']
                solution_conf['themeJobStatus'] = job.get('status')
                solution_conf["themeJobCreationDateTime"] = job["creationDateTime"]
                break

        if theme_job_exists:
            break

    if not theme_job_exists:
        logger.info('Creating content generator batch inference theme job %s', job_name)

        item_ids = get_featured_product_ids()

        logger.info("Building content generator batch inference input file")
        json_input_filename = "related_items_json_input.json"
        with open("/tmp/" + json_input_filename, 'w') as json_input:
            for id in item_ids:
                json_input.write(f'{{"itemId": "{id}"}}\n')

        s3.upload_file(f"/tmp/{json_input_filename}", bucket, json_input_filename)

        s3_input_path = f"s3://{bucket}/{json_input_filename}"
        s3_output_path = f"s3://{bucket}/related-items/similar-items/"

        response = personalize.create_batch_inference_job(
            solutionVersionArn = similar_items_solution_version_arn,
            jobName = job_name,
            roleArn = role_arn,
            filterArn = include_category_filter_arn,
            batchInferenceJobMode = "THEME_GENERATION",
            themeGenerationConfig = {
                "fieldsForThemeGeneration": {
                    "itemName": "PRODUCT_NAME"
                }
            },
            jobInput = {"s3DataSource": {"path": s3_input_path}},
            jobOutput = {"s3DataDestination":{"path": s3_output_path}},
            numResults = 15
        )

        solution_conf['themeJobArn'] = response['batchInferenceJobArn']

    return solution_conf['themeJobArn'], not theme_job_exists

def download_batch_inference_output(solution_conf):
    job_start_time = solution_conf["themeJobCreationDateTime"]

    response = s3.list_objects_v2(
        Bucket=bucket,
        Prefix="related-items/similar-items/",
    )

    output_key_name = None

    for obj in response["Contents"]:
        if obj["LastModified"] > job_start_time and obj["Key"].endswith(".out"):
            output_key_name = obj["Key"]
            break

    assert output_key_name is not None, "Unable to locate the job output file in the output folder"

    logger.info("Downloading output file %s from %s", output_key_name, bucket)

    out_file = "/tmp/related_items_json_input.json.out"
    s3.download_file(bucket, output_key_name, out_file)

    return out_file

def update_products_with_themes(output_file):
    # We will limit related items to those with a score >= 0.1
    score_threshold = 0.1

    response = servicediscovery.discover_instances(
        NamespaceName='retaildemostore.local',
        ServiceName='products',
        MaxResults=1,
        HealthStatus='HEALTHY'
    )

    assert len(response['Instances']) > 0, 'Products service instance not found; check ECS to ensure it launched cleanly'

    products_service_instance = response['Instances'][0]['Attributes']['AWS_INSTANCE_IPV4']

    with open(output_file) as themes_file:
        # Read all lines from the segmentation output file.
        themes_lines = themes_file.readlines()

        for idx, theme_line in enumerate(themes_lines):
            theme_results = json.loads(theme_line)
            item_id = theme_results["input"]["itemId"]
            if "output" not in theme_results:
                if "error" in theme_results:
                    logger.error('Error generating similar items and theme for item %s: %s', item_id, theme_results["error"])
                else:
                    logger.error('Unknown error generating similar items and theme for item %s', item_id)

                continue

            similar_items = theme_results["output"]["recommendedItems"]
            theme = theme_results["output"]["theme"]
            theme_scores = theme_results["output"]["itemsThemeRelevanceScores"]

            final_items = []
            for idx_item, similar_item_id in enumerate(similar_items):
                score = theme_scores[idx_item]
                if score >= score_threshold:
                    final_items.append(similar_item_id)

            response = requests.get(f"http://{products_service_instance}/products/id/{item_id}")
            product = response.json()

            if len(final_items) >= 3:
                product["related_items_theme"] = theme.rstrip(".")
                product["related_items"] = final_items
            else:
                logger.warning(f"Not enough items with score >= {score_threshold} for item {item_id}; clearing related items fields for product")
                product.pop("related_items_theme", None)
                product.pop("related_items", None)

            logger.info(f"Updating related items for product {item_id}")
            headers = {"Content-Type": "application/json"}
            response = requests.put(f"http://{products_service_instance}/products/id/{item_id}", json=product, headers=headers)
            if not response.ok:
                logger.error(f"status_code={response.status_code}")

def is_ssm_parameter_set(parameter_name: str) -> bool:
    try:
        response = ssm.get_parameter(Name=parameter_name)
        return response['Parameter']['Value'] != 'NONE'
    except ssm.exceptions.ParameterNotFound:
        return False

def enable_event_rule(rule_name: str):
    try:
        logger.info('Enabling event rule %s', rule_name)
        cw_events.enable_rule(Name=rule_name)

    except cw_events.exceptions.ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'ResourceNotFoundException':
            logger.error('CloudWatch event rule to enable not found')
            raise
        else:
            logger.error(e)
            raise

def disable_event_rule(rule_name: str):
    """
    Disables the CloudWatch event rule used to trigger this lambda function on a recurring schedule.
    Can be preferrable to deleting the rule because it is then easy to re-instate exactly the same rule by
    simply enabling it.
    Args:
        rule_name (str): Rule to disable
    """
    try:
        logger.info('Disabling event rule %s', rule_name)
        cw_events.disable_rule(Name=rule_name)

    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'ResourceNotFoundException':
            logger.warning('CloudWatch event rule to disable not found')
        else:
            logger.error(e)

def create_dataset_group(dataset_group_conf: Dict) -> Tuple[str, bool]:
    dsg_exists = False
    paginator = personalize.get_paginator('list_dataset_groups')
    for paginate_result in paginator.paginate():
        for dsg in paginate_result['datasetGroups']:
            if dsg['name'] == dataset_group_conf['name']:
                logger.info("Dataset group %s already exists, not creating", dataset_group_conf['name'])
                dsg_exists = True
                dataset_group_conf['arn'] = dsg['datasetGroupArn']
                break

        if dsg_exists:
            break

    if not dsg_exists:
        params = {
            'name': dataset_group_conf['name']
        }
        if dataset_group_conf.get('domain'):
            params['domain'] = dataset_group_conf['domain']

        response = personalize.create_dataset_group(**params)
        dataset_group_conf['arn'] = response['datasetGroupArn']

    return dataset_group_conf['arn'], not dsg_exists

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

def update() -> bool:
    done = True
    for dataset_group_conf in dataset_group_confs:
        # Create schemas for DSG
        for dataset_conf in dataset_group_conf['datasets']:
            create_schema(dataset_group_conf, dataset_conf)

        # Create DSG
        _,dsg_created = create_dataset_group(dataset_group_conf)
        if dsg_created:
            done = False
            continue

        # Create datasets
        all_ds_active = True
        for dataset_conf in dataset_group_conf['datasets']:
            _,ds_created = create_dataset(dataset_group_conf['arn'], dataset_conf)
            if ds_created or dataset_conf.get('status') != 'ACTIVE':
                all_ds_active = False

        if not all_ds_active:
            logger.info('Not all datasets active; wait for callback')
            done = False
            continue

        # Create import jobs for datasets
        all_imports_active = True
        for dataset_conf in dataset_group_conf['datasets']:
            _,import_created = create_import_job(dataset_conf)
            if import_created or dataset_conf['importJobStatus'] != 'ACTIVE':
                all_imports_active = False

        if not all_imports_active:
            logger.info('At least one dataset import job created or not yet active; wait for callback')
            done = False
            continue

        # Create recommenders
        all_recs_active = True
        for recommender_conf in dataset_group_conf.get('recommenders', []):
            _,rec_created = create_recommender(dataset_group_conf['arn'], recommender_conf)
            if rec_created or recommender_conf.get('status') != 'ACTIVE':
                all_recs_active = False

        # Create solutions, solution versions, and campaigns
        all_svs_active = True
        all_campaigns_active = True
        for solution_conf in dataset_group_conf.get('solutions', []):
            _,sv_created = create_solution_version(dataset_group_conf['arn'], solution_conf)
            if sv_created:
                all_svs_active = False
            elif solution_conf.get('solutionVersionStatus') == 'ACTIVE':
                campaign_conf = solution_conf.get('campaign')
                if campaign_conf:
                    _,campaign_created = create_campaign(solution_conf, campaign_conf)
                    if campaign_created or campaign_conf['status'] != 'ACTIVE':
                        all_campaigns_active = False
            else:
                all_svs_active = False

        # Create event tracker
        event_tracker_active = True
        event_tracker_conf  = dataset_group_conf.get('eventTracker')
        if event_tracker_conf:
            _,event_tracker_created = create_event_tracker(dataset_group_conf['arn'], event_tracker_conf)
            if event_tracker_created:
                event_tracker_active = False

        # Create filters
        all_filters_active = True
        for filter_conf in dataset_group_conf.get('filters', []):
            try:
                _,filter_created = create_filter(dataset_group_conf['arn'], filter_conf)
                if filter_created or filter_conf['status'] != 'ACTIVE':
                    all_filters_active = False
            except ClientError as e:
                if e.response['Error']['Code'] == 'LimitExceededException':
                    all_filters_active = False
                    logger.warn('Too many filters being created; backing off and retrying...')
                    break
                else:
                    raise e

        # Run batch inference jobs
        all_batch_inf_active = True
        if all_svs_active and all_filters_active:
            for solution_conf in dataset_group_conf.get('solutions', []):
                if solution_conf.get("generateFeaturedProductThemes", False):
                    if region in CONTENT_GENERATOR_REGIONS:
                        filter_arn = None
                        for filter_conf in dataset_group_conf["filters"]:
                            if filter_conf["name"] == "retaildemostore-filter-same-categories":
                                filter_arn = filter_conf["arn"]
                                break

                        _,job_created = create_theme_generation_job(solution_conf, filter_arn)
                        if job_created:
                            all_batch_inf_active = False
                        elif solution_conf['themeJobStatus'] == 'ACTIVE':
                            output_file = download_batch_inference_output(solution_conf)
                            update_products_with_themes(output_file)
                        else:
                            all_batch_inf_active = False
                    else:
                        logger.warn("Personalize content generator not supported in the current region (%s); skipping (https://docs.aws.amazon.com/personalize/latest/dg/themed-batch-recommendations.html#themes-regions)", region)

        if all_recs_active and all_svs_active and all_campaigns_active and event_tracker_active and all_filters_active and all_batch_inf_active:
            # All resources are active for the DSG. Set SSM params for filters, recommenders, and campaigns
            # Note that the event tracker SSM param value is set in create_event_tracker function.
            for filter_conf in dataset_group_conf.get('filters', []):
                if filter_conf.get('param'):
                    ssm.put_parameter(
                        Name=filter_conf['param'],
                        Description=filter_conf['paramDescription'],
                        Value='{}'.format(filter_conf['arn']),
                        Type='String',
                        Overwrite=True
                    )
            for recommender_conf in dataset_group_conf.get('recommenders', []):
                if recommender_conf.get('param'):
                    ssm.put_parameter(
                        Name=recommender_conf['param'],
                        Description=recommender_conf['paramDescription'],
                        Value='{}'.format(recommender_conf['arn']),
                        Type='String',
                        Overwrite=True
                    )
            for solution_conf in dataset_group_conf.get('solutions', []):
                campaign_conf = solution_conf.get('campaign')
                if campaign_conf and campaign_conf.get('param'):
                    ssm.put_parameter(
                        Name=campaign_conf['param'],
                        Description=campaign_conf['paramDescription'],
                        Value='{}'.format(campaign_conf['arn']),
                        Type='String',
                        Overwrite=True
                    )
        else:
            # More waiting required.
            logger.info('DSG %s not done: all_recs_active = %s; all_svs_active = %s; all_campaigns_active = %s; event_tracker_active = %s; all_filters_active = %s; all_batch_inf_active = %s',
                    dataset_group_conf["name"], all_recs_active, all_svs_active, all_campaigns_active, event_tracker_active, all_filters_active, all_batch_inf_active)
            done = False

    if done:
        # Last thing to do on our way out is to trigger a rebuild and deploy of the webapp so any
        # statically declared settings (like event tracker) get picked up.
        rebuild_webui_service(region, account_id)

    return done

@cloudformation_helper.poll_create
def poll_create(event, context) -> bool:
    if create_personalize_resources:
        # Enable the event rule so we start getting called repeatedly.
        enable_event_rule(lambda_event_rule_name)
        # Let's get some work started since we're here.
        update()

    return True

@cloudformation_helper.poll_delete
def poll_delete(event, context) -> bool:
    """
     Called on deletion by CloudFormation.

     Incrementally deletes resources for both dataset groups.

     Args:
         event: We ignore this - we know what needs to be deleted
         context: We ignore this

     Returns:
         True if polling is finished.
     """

    try:
        dataset_group_names = []
        for dataset_group_conf in dataset_group_confs:
            dataset_group_names.append(dataset_group_conf['name'])

        delete_dataset_groups(dataset_group_names, region, wait_for_resources = False)

        # Clear/reset SSM params.
        for dataset_group_conf in dataset_group_confs:
            for filter_conf in dataset_group_conf.get('filters', []):
                if filter_conf.get('param'):
                    ssm.put_parameter(
                        Name=filter_conf['param'],
                        Description=filter_conf['paramDescription'],
                        Value='NONE',
                        Type='String',
                        Overwrite=True
                    )
            for recommender_conf in dataset_group_conf.get('recommenders', []):
                if recommender_conf.get('param'):
                    ssm.put_parameter(
                        Name=recommender_conf['param'],
                        Description=recommender_conf['paramDescription'],
                        Value='NONE',
                        Type='String',
                        Overwrite=True
                    )
            for solution_conf in dataset_group_conf.get('solutions', []):
                campaign_conf = solution_conf.get('campaign')
                if campaign_conf and campaign_conf.get('param'):
                    ssm.put_parameter(
                        Name=campaign_conf['param'],
                        Description=campaign_conf['paramDescription'],
                        Value='NONE',
                        Type='String',
                        Overwrite=True
                    )
            if dataset_group_conf.get('eventTracker') and dataset_group_conf['eventTracker'].get('param'):
                ssm.put_parameter(
                    Name=dataset_group_conf['eventTracker']['param'],
                    Description=dataset_group_conf['eventTracker']['paramDescription'],
                    Value='NONE',
                    Type='String',
                    Overwrite=True
                )

        # All done!
        return True
    except ResourcePending as e:
        # Still more to do.
        logger.info(str(e))

    return False

def lambda_handler(event, context):
    """ Continues current state of Personalize resource creation process

    This function can either be called from CloudFormation as a custom resource
    or from EventBridge as a CloudWatch event.
    """
    logger.debug('## ENVIRONMENT VARIABLES')
    logger.debug(os.environ)
    logger.debug('## EVENT')
    logger.debug(event)

    ## Inspect the event - if it is coming from EventBridge then it is polling after reset
    ## If it is coming from CloudFormation then use the helper to create or tear down
    if "source" in event and event["source"] == "aws.events":
        done = update()
        if done:
            logger.info('All work completed; disabling event rule')
            disable_event_rule(lambda_event_rule_name)
            return {
                'statusCode': 200,
                'body': json.dumps("Event rule disabled")
            }
        else:
            logger.info('Still more work to do; returning until next callback')
            return {
                'statusCode': 200,
                'body': json.dumps("Polled Personalize Create Update")
            }
    else:
        # We have a Cloud Formation Event - the event contains info about whether it wants to update, create or delete
        cloudformation_helper(event, context)
