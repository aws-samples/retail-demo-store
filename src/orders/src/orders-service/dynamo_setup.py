# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import os
import time
import boto3
from server import app

def create_table(client, ddb_table_name, 
                 attribute_definitions, 
                 key_schema, 
                 global_secondary_indexes=None):
    try: 
        client.create_table(
            TableName=ddb_table_name,
            KeySchema=key_schema,
            AttributeDefinitions=attribute_definitions,
            GlobalSecondaryIndexes=global_secondary_indexes or [],
            BillingMode="PAY_PER_REQUEST",
        )
        print(f'Created table: {ddb_table_name}')
    except Exception as e:
        if e.response["Error"]["Code"] == "ResourceInUseException":
            app.logger.info(f'Table {ddb_table_name} already exists; continuing...')
        else:
            raise e


# DynamoDB table names passed via environment
ddb_table_orders = os.getenv("DDB_TABLE_ORDERS")

# Allow DDB endpoint to be overridden to support amazon/dynamodb-local
ddb_endpoint_override = os.getenv("DDB_ENDPOINT_OVERRIDE")
running_local = False

dynamo_resource = None

def verify_local_ddb_running(endpoint, dynamo_client):
    app.logger.info(f"Verifying that local DynamoDB is running at: {endpoint}")
    for _ in range(5):
        try:
            response = dynamo_client.list_tables()
            if ddb_table_orders not in response["TableNames"]:
                create_table(
                    ddb_table_name=ddb_table_orders,
                    client=dynamo_client,
                    attribute_definitions=[
                        {"AttributeName": "id", "AttributeType": "S"},
                        {"AttributeName": "username", "AttributeType": "S"}
                    ],
                    key_schema=[
                        {"AttributeName": "id", "KeyType": "HASH"},
                    ],
                    global_secondary_indexes=[
                        {
                            "IndexName": "username-index",
                            "KeySchema": [{
                                "AttributeName": "username", 
                                "KeyType": "HASH"}],
                            "Projection": {"ProjectionType": "ALL"},
                            "ProvisionedThroughput": {
                                "ReadCapacityUnits": 5,
                                "WriteCapacityUnits": 5,
                            }
                        }
                    ]
                )
            app.logger.info("DynamoDB local is responding!")
            return
        except Exception as e:
            app.logger.info(e)
            app.logger.info(
                "Local DynamoDB service is not ready yet... pausing before trying again"
                )
            time.sleep(2)
    app.logger.error(
        "Local DynamoDB service not responding;\
        verify that your docker-compose .env file is setup correctly"
        )
    exit(1)

def setup():
    global dynamo_resource, running_local

    if ddb_endpoint_override:
        running_local = True
        app.logger.info("Creating DDB client with endpoint override: " 
                        + ddb_endpoint_override)
        dynamo_resource = boto3.resource(
            'dynamodb',
            endpoint_url=ddb_endpoint_override,
            region_name='us-west-2',
            aws_access_key_id='XXXX',
            aws_secret_access_key='XXXX'
        )
        verify_local_ddb_running(ddb_endpoint_override, dynamo_resource.meta.client)
    else:
        running_local = False
        dynamo_resource = boto3.resource('dynamodb')

setup()