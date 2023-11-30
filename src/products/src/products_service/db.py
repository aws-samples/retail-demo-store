# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import boto3
from botocore.exceptions import ClientError
from flask import Flask, current_app
from abc import ABC

class DynamoDB():
    
    def __init__(self, app: Flask | None = None) -> None:
        if app is not None:
            self.init_app(app)
        self.product = None
        self.categories = None
        self.personalised_products = None

    def init_app(self, app: Flask) -> None:
        if app.config.get('DDB_ENDPOINT_OVERRIDE'):
            app.logger.info(f"DynamoDB endpoint: {app.config.get('DDB_ENDPOINT_OVERRIDE')}")
            resource = boto3.resource(
                'dynamodb',
                endpoint_url=app.config.get('DDB_ENDPOINT_OVERRIDE'),
                aws_access_key_id='XXXX',
                aws_secret_access_key='XXXX'
            )            
        else:
            resource = boto3.resource('dynamodb')
        
        self.products = Products(resource, app.config["DDB_TABLE_PRODUCTS"])
        self.categories = Categories(resource, app.config["DDB_TABLE_CATEGORIES"])
        self.personalised_products = PersonalisedProducts(resource, app.config['DDB_TABLE_PERSONALISED_PRODUCTS'])
        self.resource = resource

    def init_tables(self):
        entities = [self.products, self.categories, self.personalised_products]
        for entity in entities:
            if not entity.table_exists():
                current_app.logger.info(f"Creating table: {entity.table.name}")
                entity.create_table()


class DynamoBase(ABC):
    def __init__(self, resource, table_name):
        self.resource = resource
        self.table = resource.Table(table_name)
    
    def table_exists(self):
        try:
            current_app.logger.info(f"Checking for existence of table {self.table.name}")
            self.table.load()
        except ClientError as err:
            if err.response["Error"]["Code"] == "ResourceNotFoundException":
                current_app.logger.info(f"Table: {self.table.name} not found")
                return False
            else:
                current_app.logger.error(
                    "Couldn't check for existence of {self.table.name}. Here's why: {err.response['Error']['Code']}: {err.response['Error']['Message']}"
                )
                raise
        else:
            current_app.logger.info(f"Table: {self.table.name} already exists")
            return True
    
    def create_table(self):
        pass

    def _create_table(self, attribute_definitions, key_schema, global_secondary_indexes=None):
        
        try: 
            kargs = {
                "GlobalSecondaryIndexes": global_secondary_indexes
            } if global_secondary_indexes else {}

            self.resource.create_table(
                TableName=self.table.name,
                KeySchema=key_schema,
                AttributeDefinitions=attribute_definitions,
                BillingMode="PAY_PER_REQUEST",
                **kargs
            )
            self.table.wait_until_exists()
            current_app.logger.info(f'Created table: {self.table.name}')
        except ClientError  as e:
            if e.response["Error"]["Code"] == "ResourceInUseException":
                print(f'Table {self.table.name} already exists; continuing...')
            else:
                raise
        return self.table
        
    def get(self, id: str):
        try:
            response = self.table.get_item(Key={'id': id })
        except ClientError as err:
            current_app.logger.error(f"Couldn't get from table {self.table.name}: {err.response['Error']['Code']} {err.response['Error']['Message']}")
            raise
        else:
            return response.get("Item")
    
    def gets(self, ids: list):
        try:
            response = self.resource.batch_get_item(
                RequestItems={
                    self.table.name: {
                        'Keys': [{'id': id} for id in ids]
                    }
                }   
            )
        except ClientError as err:
            current_app.logger.error(f"Couldn't get from table {self.table.name}: {err.response['Error']['Code']} {err.response['Error']['Message']}")
            raise
        else:
            return response['Responses'][self.table.name]
    
    def get_all(self):
        response = self.table.scan()
        return response['Items'] if 'Items' in response else []

    def upsert(self, item):
        self.table.put_item(Item=item)

    def delete(self, id):
        self.table.delete_item(
            Key={
                'id': id
            }
        )
    

class Products(DynamoBase):

    def create_table(self):
        self._create_table(
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
    
    def get_featured(self):
        try: 
            response = self.table.query(
                IndexName='featured-index',
                ExpressionAttributeValues={
                    ':featured': 'true'
                },
                KeyConditionExpression='featured = :featured',
                ProjectionExpression='id, category, #n, image, #s, description, price, gender_affinity, current_stock, promoted',
                ExpressionAttributeNames={
                    '#n': 'name',
                    '#s': 'style'
                }
            )
        except ClientError as err:
            current_app.logger.error(f"Couldn't get products from table {self.table.name}: {err.response['Error']['Code']} {err.response['Error']['Message']}")
            raise
        else:
            return response['Items'] if 'Items' in response else []

    def get_by_category(self, category):
        response = self.table.query(
            IndexName='category-index',
            ExpressionAttributeValues= {
                ':category': category
            },
            KeyConditionExpression='category = :category',
            ProjectionExpression='id, category, #n, image, #s, description, price, gender_affinity, current_stock, promoted',
            ExpressionAttributeNames={
                '#n': 'name',
                '#s': 'style'
            }
        )
        return response['Items'] if 'Items' in response else []

    def update_inventory(self, id, current_stock, stock_delta):
        self.table.update_item(
            Key={
                'id': id
            },
            ExpressionAttributeValues={
                ':stock_delta': stock_delta,
                ':current_stock': current_stock
            },
            UpdateExpression='SET current_stock = current_stock + :stock_delta',
            ConditionExpression='current_stock = :current_stock',
            ReturnValues='UPDATED_NEW'
        )

class Categories(DynamoBase):

    def create_table(self):
        self._create_table(
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
    
    def get_by_name(self, category_name):
        response = self.table.query(
            IndexName='name-index',
            ExpressionAttributeValues= {
                ':category_name': category_name
            },
            KeyConditionExpression='#n = :category_name',
            ExpressionAttributeNames={'#n': 'name'},
            ProjectionExpression='id, #n, image'
        )
        return response['Items'][0] if 'Items' in response else None

class PersonalisedProducts(DynamoBase):
    
    def create_table(self):
        self._create_table(
            attribute_definitions=[
                {"AttributeName": "id", "AttributeType": "S"},
            ],
            key_schema=[
                {"AttributeName": "id", "KeyType": "HASH"},
            ]
        )