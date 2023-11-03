# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import os
import time
import boto3

from server import app
import yaml
from decimal import Decimal

# DynamoDB table names passed via environment
ddb_table_products = os.getenv("DDB_TABLE_PRODUCTS")
ddb_table_categories = os.getenv("DDB_TABLE_CATEGORIES")
products_file = "dynamo-data/products.yaml"
categories_file = "dynamo-data/categories.yaml"

def create_table(resource, ddb_table_name, attribute_definitions, key_schema, global_secondary_indexes=None):
    try: 
        resource.create_table(
            TableName=ddb_table_name,
            KeySchema=key_schema,
            AttributeDefinitions=attribute_definitions,
            GlobalSecondaryIndexes=global_secondary_indexes or [],
            BillingMode="PAY_PER_REQUEST",
        )
        app.logger.info(f'Created table: {ddb_table_name}')
    except Exception as e:
        if e.response["Error"]["Code"] == "ResourceInUseException":
            app.logger.info(f'Table {ddb_table_name} already exists; continuing...')
        else:
            raise e

def verify_local_ddb_running(endpoint, dynamo_resource):
    app.logger.info(f"Verifying that local DynamoDB is running at: {endpoint}")
    for _ in range(5):
        try:
            response = dynamo_resource.meta.client.list_tables()
            if ddb_table_products not in response['TableNames']:
                try:
                    create_table(
                        ddb_table_name=ddb_table_products,
                        resource=dynamo_resource,
                        attribute_definitions=[
                            {"AttributeName": "id", "AttributeType": "S"},
                            {"AttributeName": "category", "AttributeType": "S"},
                            {"AttributeName": "featured", "AttributeType": "S"},
                        ],
                        key_schema=[
                            {"AttributeName": "id", "KeyType": "HASH"},
                        ],
                        global_secondary_indexes=[
                            {
                                "IndexName": "category-index",
                                "KeySchema": [{"AttributeName": "category", "KeyType": "HASH"}],
                                "Projection": {"ProjectionType": "ALL"},
                                "ProvisionedThroughput": {
                                    "ReadCapacityUnits": 5,
                                    "WriteCapacityUnits": 5,
                                }
                            },
                            {
                                "IndexName": "featured-index",
                                "KeySchema": [{"AttributeName": "featured", "KeyType": "HASH"}],
                                "Projection": {"ProjectionType": "ALL"},
                                "ProvisionedThroughput": {
                                    "ReadCapacityUnits": 5,
                                    "WriteCapacityUnits": 5,
                                }
                            }
                        ]
                    )
                    table = dynamo_resource.Table(ddb_table_products)
                    app.logger.info(f'Loading products from {products_file}')
                    with open(products_file, 'r') as f:
                        products = yaml.safe_load(f)
                    app.logger.info(f'Updating products in table {ddb_table_products}')
                    for product in products:
                        product['id'] = str(product['id'])
                        if product.get('price'):
                            product['price'] = Decimal(str(product['price']))
                        if product.get('featured'):
                            product['featured'] = str(product['featured']).lower()
                        table.put_item(Item=product)
                        
                    table.load()
                    app.logger.info(f"Table Name: {table.table_name}")
                    app.logger.info(f"Key Schema: {table.key_schema}")
                    app.logger.info(f"Attribute Definitions: {table.attribute_definitions}")
                    app.logger.info(f"Provisioned Throughput: {table.provisioned_throughput}")
                    app.logger.info(f"Global Secondary Indexes: {getattr(table, 'global_secondary_indexes', 'None')}")
                    app.logger.info(f"Local Secondary Indexes: {getattr(table, 'local_secondary_indexes', 'None')}")
                    app.logger.info(f"Table Status: {table.table_status}")
                    app.logger.info(f"Item Count: {table.item_count}")
                    app.logger.info(f"Table Size (Bytes): {table.table_size_bytes}")
                    app.logger.info(f"Creation Date Time: {table.creation_date_time.isoformat()}")

                    app.logger.info(f'Products loaded: {len(products)}')
                except Exception as e:
                    app.logger.error(f"Failed to initialize product table: {str(e)}")
                    exit(1)
            if ddb_table_categories not in response['TableNames']:
                try:
                    create_table(
                        resource=dynamo_resource,
                        ddb_table_name=ddb_table_categories,
                        attribute_definitions=[
                            {"AttributeName": "id", "AttributeType": "S"},
                            {"AttributeName": "name", "AttributeType": "S"},
                        ],
                        key_schema=[
                            {"AttributeName": "id", "KeyType": "HASH"},
                        ],
                        global_secondary_indexes=[
                            {
                                "IndexName": "name-index",
                                "KeySchema": [{"AttributeName": "name", "KeyType": "HASH"}],
                                "Projection": {"ProjectionType": "ALL"},
                                "ProvisionedThroughput": {
                                    "ReadCapacityUnits": 5,
                                    "WriteCapacityUnits": 5,
                                }
                            }
                        ]
                    )
                    table = dynamo_resource.Table(ddb_table_categories)
                    app.logger.info(f'Loading categories from {categories_file}')
                    with open(categories_file, 'r') as f:
                        categories = yaml.safe_load(f)
                    app.logger.info(f'Updating categories in table {ddb_table_categories}')
                    for category in categories:
                        category['id'] = str(category['id'])
                        table.put_item(Item=category)
                    table.load()
                    app.logger.info(f"Table Name: {table.table_name}")
                    app.logger.info(f"Key Schema: {table.key_schema}")
                    app.logger.info(f"Attribute Definitions: {table.attribute_definitions}")
                    app.logger.info(f"Provisioned Throughput: {table.provisioned_throughput}")
                    app.logger.info(f"Global Secondary Indexes: {getattr(table, 'global_secondary_indexes', 'None')}")
                    app.logger.info(f"Local Secondary Indexes: {getattr(table, 'local_secondary_indexes', 'None')}")
                    app.logger.info(f"Table Status: {table.table_status}")
                    app.logger.info(f"Item Count: {table.item_count}")
                    app.logger.info(f"Table Size (Bytes): {table.table_size_bytes}")
                    app.logger.info(f"Creation Date Time: {table.creation_date_time.isoformat()}")

                    app.logger.info(f'Categories loaded: {len(categories)}')
                except Exception as e:
                    app.logger.error(f"Failed to initialize category table: {str(e)}")
                    exit(1)
            app.logger.info("DynamoDB local is responding!")
            return
        except Exception as e:
            app.logger.info(e)
            app.logger.info("Local DynamoDB service is not ready yet... pausing before trying again")
            time.sleep(2)
    app.logger.info("Local DynamoDB service not responding; verify that your docker-compose .env file is set up correctly")
    exit(1)

ddb_endpoint_override = os.getenv("DDB_ENDPOINT_OVERRIDE")
running_local = False
dynamo_resource = None

def setup():
    global dynamo_resource, running_local

    if ddb_endpoint_override:
        running_local = True
        app.logger.info("Creating DDB client with endpoint override: " + ddb_endpoint_override)
        dynamo_resource = boto3.resource(
            'dynamodb',
            endpoint_url=ddb_endpoint_override,
            region_name='us-west-2',
            aws_access_key_id='XXXX',
            aws_secret_access_key='XXXX'
        )
        verify_local_ddb_running(ddb_endpoint_override, dynamo_resource)
    else:
        running_local = False
        dynamo_client = boto3.client('dynamodb')

setup()
