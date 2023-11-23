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

class DynamoBase(ABC):
    def __init__(self, resource, table_name):
        self.resource = resource
        self.table = resource.Table(table_name)
        
    def get(self, id: str):
        try:
            response = self.table.get_item(Key={'id': id })
        except ClientError as err:
            current_app.logger.error(f"Couldn't get get from table {self.table.name}: {err.response['Error']['Code']} {err.response['Error']['Message']}")
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
    pass