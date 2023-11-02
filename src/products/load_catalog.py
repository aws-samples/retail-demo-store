# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

'''
Utility script that can be run locally to load/reload the catalog in DynamoDB tables.
This script can update either the categories table, products table, or both. Each table
can also be truncated before loading data when you want to completely replace the table's
contents.

By default the script will load categories and products from the default location in the
repo. That is, the corresponding YAML files in the src/products-service/data/ directory.
You can override the file location on the command-line.

Usage:

python load_catalog.py --categories-table-name CATEGORIES_TABLE_NAME [--categories-file CATEGORIES_FILE] --products-table-name PRODUCTS_TABLE_NAME [--products_file PRODUCTS_FILE] [--truncate] --carts-table-name CARTS_TABLE_NAME [--carts_file CARTS_FILE] --endpoint-url ENDPOINT_URL] --endpoint-url ENDPOINT_URL

Where:
CATEGORIES_TABLE_NAME is the DynamoDB table name for categories
CATEGORIES_FILE is the location on your local machine where the categories.yaml is located (defaults to src/products-service/data/categories.yaml)
PRODUCTS_TABLE_NAME is the DynamoDB table name for products
PRODUCTS_FILE is the location on your local machine where the products.yaml is located (defaults to src/products-service/data/products.yaml)
CARTS_TABLE_NAME is the DynamoDB table name for carts
CARTS_FILE is the location on your local machine where the carts.yaml is located (defaults to src/products-service/data/carts.yaml)
truncate is a flag that will truncate the table before loading data (defaults to False)
endpoint-url is the endpoint URL for the DynamoDB service (defaults to 'http://localhost:3001')

Examples:

The script will only truncate (optional) and load the table(s) specified.

Your AWS credentials are discovered from your current environment.
'''

import sys
import getopt
import time
import yaml
from boto3 import resource
from decimal import Decimal
from botocore.exceptions import ClientError



def truncate_table(table):
    print('Truncating table...')
    #get the table keys
    tableKeyNames = [key.get("AttributeName") for key in table.key_schema]

    #Only retrieve the keys for each item in the table (minimize data transfer)
    projectionExpression = ", ".join('#' + key for key in tableKeyNames)
    expressionAttrNames = {'#'+key: key for key in tableKeyNames}

    counter = 0
    page = table.scan(ProjectionExpression=projectionExpression, ExpressionAttributeNames=expressionAttrNames)
    with table.batch_writer() as batch:
        while page["Count"] > 0:
            counter += page["Count"]
            # Delete items in batches
            for itemKeys in page["Items"]:
                batch.delete_item(Key=itemKeys)
            # Fetch the next page
            if 'LastEvaluatedKey' in page:
                page = table.scan(
                    ProjectionExpression=projectionExpression, ExpressionAttributeNames=expressionAttrNames,
                    ExclusiveStartKey=page['LastEvaluatedKey'])
            else:
                break
    print(f"Deleted {counter} items")
    
def  create_table(resource, ddb_table_name, attribute_definitions, key_schema, global_secondary_indexes=None):
    try: 
        resource.create_table(
            TableName=ddb_table_name,
            KeySchema=key_schema,
            AttributeDefinitions=attribute_definitions,
            GlobalSecondaryIndexes=global_secondary_indexes or [],
            BillingMode="PAY_PER_REQUEST",
        )
        print(f'Created table: {ddb_table_name}')
    except ClientError  as e:
        if e.response["Error"]["Code"] == "ResourceInUseException":
            print(f'Table {ddb_table_name} already exists; continuing...')
        else:
            raise e
        
def enable_ttl_on_table(resource, table_name, ttl_attribute):
    try:
        response = resource.meta.client.update_time_to_live(
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
    except ClientError as e:
        print(f'Error enabling TTL: {e}')
        
def verify_local_ddb_running(endpoint,dynamodb):
    print(f"Verifying that local DynamoDB is running at: {endpoint}")
    for _ in range(5):
        try:
            dynamodb.tables.all()
            print("DynamoDB local is responding!")
            return
        except Exception:
            print("Local DynamoDB service is not ready yet... pausing before trying again")
            time.sleep(2)
    print("Local DynamoDB service not responding; verify that your docker-compose .env file is setup correctly")
    exit(1)

if __name__=="__main__":
    categories_table_name = None
    categories_file = 'src/products-service/data/categories.yaml'
    products_table_name = None
    products_file = 'src/products-service/data/products.yaml'
    carts_table_name = None
    carts_file = 'src/products-service/data/carts.yaml'
    truncate = False
    endpoint_url = 'http://localhost:3001'

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'h', ['categories-table-name=', 'categories-file=', 'products-table-name=', 'products-file=', 'truncate', 'endpoint-url=', 'carts-table-name=', 'carts-file='])
    except getopt.GetoptError:
        print(f'Usage: {sys.argv[0]} --categories-table-name CATEGORIES_TABLE_NAME [--categories-file CATEGORIES_FILE] --products-table-name PRODUCTS_TABLE_NAME [--products_file PRODUCTS_FILE] [--truncate] --carts-table-name CARTS_TABLE_NAME [--carts_file CARTS_FILE] [--endpoint-url ENDPOINT_URL]')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print(f'Usage: {sys.argv[0]} --categories-table-name CATEGORIES_TABLE_NAME [--categories-file CATEGORIES_FILE] --products-table-name PRODUCTS_TABLE_NAME [--products_file PRODUCTS_FILE] [--truncate] --carts-table-name CARTS_TABLE_NAME [--carts_file CARTS_FILE] [--endpoint-url ENDPOINT_URL]')
            sys.exit()
        elif opt in ('--categories-table-name'):
            categories_table_name = arg
        elif opt in ('-categories-file-name'):
            categories_file = arg
        elif opt in ('--products-table-name'):
            products_table_name = arg
        elif opt in ('--products-file-name'):
            products_file = arg
        elif opt in ('--truncate'):
            truncate = True
        elif opt in ('--endpoint-url'):
            endpoint_url = arg
            print(f'Using endpoint_url: {endpoint_url}')
        elif opt in ('--carts-table-name'):
            carts_table_name = arg
        elif opt in ('--carts-file-name'):
            carts_file = arg

    if (not categories_table_name and not products_table_name and not carts_table_name):
        print('"--categories-table-name and/or --products-table-name and/or carts_table_name" are required')
        print(f'Usage: {sys.argv[0]} --categories-table-name CATEGORIES_TABLE_NAME [--categories-file CATEGORIES_FILE] --products-table-name PRODUCTS_TABLE_NAME [--products_file PRODUCTS_FILE] [--truncate] --carts-table-name CARTS_TABLE_NAME [--carts_file CARTS_FILE] [--endpoint-url ENDPOINT_URL]')
        sys.exit(1)

    dynamodb = resource('dynamodb', endpoint_url=endpoint_url)

    if categories_table_name:
        print(f'Loading categories from {categories_file} into table {categories_table_name}')
       
        create_table(
            ddb_table_name=categories_table_name,
            resource=dynamodb,
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
        table = dynamodb.Table(categories_table_name)
        
        if truncate:
            truncate_table(table)

        print(f'Loading categories from {categories_file}')
        with open(categories_file, 'r') as f:
            categories = yaml.safe_load(f)

        print(f'Updating categories in table {categories_table_name}')
        for category in categories:
            category['id'] = str(category['id'])
            table.put_item(Item=category)

        print(f'Categories loaded: {len(categories)}')

    if products_table_name:
        print(f'Loading products from {products_file} into table {products_table_name}')
        
        create_table(
            ddb_table_name=products_table_name,
            resource=dynamodb,
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
        
        table = dynamodb.Table(products_table_name)
        
        if truncate:
            truncate_table(table)

        print(f'Loading products from {products_file}')
        with open(products_file, 'r') as f:
            products = yaml.safe_load(f)

        print(f'Updating products in table {products_table_name}')
        for product in products:
            if product.get('price'):
                product['price'] = Decimal(str(product['price']))
            if product.get('featured'):
                product['featured'] = str(product['featured']).lower()
            table.put_item(Item=product)

        print(f'Products loaded: {len(products)}')
        
    if carts_table_name:
        print(f'Creating carts table {carts_table_name}')
            
        create_table(
            ddb_table_name=carts_table_name,
            resource=dynamodb,
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
        
        enable_ttl_on_table(dynamodb, carts_table_name, ttl_attribute='ttl')