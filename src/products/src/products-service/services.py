import os
from server import app
from boto3.dynamodb.types import TypeSerializer, TypeDeserializer
from uuid import uuid4
from dynamo_setup import ddb_table_categories, ddb_table_products, dynamo_resource

class ProductService:
    
    dynamo_client = dynamo_resource.meta.client
    ddb_table_products = ddb_table_products
    ddb_table_categories = ddb_table_categories
    MAX_BATCH_GET_ITEM = 100
    web_root_url = os.getenv("WEB_ROOT_URL")
    serializer = TypeSerializer()
    deserializer = TypeDeserializer()
    ALLOWED_PRODUCT_KEYS = {
        'id', 'url', 'sk', 'name', 'category', 'style', 'description', 'aliases',
        'price', 'image', 'featured', 'gender_affinity', 'current_stock', 'promoted'
        }
        
    
    def validate_product(self,product):
        invalid_keys = set(product.keys()) - self.ALLOWED_PRODUCT_KEYS
        if invalid_keys:
            raise ValueError(f'Invalid keys: {invalid_keys}')
        category = self.get_category_by_name(product['category'])
        if not category:
            raise ValueError(f'Category {product["category"]} not found')
        product['price'] = str(product['price'])
        product['current_stock'] = str(product['current_stock'])
    
    @staticmethod
    def get_product_template():
        return {
            'id': str(uuid4()),
            'aliases': []
        }

    @staticmethod
    def update_product_template(product):
        if 'aliases' not in product or not product['aliases']:
            product['aliases'] = []
        if 'sk' not in product or product['sk'] is None:
            product['sk'] = ''
        product['current_stock'] = int(product['current_stock'])
        product['price'] = float(product['price'])
        if 'promoted' in product:
            product['promoted'] = str(product['promoted'])
        return product
        
    @staticmethod
    def execute_and_log(func, success_message, error_message, **kwargs):
        try:
            app.logger.info('Executing operation')
            response = func(**kwargs)
            app.logger.info(success_message)
            return response
        except Exception as e:
            app.logger.error(f'Execution error, {error_message}: {str(e)}')
            raise
    
    def set_product_url(self, product):
        if self.web_root_url:
            product["url"] = f"{self.web_root_url}/#/product/{product['id']}"
            
    def set_category_url(self, category):
        if self.web_root_url:
            category["url"] = f"{self.web_root_url}/#/category/{category['id']}"
            
    def get_product_by_id(self, product_id):
        product_id = str(product_id.lower())
        app.logger.info(f'Finding product with id: {product_id}, {self.ddb_table_products}')
        response = self.execute_and_log(
            self.dynamo_client.get_item,
            f'Retrieved product with id: {product_id}',
            f'Error retrieving product with id: {product_id}',
            TableName=self.ddb_table_products,
            Key={
                'id': product_id
            }
        )
        if 'Item' in response:
            app.logger.info(f'Retrieved product: {response["Item"]}')
            product = response['Item']
            self.set_product_url(product)
            self.update_product_template(product)
            app.logger.info(f"Found product: {product}, category: {product['category']}")
            return product
        else:
            raise KeyError
        
    def get_products_by_ids(self, product_ids):
        if len(product_ids) > self.MAX_BATCH_GET_ITEM:
            raise Exception("Cannot query more than 100 items at a time")
        
        app.logger.info(f"Finding products with ids: {product_ids}, {self.ddb_table_products}")
        
        request_items = {
            self.ddb_table_products: {
                'Keys': [{'id': product_id} for product_id in product_ids]
            }
        }
        response = self.execute_and_log(
            self.dynamo_client.batch_get_item,
            f'Retrieved products with ids: {product_ids}',
            f'Error retrieving products with ids: {product_ids}',
            RequestItems=request_items
        )
        products = response['Items']
        return products
    
    def get_category_by_id(self, category_id):
        category_id = category_id.lower()
        app.logger.info(f"Finding category with id: {category_id}, {self.ddb_table_categories}")
        response = self.execute_and_log(
            self.dynamo_client.get_item,
            f'Retrieved category with id: {category_id}',
            f'Error retrieving category with id: {category_id}',
            TableName=self.ddb_table_categories,
            Key={'id': category_id}
        )
        if 'Item' in response:
            category = response['Item']
            self.set_category_url(category)
            app.logger.info(f"Found category: {category}")
            return category
        else:
            raise KeyError
        
    def get_category_by_name(self, category_name):
        app.logger.info(f"Finding category with name: {category_name}, {self.ddb_table_categories}")
        response = self.execute_and_log(
            self.dynamo_client.query,
            f'Retrieved category with name: {category_name}',
            f'Error retrieving category with name: {category_name}',
            TableName=self.ddb_table_categories,
            IndexName='name-index',
            ExpressionAttributeValues= {
                ':category_name': category_name
            },
            KeyConditionExpression='#n = :category_name',
            ExpressionAttributeNames={'#n': 'name'},
            ProjectionExpression='id, #n, image'
        )
        if 'Items' in response:
            category = response['Items'][0]
            self.set_category_url(category)
            app.logger.info(f"Found category: {category}")
            return category
        else:
            raise KeyError
        
    def get_product_by_category(self, category):
        app.logger.info(f"Finding products by category: {category}, {self.ddb_table_products}")
        
        response = self.execute_and_log(
            self.dynamo_client.query,
            f'Retrieved products by category: {category}',
            f'Error retrieving products by category: {category}',
            TableName=self.ddb_table_products,
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
        if 'Items' in response:
            products = response['Items']
            for product in products:
                self.set_product_url(product)
                self.update_product_template(product)
            app.logger.info(f"Found products: {products}")
            return products
        
    def get_featured_products(self):
        app.logger.info(f"Finding featured products, {self.ddb_table_products} | featured=true")
        
        
        response = self.execute_and_log(
            self.dynamo_client.query,
            'Retrieved featured products',
            'Error retrieving featured products',
            TableName=self.ddb_table_products,
            IndexName='featured-index',
            ExpressionAttributeValues= {
                ':featured': 'true'
            },
            KeyConditionExpression='featured = :featured',
            ProjectionExpression='id, category, #n, image, #s, description, price, gender_affinity, current_stock, promoted',
            ExpressionAttributeNames={
                '#n': 'name',
                '#s': 'style'
            }
        )
        if 'Items' in response:
            products = response['Items']
            for product in products:
                self.set_product_url(product)
                self.update_product_template(product)
                product['featured'] = 'true'
                app.logger.info(f"Found featured product: {product}")
            return products
        
    def get_all_categories(self):
        app.logger.info(f"Finding all categories, {self.ddb_table_categories}")
        
        response = self.execute_and_log(
            self.dynamo_client.scan,
            'Retrieved all categories',
            'Error retrieving all categories',
            TableName=self.ddb_table_categories
        )
        if 'Items' in response:
            app.logger.info(f"Found {len(response['Items'])} categories")
            categories = response['Items']
            for category in categories:
                self.set_category_url(category)
            return categories
    
    def get_all_products(self):
        app.logger.info(f"Finding all products, {self.ddb_table_products}")
        
        response = self.execute_and_log(
            self.dynamo_client.scan,
            'Retrieved all products',
            'Error retrieving all products',
            TableName=self.ddb_table_products
        )
        if 'Items' in response:
            app.logger.info(f"Found {len(response['Items'])} products")
            products = response['Items']
            for product in response['Items']:
                self.set_product_url(product)
                self.update_product_template(product)
            app.logger.info(f"Found products: {products[0:2]}")
            return products
        
    def update_product(self, original_product, updated_product):
        updated_product['id'] = original_product['id']
        self.set_product_url(updated_product)
        self.validate_product(updated_product)
        app.logger.info(f"Updating product: {original_product} to {updated_product}")
        self.execute_and_log(
            self.dynamo_client.put_item,
            f'Updated product: {updated_product}',
            f'Error updating product: {updated_product}',
            TableName=self.ddb_table_products,
            Item=updated_product
        )
        
    def update_inventory_delta(self, product, stock_delta):
        app.logger.info(f"Updating inventory delta for product: {product['name']}")
        
        if product['current_stock'] + stock_delta < 0:
            stock_delta = -product['current_stock']
            
        params = {
            'TableName': ddb_table_products,
            'Key': {
                'id': product['id'],
                'category': product['category']
            },
            'ExpressionAttributeValues': {
                ':stock_delta': str(stock_delta),
                ':current_stock': str(product['current_stock'])
            },
            'UpdateExpression': 'SET current_stock = current_stock + :stock_delta',
            'ConditionExpression': 'current_stock + :stock_delta >= 0',
            'ReturnValues': 'UPDATED_NEW'      
        }
        
        self.execute_and_log(
            self.dynamo_client.update_item,
            f'Updated product: {product}',
            f'Error updating product: {product}',
            **params)
        
        product['current_stock'] += stock_delta
        
    def add_product(self, product):
        product_temp = self.get_product_template()
        product.update(product_temp)
        self.set_product_url(product)
        self.validate_product(product)
        app.logger.info(f"Adding product: {product}")
        self.execute_and_log(
            self.dynamo_client.put_item,
            f'Added product: {product}',
            f'Error adding product: {product}',
            TableName=self.ddb_table_products,
            Item=product
        )
        
    def delete_product(self, product):
        app.logger.info(f"Deleting product: {product['name']}")
        
        self.execute_and_log(
            self.dynamo_client.delete_item,
            f'Deleted product: {product}',
            f'Error deleting product: {product}',
            TableName=self.ddb_table_products,
            Key={'id': product['id'], 'category': product['category']}
        )