#!/usr/bin/env python
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

"""
Deletes one or more Amazon Personalize dataset groups, including all of their associated resources:

- Recommenders
- Campaigns
- Filters
- Solutions (includes Solution Versions)
- Event Tracker
- Datasets
- Schemas (associated with datasets)
- Dataset Group

Command line arguments:

-n/--name= - comma delimited list of dataset group names (required)
-r/--region= - region name (optional, will use default if not specified)

Examples:

aws_personalize_delete_dsg.py -n my_dataset_group -r us-east-1
aws_personalize_delete_dsg.py --name=my_dataset_group
aws_personalize_delete_dsg.py --name=my_dataset_group1,my_dataset_group2

Credentials will be picked up by boto3 based on your environment.
"""

import sys
import getopt
import logging
import botocore
import boto3
import time
from typing import List, Tuple
from packaging import version
from botocore.exceptions import ClientError

logger = logging.getLogger()
personalize = None

class ResourcePending(Exception):
    pass

def _get_dataset_group_arn(dataset_group_name: str) -> str:
    dsg_arn = None

    paginator = personalize.get_paginator('list_dataset_groups')
    for paginate_result in paginator.paginate():
        for dataset_group in paginate_result["datasetGroups"]:
            if dataset_group['name'] == dataset_group_name:
                dsg_arn = dataset_group['datasetGroupArn']
                break

        if dsg_arn:
            break

    return dsg_arn

def _get_solutions(dataset_group_arn: str) -> List[str]:
    solution_arns = []

    paginator = personalize.get_paginator('list_solutions')
    for paginate_result in paginator.paginate(datasetGroupArn = dataset_group_arn):
        for solution in paginate_result['solutions']:
            solution_arns.append(solution['solutionArn'])

    return solution_arns

def _delete_recommenders_and_campaigns(dataset_group_arn: str, solution_arns: List[str], wait_for_resources: bool = True):
    recommender_arns = []

    paginator = personalize.get_paginator('list_recommenders')
    for recommender_page in paginator.paginate(datasetGroupArn = dataset_group_arn):
        for recommender in recommender_page['recommenders']:
            # Recommender status transitions:
            # CREATE PENDING > CREATE IN_PROGRESS > ACTIVE -or- CREATE FAILED
            # STOP PENDING > STOP IN_PROGRESS > INACTIVE > START PENDING > START IN_PROGRESS > ACTIVE
            # DELETE PENDING > DELETE IN_PROGRESS
            if recommender['status'] in [ 'ACTIVE', 'INACTIVE', 'CREATE FAILED' ]:
                logger.info('Deleting recommender {}'.format(recommender['recommenderArn']))
                personalize.delete_recommender(recommenderArn = recommender['recommenderArn'])
            elif recommender['status'].startswith('DELETE'):
                logger.warning('Recommender {} is already being deleted so will wait for delete to complete'.format(recommender['recommenderArn']))
            elif recommender['status'].startswith('CREATE'):
                logger.warning('Recommender {} is currently being created so will wait for it to complete before deleting'.format(recommender['recommenderArn']))
            elif recommender['status'].startswith('STOP'):
                logger.warning('Recommender {} is currently being stopped so will wait for it to complete before deleting'.format(recommender['recommenderArn']))
            elif recommender['status'].startswith('START'):
                logger.warning('Recommender {} is currently being started so will wait for it to complete before deleting'.format(recommender['recommenderArn']))
            else:
                raise Exception('Recommender {} has a status of {} so cannot be deleted'.format(recommender['recommenderArn'], recommender['status']))

            recommender_arns.append(recommender['recommenderArn'])

    campaign_arns = []

    for solution_arn in solution_arns:
        paginator = personalize.get_paginator('list_campaigns')
        for paginate_result in paginator.paginate(solutionArn = solution_arn):
            for campaign in paginate_result['campaigns']:
                # Campaign status transitions:
                # CREATE PENDING > CREATE IN_PROGRESS > ACTIVE -or- CREATE FAILED
                # DELETE PENDING > DELETE IN_PROGRESS
                if campaign['status'] in ['ACTIVE', 'CREATE FAILED']:
                    logger.info('Deleting campaign: ' + campaign['campaignArn'])
                    personalize.delete_campaign(campaignArn = campaign['campaignArn'])
                elif campaign['status'].startswith('DELETE'):
                    logger.warning('Campaign {} is already being deleted so will wait for delete to complete'.format(campaign['campaignArn']))
                elif campaign['status'].startswith('CREATE'):
                    logger.warning('Campaign {} is currently being created so will wait for it to complete before deleting'.format(campaign['campaignArn']))
                else:
                    raise Exception('Campaign {} has a status of {} so cannot be deleted'.format(campaign['campaignArn'], campaign['status']))

                campaign_arns.append(campaign['campaignArn'])

    max_time = time.time() + 30*60 # 30 mins
    while time.time() < max_time:
        for recommender_arn in recommender_arns:
            try:
                describe_response = personalize.describe_recommender(recommenderArn = recommender_arn)
                recommender = describe_response['recommender']
                logger.debug('Recommender {} status is {}'.format(recommender_arn, recommender['status']))
                if recommender['status'] in [ 'ACTIVE', 'INACTIVE', 'CREATE FAILED' ]:
                    logger.info('Deleting recommender {}'.format(recommender['recommenderArn']))
                    personalize.delete_recommender(recommenderArn = recommender['recommenderArn'])
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == 'ResourceNotFoundException':
                    recommender_arns.remove(recommender_arn)

        if len(recommender_arns) == 0:
            logger.info('All recommenders have been deleted or none exist for dataset group')
            break
        elif wait_for_resources:
            logger.info('Waiting for {} recommender(s) to be deleted'.format(len(recommender_arns)))
            time.sleep(20)
        else:
            raise ResourcePending(f'There are {len(recommender_arns)} recommender(s) still being deleted')

    if len(recommender_arns) > 0:
        raise ResourcePending('Timed out waiting for all recommenders to be deleted')

    max_time = time.time() + 30*60 # 30 mins
    while time.time() < max_time:
        for campaign_arn in campaign_arns:
            try:
                describe_response = personalize.describe_campaign(campaignArn = campaign_arn)
                campaign = describe_response["campaign"]
                logger.debug('Campaign {} status is {}'.format(campaign_arn, campaign['status']))
                if campaign['status'] in ['ACTIVE', 'CREATE FAILED']:
                    logger.info('Deleting campaign: %s', campaign['campaignArn'])
                    personalize.delete_campaign(campaignArn = campaign['campaignArn'])
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == 'ResourceNotFoundException':
                    campaign_arns.remove(campaign_arn)

        if len(campaign_arns) == 0:
            logger.info('All campaigns have been deleted or none exist for dataset group')
            break
        elif wait_for_resources:
            logger.info('Waiting for {} campaign(s) to be deleted'.format(len(campaign_arns)))
            time.sleep(20)
        else:
            raise ResourcePending(f'There are {len(campaign_arns)} campaign(s) still being deleted')

    if len(campaign_arns) > 0:
        raise ResourcePending('Timed out waiting for all campaigns to be deleted')

def _is_solution_deletable(solution) -> Tuple[bool, bool]:
    # Solution status transitions:
    # CREATE PENDING > CREATE IN_PROGRESS > ACTIVE -or- CREATE FAILED
    # DELETE PENDING > DELETE IN_PROGRESS
    if solution["status"] in ["ACTIVE", "CREATE FAILED"]:
        # Solution version status transitions:
        # CREATE PENDING > CREATE IN_PROGRESS > ACTIVE -or- CREATE FAILED
        # CREATE STOPPING > CREATE STOPPED
        if "latestSolutionVersion" in solution and solution["latestSolutionVersion"]["status"] in ["CREATE PENDING", "CREATE IN_PROGRESS"]:
            return False, True  # Solution version can be stopped
        elif "latestSolutionVersion" in solution and solution["latestSolutionVersion"]["status"] == "CREATE STOPPING":
            return False, False # Solution version is stopping; have to wait

        return True, False  # Solution can be deleted
    elif solution['status'].startswith('DELETE'):
        return False, False # Solution is already being deleted; have to wait
    elif solution['status'].startswith('CREATE'):
        return False, False # Solution is being created; have to wait

    raise Exception('Solution {} has a status of {} so cannot be deleted'.format(solution["solutionArn"], solution['status']))

def _delete_solutions(solution_arns: List[str], wait_for_resources: bool = True):
    for solution_arn in solution_arns:
        try:
            describe_response = personalize.describe_solution(solutionArn = solution_arn)
            solution = describe_response['solution']

            soln_can_be_deleted, sv_can_be_stopped = _is_solution_deletable(solution)

            if sv_can_be_stopped:
                logger.warning('Solution %s is %s but currently has a solution version being created/trained so will stop solution version before deleting', solution_arn, solution["status"])
                logger.info('Stopping solution version %s', solution["latestSolutionVersion"]["solutionVersionArn"])
                personalize.stop_solution_version_creation(solutionVersionArn = solution["latestSolutionVersion"]["solutionVersionArn"])
            elif soln_can_be_deleted:
                logger.info('Deleting solution: {}'.format(solution_arn))
                personalize.delete_solution(solutionArn = solution_arn)
            elif "latestSolutionVersion" in solution:
                logger.warning('Solution %s is %s and has latest solution version in %s; cannot be deleted', solution_arn, solution["status"], solution["latestSolutionVersion"]["status"])
            else:
                logger.info('Solution %s is %s', solution_arn, solution["status"])
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code != 'ResourceNotFoundException':
                raise e

    max_time = time.time() + 30*60 # 30 mins
    while time.time() < max_time:
        for solution_arn in solution_arns:
            try:
                describe_response = personalize.describe_solution(solutionArn = solution_arn)
                solution = describe_response['solution']
                if "latestSolutionVersion" in solution:
                    logger.debug('Solution %s is %s and has latest solution version in %s; cannot be deleted', solution_arn, solution["status"], solution["latestSolutionVersion"]["status"])
                else:
                    logger.debug('Solution %s is %s', solution_arn, solution["status"])

                soln_can_be_deleted, sv_can_be_stopped = _is_solution_deletable(solution)

                if sv_can_be_stopped:
                    logger.warning('Solution %s is %s but currently has a solution version being created/trained so will stop solution version before deleting', solution_arn, solution["status"])
                    logger.info('Stopping solution version %s', solution["latestSolutionVersion"]["solutionVersionArn"])
                    personalize.stop_solution_version_creation(solutionVersionArn = solution["latestSolutionVersion"]["solutionVersionArn"])
                elif soln_can_be_deleted:
                    logger.info('Deleting solution: %s', solution_arn)
                    personalize.delete_solution(solutionArn = solution_arn)

            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == 'ResourceNotFoundException':
                    solution_arns.remove(solution_arn)

        if len(solution_arns) == 0:
            logger.info('All solutions have been deleted or none exist for dataset group')
            break
        elif wait_for_resources:
            logger.info('Waiting for {} solution(s) to be deleted'.format(len(solution_arns)))
            time.sleep(20)
        else:
            raise ResourcePending(f'There are {len(solution_arns)} solution(s) still being deleted')

    if len(solution_arns) > 0:
        raise ResourcePending('Timed out waiting for all solutions to be deleted')

def _delete_event_trackers(dataset_group_arn: str, wait_for_resources: bool = True):
    event_tracker_arns = []

    event_trackers_paginator = personalize.get_paginator('list_event_trackers')
    for event_tracker_page in event_trackers_paginator.paginate(datasetGroupArn = dataset_group_arn):
        for event_tracker in event_tracker_page['eventTrackers']:
            # CREATE PENDING > CREATE IN_PROGRESS > ACTIVE -or- CREATE FAILED
            # DELETE PENDING > DELETE IN_PROGRESS
            if event_tracker['status'] in [ 'ACTIVE', 'CREATE FAILED' ]:
                logger.info('Deleting event tracker {}'.format(event_tracker['eventTrackerArn']))
                personalize.delete_event_tracker(eventTrackerArn = event_tracker['eventTrackerArn'])
            elif event_tracker['status'].startswith('DELETE'):
                logger.warning('Event tracker {} is already being deleted so will wait for delete to complete'.format(event_tracker['eventTrackerArn']))
            elif event_tracker['status'].startswith('CREATE'):
                logger.warning('Event tracker {} is being created so will wait for create to complete'.format(event_tracker['eventTrackerArn']))
            else:
                raise Exception('Solution {} has a status of {} so cannot be deleted'.format(event_tracker['eventTrackerArn'], event_tracker['status']))

            event_tracker_arns.append(event_tracker['eventTrackerArn'])

    max_time = time.time() + 30*60 # 30 mins
    while time.time() < max_time:
        for event_tracker_arn in event_tracker_arns:
            try:
                describe_response = personalize.describe_event_tracker(eventTrackerArn = event_tracker_arn)
                event_tracker = describe_response["eventTracker"]
                logger.debug('Event tracker {} status is {}'.format(event_tracker_arn, event_tracker['status']))
                if event_tracker['status'] in [ 'ACTIVE', 'CREATE FAILED' ]:
                    logger.info('Deleting event tracker %s', event_tracker_arn)
                    personalize.delete_event_tracker(eventTrackerArn = event_tracker_arn)
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == 'ResourceNotFoundException':
                    event_tracker_arns.remove(event_tracker_arn)

        if len(event_tracker_arns) == 0:
            logger.info('All event trackers have been deleted or none exist for dataset group')
            break
        elif wait_for_resources:
            logger.info('Waiting for {} event tracker(s) to be deleted'.format(len(event_tracker_arns)))
            time.sleep(20)
        else:
            raise ResourcePending(f'There are {len(event_tracker_arns)} event tracker(s) still being deleted')

    if len(event_tracker_arns) > 0:
        raise ResourcePending('Timed out waiting for all event trackers to be deleted')

def _delete_filters(dataset_group_arn: str, wait_for_resources: bool = True):
    filter_arns = []

    filters_response = personalize.list_filters(datasetGroupArn = dataset_group_arn, maxResults = 100)
    for filter in filters_response['Filters']:
        filter_arns.append(filter['filterArn'])
        # Filter status transitions:
        # CREATE PENDING > CREATE IN_PROGRESS > ACTIVE -or- CREATE FAILED
        # DELETE PENDING > DELETE IN_PROGRESS
        if filter['status'] in ['ACTIVE', 'CREATE FAILED']:
            logger.info('Deleting filter %s', filter['filterArn'])
            personalize.delete_filter(filterArn = filter['filterArn'])
        elif filter['status'].startswith('DELETE'):
            logger.warning('Filter %s is already being deleted so will wait for delete to complete', filter["filterArn"])
        elif filter['status'].startswith('CREATE'):
            logger.warning('Filter %s is currently being created so will wait for it to complete before deleting', filter["filterArn"])
        else:
            raise Exception('Filter {} has a status of {} so cannot be deleted'.format(filter['filterArn'], filter['status']))

    max_time = time.time() + 30*60 # 30 mins
    while time.time() < max_time:
        for filter_arn in filter_arns:
            try:
                describe_response = personalize.describe_filter(filterArn = filter_arn)
                filter = describe_response["filter"]
                logger.debug('Filter %s status is %s', filter_arn, filter['status'])
                if filter['status'] in ['ACTIVE', 'CREATE FAILED']:
                    logger.info('Deleting filter %s', filter_arn)
                    personalize.delete_filter(filterArn = filter_arn)
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == 'ResourceNotFoundException':
                    filter_arns.remove(filter_arn)

        if len(filter_arns) == 0:
            logger.info('All filters have been deleted or none exist for dataset group')
            break
        elif wait_for_resources:
            logger.info('Waiting for {} filter(s) to be deleted'.format(len(filter_arns)))
            time.sleep(20)
        else:
            raise ResourcePending(f'There are {len(filter_arns)} filter(s) still being deleted')

    if len(filter_arns) > 0:
        raise ResourcePending('Timed out waiting for all filter to be deleted')

def _delete_datasets_and_schemas(dataset_group_arn: str, wait_for_resources: bool = True):
    dataset_arns = []
    schema_arns = []

    dataset_paginator = personalize.get_paginator('list_datasets')
    for dataset_page in dataset_paginator.paginate(datasetGroupArn = dataset_group_arn):
        for dataset in dataset_page['datasets']:
            describe_response = personalize.describe_dataset(datasetArn = dataset['datasetArn'])
            schema_arns.append(describe_response['dataset']['schemaArn'])

            # Dataset status transitions:
            # CREATE PENDING > CREATE IN_PROGRESS > ACTIVE -or- CREATE FAILED
            # DELETE PENDING > DELETE IN_PROGRESS
            if dataset['status'] in ['ACTIVE', 'CREATE FAILED']:
                logger.info('Deleting dataset %s', dataset['datasetArn'])
                personalize.delete_dataset(datasetArn = dataset['datasetArn'])
            elif dataset['status'].startswith('DELETE'):
                logger.warning('Dataset %s is already being deleted so will wait for delete to complete', dataset['datasetArn'])
            elif dataset['status'].startswith('CREATE'):
                logger.warning('Dataset %s is being created so will wait for create to complete', dataset['datasetArn'])
            else:
                raise Exception('Dataset {} has a status of {} so cannot be deleted'.format(dataset['datasetArn'], dataset['status']))

            dataset_arns.append(dataset['datasetArn'])

    max_time = time.time() + 30*60 # 30 mins
    while time.time() < max_time:
        for dataset_arn in dataset_arns:
            try:
                describe_response = personalize.describe_dataset(datasetArn = dataset_arn)
                dataset = describe_response["dataset"]
                logger.debug('Dataset %s status is %s', dataset_arn, dataset['status'])
                if dataset['status'] in ['ACTIVE', 'CREATE FAILED']:
                    logger.info('Deleting dataset %s', dataset_arn)
                    personalize.delete_dataset(datasetArn = dataset_arn)

            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == 'ResourceNotFoundException':
                    dataset_arns.remove(dataset_arn)

        if len(dataset_arns) == 0:
            logger.info('All datasets have been deleted or none exist for dataset group')
            break
        elif wait_for_resources:
            logger.info('Waiting for {} dataset(s) to be deleted'.format(len(dataset_arns)))
            time.sleep(20)
        else:
            raise ResourcePending(f'There are {len(dataset_arns)} dataset(s) still being deleted')

    if len(dataset_arns) > 0:
        raise ResourcePending('Timed out waiting for all datasets to be deleted')

    for schema_arn in schema_arns:
        try:
            logger.info('Deleting schema ' + schema_arn)
            personalize.delete_schema(schemaArn = schema_arn)
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ResourceInUseException':
                logger.info('Schema {} is still in-use by another dataset (likely in another dataset group)'.format(schema_arn))
            else:
                raise e

    logger.info('All schemas used exclusively by datasets have been deleted or none exist for dataset group')

def _delete_dataset_group(dataset_group_arn: str, wait_for_resources: bool = True):
    try:
        describe_response = personalize.describe_dataset_group(datasetGroupArn = dataset_group_arn)
        dsg = describe_response['datasetGroup']
        logger.debug('Dataset group {} status is {}'.format(dataset_group_arn, dsg['status']))
        # Dataset group status transitions:
        # CREATE PENDING > CREATE IN_PROGRESS > ACTIVE -or- CREATE FAILED
        # DELETE PENDING
        if dsg['status'] in ['ACTIVE', 'CREATE FAILED']:
            logger.info('Deleting dataset group %s', dataset_group_arn)
            personalize.delete_dataset_group(datasetGroupArn = dataset_group_arn)
        elif dsg['status'].startswith('DELETE'):
            logger.warning('Dataset Group {} is already being deleted so will wait for delete to complete'.format(dataset_group_arn))
        elif dsg['status'].startswith('CREATE'):
            logger.warning('Dataset Group {} is currently being created so will wait for it to complete before deleting'.format(dataset_group_arn))
        else:
            raise Exception('Dataset Group {} has a status of {} so cannot be deleted'.format(dataset_group_arn, dsg['status']))
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'ResourceNotFoundException':
            logger.info('Dataset group {} does not exist'.format(dataset_group_arn))
            return
        raise e

    max_time = time.time() + 30*60 # 30 mins
    while time.time() < max_time:
        try:
            describe_response = personalize.describe_dataset_group(datasetGroupArn = dataset_group_arn)
            dsg = describe_response["datasetGroup"]
            logger.debug('Dataset group %s status is %s', dataset_group_arn, dsg['status'])
            if dsg['status'] in ['ACTIVE', 'CREATE FAILED']:
                logger.info('Deleting dataset group %s', dataset_group_arn)
                personalize.delete_dataset_group(datasetGroupArn = dataset_group_arn)
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ResourceNotFoundException':
                logger.info('Dataset group %s has been fully deleted', dataset_group_arn)
                break
            else:
                raise e

        if wait_for_resources:
            logger.info('Waiting for dataset group to be deleted')
            time.sleep(20)
        else:
            raise ResourcePending('Dataset group still being deleted')

def delete_dataset_groups(dataset_group_names: List[str], region: str = None, wait_for_resources: bool = True):
    min_botocore_version = '1.23.15' # As of re:Invent 2021 when domain recommenders were added to the API
    if version.parse(botocore.__version__) < version.parse(min_botocore_version):
        raise Exception(f'Current botocore version {botocore.__version__} does not meet minimum required version of {min_botocore_version}; please upgrade boto3/botocore and try again')

    global personalize
    personalize = boto3.client(service_name = 'personalize', region_name = region)

    for dataset_group_name in dataset_group_names:
        dataset_group_arn = _get_dataset_group_arn(dataset_group_name)
        if not dataset_group_arn:
            logger.warning('Dataset Group "%s" does not exist; verify region is correct', dataset_group_name)
            continue

        logger.info('Dataset Group ARN: %s', dataset_group_arn)

        solution_arns = _get_solutions(dataset_group_arn)

        # 1. Delete recommenders and campaigns
        _delete_recommenders_and_campaigns(dataset_group_arn = dataset_group_arn, solution_arns = solution_arns, wait_for_resources = wait_for_resources)

        # 2. Delete solutions
        _delete_solutions(solution_arns = solution_arns, wait_for_resources = wait_for_resources)

        # 3. Delete event trackers
        _delete_event_trackers(dataset_group_arn = dataset_group_arn, wait_for_resources = wait_for_resources)

        # 4. Delete filters
        _delete_filters(dataset_group_arn = dataset_group_arn, wait_for_resources = wait_for_resources)

        # 5. Delete datasets and their schemas
        _delete_datasets_and_schemas(dataset_group_arn = dataset_group_arn, wait_for_resources = wait_for_resources)

        # 6. Delete dataset group
        _delete_dataset_group(dataset_group_arn = dataset_group_arn, wait_for_resources = wait_for_resources)

        logger.info(f'Dataset group {dataset_group_name} fully deleted')

def _main(argv):
    region = None
    dataset_group_names = []

    try:
        opts, _ = getopt.getopt(argv, 'hn:r:', ['name=', 'region='])
    except getopt.GetoptError:
        print(f'Usage: {sys.argv[0]} -n dataset-group-names [-r region]')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print(f'Usage: {sys.argv[0]} -n dataset-group-names [-r region]')
            sys.exit()
        elif opt in ('-n', '--name'):
            dataset_group_names = arg.split(',')
        elif opt in ('-r', '--region'):
            region = arg

    if len(dataset_group_names) == 0:
        print('Dataset group name(s) is required')
        print(f'Usage: {sys.argv[0]} -n dataset-group-names [-r region]')
        sys.exit(1)

    delete_dataset_groups(dataset_group_names, region)

if __name__=="__main__":
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    logger.addHandler(handler)

    _main(sys.argv[1:])
