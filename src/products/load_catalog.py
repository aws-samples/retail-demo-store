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

python load_catalog.py --categories-table-name CATEGORIES_TABLE_NAME [--categories-file CATEGORIES_FILE] --products-table-name PRODUCTS_TABLE_NAME [--products_file PRODUCTS_FILE] [--truncate]

Where:
CATEGORIES_TABLE_NAME is the DynamoDB table name for categories
CATEGORIES_FILE is the location on your local machine where the categories.yaml is located (defaults to src/products-service/data/categories.yaml)
PRODUCTS_TABLE_NAME is the DynamoDB table name for products
PRODUCTS_FILE is the location on your local machine where the products.yaml is located (defaults to src/products-service/data/products.yaml)

The script will only truncate (optional) and load the table(s) specified.

Your AWS credentials are discovered from your current environment.
'''

import sys
import getopt
import yaml
import boto3
from decimal import Decimal

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

if __name__=="__main__":
    categories_table_name = None
    categories_file = 'src/products-service/data/categories.yaml'
    products_table_name = None
    products_file = 'src/products-service/data/products.yaml'
    truncate = False

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'h', ['categories-table-name=', 'categories-file=', 'products-table-name=', 'products-file=', 'truncate'])
    except getopt.GetoptError:
        print(f'Usage: {sys.argv[0]} --categories-table-name CATEGORIES_TABLE_NAME [--categories-file CATEGORIES_FILE] --products-table-name PRODUCTS_TABLE_NAME [--products_file PRODUCTS_FILE] [--truncate]')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print(f'Usage: {sys.argv[0]} --categories-table-name CATEGORIES_TABLE_NAME [--categories-file CATEGORIES_FILE] --products-table-name PRODUCTS_TABLE_NAME [--products_file PRODUCTS_FILE] [--truncate]')
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

    if not categories_table_name and not products_table_name:
        print('--categories-table-name and/or --products-table-name are required')
        print(f'Usage: {sys.argv[0]} --categories-table-name CATEGORIES_TABLE_NAME [--categories-file CATEGORIES_FILE] --products-table-name PRODUCTS_TABLE_NAME [--products_file PRODUCTS_FILE] [--truncate]')
        sys.exit(1)

    dynamodb = boto3.resource('dynamodb')

    if categories_table_name:
        print(f'Loading categories from {categories_file} into table {categories_table_name}')
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