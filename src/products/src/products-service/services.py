# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from server import app
import os
from botocore.exceptions import ClientError
from boto3.dynamodb.types import TypeDeserializer,TypeSerializer
from uuid import uuid4
from dynamo_setup import dynamo_client, ddb_table_products, ddb_table_categories
import ast
from decimal import Decimal

class ProductService:
    
    def __init__(self):
        self.dynamo_client = dynamo_client
        self.ddb_table_products = ddb_table_products
        self.ddb_table_categories = ddb_table_categories
        self.MAX_BATCH_GET_ITEM = 100
        self.web_root_url = os.getenv("WEB_ROOT_URL")
        self.serializer = TypeSerializer()
        self.deserializer = TypeDeserializer()
        
    
        
    def set_product_url(self, product):
        if self.web_root_url:
            product["url"] = f"{self.web_root_url}/#/product/{product['id']}"
            
    def set_category_url(self, category):
        if self.web_root_url:
            category["url"] = f"{self.web_root_url}/#/category/{category['id']}"
            
            
    
    
    def unmarshal_items(self, dynamodb_items):
        
        
        def is_number_string(s):
            return isinstance(s, str) and s.replace('.', '', 1).isdigit()

        def is_string_list(s):
            return isinstance(s, str) and s.startswith("[") and s.endswith("]")
        
        def convert_decimal(v):
            if isinstance(v, Decimal):
                if v % 1 > 0:
                    return float(v)
                else:
                    return int(v)
            return v
        def convert_boolean(v):
            if isinstance(v, bool):
                return str(v)
            return v 
        return [
            {k: convert_decimal(ast.literal_eval(v)) if is_string_list(v)
             else convert_decimal(float(v)) if is_number_string(v)
             else convert_boolean(v) if isinstance(v, bool)
             else convert_decimal(v) 
             for k, v in {k: self.deserializer.deserialize(v) for k, v in item.items()}.items()}
            for item in dynamodb_items
        ]
        
    def marshal_item(self, data):
        app.logger.info(f"Marshalling item: {data}")
        return {
            k: {'S': str(v)}
            for item in data
            for k, v in item.items()
        }
    
    def unmarshal_items_categories(self, dynamodb_items):

        def is_string_list(s):
            return isinstance(s, str) and s.startswith("[") and s.endswith("]")

        def is_boolean_string(s):
            return isinstance(s, str) and s.lower() in ["true", "false"]

        return [
            {
                k: ast.literal_eval(v) if is_string_list(v)
                else True if is_boolean_string(v) and v.lower() == "true"
                else False if is_boolean_string(v) and v.lower() == "false"
                else v
                for k, v in {k: self.deserializer.deserialize(v) for k, v in item.items()}.items()
            }
            for item in dynamodb_items
        ]
    
    def product_fill(self, product):
        if 'sk' not in product or product['sk'] is None:
            product['sk'] = ""
        if 'aliases' not in product or product['aliases'] is None:
            product['aliases'] = []

    
    #find product by id
    def find_product(self, product_id):
        product_id = product_id.lower()
        app.logger.info(f"Finding product with id: {product_id}, {ddb_table_products}")
        
        try:
            response = self.dynamo_client.get_item(
                TableName=ddb_table_products,
                Key={
                    'id': {'S': product_id}
                }
            )
        except ClientError as e:
            app.logger.error(e.response['Error']['Message'])
            return None
        
        if 'Item' in response:
            #product = {k: float(v['S']) if 'S' in v and v['S'].replace('.', '', 1).isdigit() else v['S'] if 'S' in v else float(v['N']) if 'N' in v else v for k, v in response['Item'].items()}
            product = self.unmarshal_items([response['Item']])[0]
            self.set_product_url(product)
            self.product_fill(product)
            app.logger.info(f"Found product: {product}, category: {product['category']}")
            return product
    
    #find multiple products by id
    def find_products(self, product_ids):
        if len(product_ids) > self.MAX_BATCH_GET_ITEM:
            raise Exception("Cannot query more than 100 items at a time")
        
        app.logger.info(f"Finding products with ids: {product_ids}, {ddb_table_products}")
        
        request_items = {
            ddb_table_products: {
                'Keys': [{'id': {'S': product_id}} for product_id in product_ids]
            }
        }
        
        try:
            response = self.dynamo_client.batch_get_item(
                RequestItems=request_items
            )
        except ClientError as e:
            app.logger.error(e.response['Error']['Message'])
            return []
        
        products = []
        
        if 'Responses' in response:
            for item in response['Responses'][ddb_table_products]:
                #product = {k: float(v['S']) if 'S' in v and v['S'].replace('.', '', 1).isdigit() else v['S'] if 'S' in v else float(v['N']) if 'N' in v else v for k, v in item.items()}
                product = self.unmarshal_items([item])[0]
                self.set_product_url(product)
                self.product_fill(product)
                products.append(product)
        
        return products
    
    #find category by id
    def find_category(self, category_id):
        category_id = category_id.lower()
        app.logger.info(f"Finding category with id: {category_id}, {ddb_table_categories}")
        
        try:
            response = self.dynamo_client.get_item(
                TableName=ddb_table_categories,
                Key={
                    'id': {'S': category_id}
                }
            )
        except ClientError as e:
            app.logger.error(e.response['Error']['Message'])
            return None
        
        if 'Item' in response:
            #category = {k: v['S'] if 'S' in v else v['N'] if 'N' in v else v for k, v in response['Item'].items()}
            category = self.unmarshal_items_categories([response['Item']])[0]
            self.set_category_url(category)
            app.logger.info(f"Found category: {category['name']}")
            return category
        
    #find category by name
    def find_category_by_name(self, category_name):
        app.logger.info(f"Finding category with name: {category_name}, {ddb_table_categories}")
        
        try:
            response = self.dynamo_client.query(
                TableName=ddb_table_categories,
                IndexName='name-index',
                ExpressionAttributeValues= {
                    ':category_name': {'S': category_name}
                },
                KeyConditionExpression='#n = :category_name',
                ProjectionExpression='id, #n, image',
                ExpressionAttributeNames={
                    '#n': 'name'
                }
            )
        except ClientError as e:
            app.logger.error(e.response['Error']['Message'])
            return []
        
        categories = []
        
        if 'Items' in response:
            for item in response['Items']:
                #category = category = {k: v['S'] if 'S' in v else v['N'] if 'N' in v else v for k, v in item.items()}
                category = self.unmarshal_items_categories([item])[0]
                self.set_category_url(category)
                categories.append(category)
                
        return categories
    
    def find_product_by_category(self, category):
        app.logger.info(f"Finding products by category: {category}, {ddb_table_products}")
        
        try:
            response = self.dynamo_client.query(
                TableName=ddb_table_products,
                IndexName='category-index',
                ExpressionAttributeValues= {
                    ':category': {'S': category}
                    },
                KeyConditionExpression='category = :category',
                ProjectionExpression='id, category, #n, image, #s, description, price, gender_affinity, current_stock, promoted',
                ExpressionAttributeNames={
                    '#n': 'name',
                    '#s': 'style'
                }
            )
        except ClientError as e:
            app.logger.error(e.response['Error']['Message'])
            return []
        
        products = self.unmarshal_items(response['Items'])
        
        for product in products:
            self.set_product_url(product)
            self.product_fill(product)
            product['category'] = category
                
        return products
    
    #find featured products
    def find_featured_products(self):
        app.logger.info(f"Finding featured products, {ddb_table_products} | featured=true")
        
        try:
            response = self.dynamo_client.query(
                TableName=ddb_table_products,
                IndexName='featured-index',
                ExpressionAttributeValues= {
                    ':featured': {'S': 'true'}
                },
                KeyConditionExpression='featured = :featured',
                ProjectionExpression='id, category, #n, image, #s, description, price, gender_affinity, current_stock, promoted',
                ExpressionAttributeNames={
                    '#n': 'name',
                    '#s': 'style'
                }
            )
        except ClientError as e:
            app.logger.error(e.response['Error']['Message'])
            return []
        
        products = self.unmarshal_items(response['Items'])
        
        for product in products:
            self.set_product_url(product)
            self.product_fill(product)
            product['featured'] = 'true'
                
        return products
    
    #find all categories
    def find_all_categories(self):
        app.logger.info(f"Finding all categories, {ddb_table_categories}")
        
        try:
            response = self.dynamo_client.scan(
                TableName=ddb_table_categories
            )
            
        except ClientError as e:
            app.logger.error(e.response['Error']['Message'])
            return []
        
        app.logger.info(f"Found {len(response['Items'])} categories")
        
        categories  = self.unmarshal_items_categories(response['Items'])
        app.logger.info(f"Found {categories}")
        
        for category in categories:
            self.set_category_url(category)
            
        app.logger.info(f"Found {categories}")
        return categories
    
    #find all products
    def find_all_products(self):
        app.logger.info(f"Finding all products, {ddb_table_products}")
        
        try:
            response = self.dynamo_client.scan(
                TableName=ddb_table_products
            )
            
        except ClientError as e:
            app.logger.error(e.response['Error']['Message'])
            return []
        
        app.logger.info(f"Found {len(response['Items'])} products")
        
        products  = self.unmarshal_items(response['Items'])
        
        for product in products:
            self.set_product_url(product)
            self.product_fill(product)
            
        app.logger.info(f"Found {products}")    
        return products
    
    #update product
    def update_product(self, original_product, updated_product):
        app.logger.info(f"Updating product: {original_product} to {updated_product}")
        updated_product['id'] = original_product['id']
        self.set_product_url(updated_product)
        prep_for_marshal = []
        prep_for_marshal.append(updated_product)
        updated_product = self.marshal_item(prep_for_marshal)
        
        
        app.logger.info(f"Updating product: {original_product} to {updated_product}")
        
        try:
            self.dynamo_client.put_item(
                TableName=ddb_table_products,
                Item=updated_product
            )
        except ClientError as e:
            app.logger.error(e.response['Error']['Message'])
            return e
        
        
        return None
    
    #update inventory delta
    def update_inventory_delta(self, product, stock_delta):
        app.logger.info(f"Updating inventory delta for product: {product['name']}")
        
        if product['current_stock'] + stock_delta < 0:
            stock_delta = -product['current_stock']
            
        params = {
            'TableName': ddb_table_products,
            'Key': {
                'id': {'S': product['id']},
                'category': {'S': product['category']}
            },
            'ExpressionAttributeValues': {
                ':stock_delta': {'N': str(stock_delta)},
                ':current_stock': {'N': str(product['current_stock'])}
            },
            'UpdateExpression': 'SET current_stock = current_stock + :stock_delta',
            'ConditionExpression': 'current_stock + :stock_delta >= 0',
            'ReturnValues': 'UPDATED_NEW'      
        }
        
        try:
            self.dynamo_client.update_item(**params)
        except ClientError as e:
            app.logger.error(e.response['Error']['Message'])
            return e
        
        product['current_stock'] += stock_delta
        return None
    
    #add a new product
    def add_product(self, product):
        app.logger.info(f"Adding product: {product['name']}")
        
        if 'id' not in product or not product['id']:
            product['id'] = str(uuid4())
            
        if 'aliases' not in product or not product['aliases']:
            product['aliases'] = []
        self.set_product_url(product)   
        marshalled_product = self.marshal_item([product])
        try:
            self.dynamo_client.put_item(
                TableName=ddb_table_products,
                Item=marshalled_product
            )
        except ClientError as e:
            app.logger.error(e.response['Error']['Message'])
            return e
        return None
    
    #delete product
    def delete_product(self, product):
        app.logger.info(f"Deleting product: {product['name']}")
        
        try:
            self.dynamo_client.delete_item(
                TableName=ddb_table_products,
                Key={
                    'id': {'S': product['id']},
                    'category': {'S': product['category']}
                }
            )
        except ClientError as e:
            app.logger.error(e.response['Error']['Message'])
            return e
        
        return None

