# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import os
import time
import boto3
from server import app

def create_table(client, ddb_table_name, attribute_definitions, key_schema, global_secondary_indexes=None):
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

def enable_ttl_on_table(client, table_name, ttl_attribute):
    try:
        response = client.update_time_to_live(
            TableName=table_name,
            TimeToLiveSpecification={
                'Enabled': True,
                'AttributeName': ttl_attribute
            }
        )
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            print(f'TTL has been enabled on {table_name} for attribute {ttl_attribute}')
        else:
            print(f'Failed to enable TTL on {table_name} for attribute {ttl_attribute}')
    except Exception as e:
        app.logger.info(f'Error enabling TTL: {e}')

# DynamoDB table names passed via environment
ddb_table_carts = os.getenv("DDB_TABLE_CARTS")

# Allow DDB endpoint to be overridden to support amazon/dynamodb-local
ddb_endpoint_override = os.getenv("DDB_ENDPOINT_OVERRIDE")
running_local = False

dynamo_client = None

def verify_local_ddb_running(endpoint, dynamo_client):
    app.logger.info(f"Verifying that local DynamoDB is running at: {endpoint}")
    for _ in range(5):
        try:
            response = dynamo_client.list_tables()
            #if does not contain ddb_table_carts, then create table
            if ddb_table_carts not in response['TableNames']  :
                create_table(
                    ddb_table_name=ddb_table_carts,
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
                            "KeySchema": [{"AttributeName": "username", "KeyType": "HASH"}],
                            "Projection": {"ProjectionType": "ALL"},
                            "ProvisionedThroughput": {
                                "ReadCapacityUnits": 5,
                                "WriteCapacityUnits": 5,
                            }
                        }
                    ]
                )
                enable_ttl_on_table(dynamo_client, ddb_table_carts, ttl_attribute='ttl')
            app.logger.info("DynamoDB local is responding!")
            return
        except Exception as e:
            app.logger.info(e)
            app.logger.info("Local DynamoDB service is not ready yet... pausing before trying again")
            time.sleep(2)
    app.logger.error("Local DynamoDB service not responding; verify that your docker-compose .env file is setup correctly")
    exit(1)

def setup():
    global dynamo_client, running_local

    if ddb_endpoint_override:
        running_local = True
        app.logger.info("Creating DDB client with endpoint override: " + ddb_endpoint_override)
        dynamo_client = boto3.client(
            'dynamodb',
            endpoint_url=ddb_endpoint_override,
            region_name='us-west-2',
            aws_access_key_id='XXXX',
            aws_secret_access_key='XXXX'
        )
        verify_local_ddb_running(ddb_endpoint_override, dynamo_client)
    else:
        running_local = False
        dynamo_client = boto3.client('dynamodb')

setup()
