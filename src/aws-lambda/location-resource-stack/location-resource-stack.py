# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import logging
import os
import random
import string
import json

from crhelper import CfnResource
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

RESOURCE_BUCKET = os.environ.get('RESOURCE_BUCKET')
RESOURCE_BUCKET_PATH = os.environ.get('RESOURCE_BUCKET_PATH')

helper = CfnResource()
location = boto3.client('location')
s3 = boto3.resource('s3')


def load_default_geofence_from_s3():
    """ Retrieves GeoJson file containing store Geofence from S3 """
    return load_json_from_s3(RESOURCE_BUCKET_PATH + 'location_services/store_geofence.json')


def load_json_from_s3(object_key):
    """ Loads a JSON object from S3 and returns it as a Python dict """
    file_obj = s3.Object(RESOURCE_BUCKET, object_key)
    object_json = json.loads(file_obj.get()['Body'].read().decode('utf-8'))
    return object_json


def get_random_string(length):
    """ Generates a random string of upper & lower case letters. """
    letters = string.ascii_letters
    rand_string = ''.join(random.choice(letters) for i in range(length))
    return rand_string


def get_geofence_collection_arn(region, account_id, collection_name):
    """ Helper to convert Geofence Collection name to ARN, since this information is not available directly from the
    Geofencing API. """
    return f"arn:aws:geo:{region}:{account_id}:geofence-collection/{collection_name}"


def get_default_geofence_id(resource_name):
    """ Helper to ensure consistency when referring to default Geofence by id (name) """
    return f"{resource_name}-default-geofence"


def put_default_geofence(resource_name):
    """ Creates a default Geofence around central London """
    geofence_geojson = load_default_geofence_from_s3()
    logger.info("Creating default Geofence")
    put_geofence(resource_name, geofence_geojson, get_default_geofence_id(resource_name))


def put_geofence(resource_name, geojson, geofence_id):
    """ Creates a Geofence in a given Geofence Collection """
    geofence = {
        "Polygon": geojson['features'][0]['geometry']['coordinates']
    }
    logger.info(f"Creating Geofence: {geofence}")
    response = location.put_geofence(
        CollectionName=resource_name,
        Geometry=geofence,
        GeofenceId=geofence_id
    )
    logger.info(response)


def associate_tracker(collection_arn, tracker_name):

    # Associate tracker consumer ie. link tracker & geofence
    logger.info(f"Associating Tracker {tracker_name} with Geofence Collection ARN: {collection_arn}")
    response = location.associate_tracker_consumer(
        ConsumerArn=collection_arn,
        TrackerName=tracker_name
    )
    logger.info(response)


@helper.create
def create(event, context):
    stack_name = event['StackName']
    region = event['Region']
    account_id = event['AccountId']
    create_default_geofence = event['ResourceProperties']['CreateDefaultGeofence'].lower() == 'true'

    # Generate the resource name to be used for all Location resources
    resource_name = stack_name + '-' + get_random_string(8)
    helper.PhysicalResourceId = resource_name
    helper.Data.update({'LocationResourceName': resource_name})

    # Create a map
    logger.info(f"Creating Map with name: {resource_name}")
    response = location.create_map(
        MapName=resource_name,
        Configuration={
            'Style': 'VectorEsriNavigation'
        },
        Description=f'Map belonging to CloudFormation Stack {stack_name}',
        PricingPlan='RequestBasedUsage'
    )
    logger.info(response)

    # Create a geofence collection
    logger.info(f"Creating Geofence Collection with name: {resource_name}")
    response = location.create_geofence_collection(
        CollectionName=resource_name,
        Description=f'Collection belonging to CloudFormation Stack {stack_name}',
        PricingPlan='RequestBasedUsage'
    )
    logger.info(response)
    collection_arn = get_geofence_collection_arn(region, account_id, resource_name)

    # Create a geofence
    if create_default_geofence:
        put_default_geofence(resource_name)

    # Create a tracker
    logger.info(f"Creating Tracker with name: {resource_name}")
    response = location.create_tracker(
        TrackerName=resource_name,
        Description=f'Tracker belonging to CloudFormation Stack {stack_name}',
        PricingPlan='RequestBasedUsage'
    )
    logger.info(response)

    # Associate tracker consumer ie. link tracker & geofence
    associate_tracker(collection_arn, resource_name)

    # Create Place Index
    logger.info(f"Creating Place Index with name: {resource_name}")
    response = location.create_place_index(
          DataSource='Esri',
          Description=f'Place Index belonging to CloudFormation Stack {stack_name}',
          IndexName=resource_name,
        PricingPlan='RequestBasedUsage'
      )
    logger.info(response)

    logger.info("Creation complete.")
    return resource_name


@helper.update
def update(event, context):
    resource_name = event['PhysicalResourceId']
    create_default_geofence = event['ResourceProperties']['CreateDefaultGeofence'].lower() == 'true'
    previous_create_default_geofence = event['OldResourceProperties']['CreateDefaultGeofence'].lower() == 'true'

    if create_default_geofence != previous_create_default_geofence:
        if create_default_geofence:
            put_default_geofence(resource_name)
        else:
            geofence_id = get_default_geofence_id(resource_name)
            logger.info(f"Deleting Geofence: {geofence_id}")
            try:
                response = location.batch_delete_geofence(
                    CollectionName=resource_name,
                    GeofenceIds=[geofence_id]
                )
                logger.info(response)
            except location.exceptions.ResourceNotFoundException:
                logger.warning(f"Geofence could not be deleted as does not exist: {geofence_id}")

    logger.info("Update complete.")
    return


@helper.delete
def delete(event, context):
    resource_name = event['PhysicalResourceId']

    # Delete Map
    logger.info(f"Deleting Map: {resource_name}")
    try:
        response = location.delete_map(MapName=resource_name)
        logger.info(response)
    except location.exceptions.ResourceNotFoundException:
        logger.info(f"Map {resource_name} does not exist, nothing to delete")

    # Delete Geofence Collection
    logger.info(f"Deleting Geofence Collection: {resource_name}")
    try:
        response = location.delete_geofence_collection(CollectionName=resource_name)
        logger.info(response)
    except location.exceptions.ResourceNotFoundException:
        logger.info(f"Geofence Collection {resource_name} does not exist, nothing to delete")

    # Delete Tracker
    logger.info(f"Deleting Tracker: {resource_name}")
    try:
        response = location.delete_tracker(TrackerName=resource_name)
        logger.info(response)
    except location.exceptions.ResourceNotFoundException:
        logger.info(f"Tracker {resource_name} does not exist, nothing to delete")

    # Delete Place Index
    logger.info(f"Deleting Place Index: {resource_name}")
    try:
        response = location.delete_place_index(IndexName=resource_name)
        logger.info(response)
    except location.exceptions.ResourceNotFoundException:
        logger.info(f"Place index {resource_name} does not exist, nothing to delete")

    logger.info("Deletion complete.")
    return


def lambda_handler(event, context):
    logger.info('Environment:')
    logger.info(os.environ)
    logger.info('Event:')
    logger.info(event)

    # Set stack name in the event here once for use across all handlers
    event['StackName'] = event['StackId'].split('/')[-2]
    event['Region'] = event['StackId'].split(':')[3]
    event['AccountId'] = event['StackId'].split(':')[4]

    helper(event, context)
