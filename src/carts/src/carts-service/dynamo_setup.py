# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import os
import time
import boto3
import requests
import json
from server import app




# DynamoDB table names passed via environment
ddb_table_carts = os.getenv("DDB_TABLE_CARTS")

# Allow DDB endpoint to be overridden to support amazon/dynamodb-local
ddb_endpoint_override = os.getenv("DDB_ENDPOINT_OVERRIDE")
running_local = False

dynamo_client = None

def verify_local_ddb_running(endpoint,dynamo_client):
    app.logger.info(f"Verifying that local DynamoDB is running at: {endpoint}")
    for _ in range(5):
        try:
            dynamo_client.list_tables()
            app.logger.info("DynamoDB local is responding!")
            return
        except Exception as e:
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
            region_name='us-west-2'
        )
        verify_local_ddb_running(ddb_endpoint_override,dynamo_client)
    else:
        running_local = False
        try:
            response = requests.get("http://169.254.170.2/v2/metadata", timeout=1)
            metadata = json.loads(response.text)
            region = metadata['AvailabilityZone'][:-1]
        except Exception as e:
            app.logger.warning("Could not fetch ECS metadata, defaulting region to 'us-east-1'")
            region = 'us-east-1'
        dynamo_client = boto3.client('dynamodb', region_name=region)

setup()