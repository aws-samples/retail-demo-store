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
        'id', 'name', 'description', 'price', 'category', 'image', 'style',
        'gender_affinity', 'current_stock', 'promoted', 'featured', 'sk', 'aliases'
    }
    ALLOWED_CATEGORY_KEYS = {'id', 'name', 'image'}
        
    
    @staticmethod
    def validate_product(product):
        invalid_keys = set(product.keys()) - ProductService.ALLOWED_PRODUCT_KEYS
        if invalid_keys:
            raise ValueError(f'Invalid keys: {invalid_keys}')
        
    @staticmethod
    def validate_category(category):
        invalid_keys = set(category.keys()) - ProductService.ALLOWED_CATEGORY_KEYS
        if invalid_keys:
            raise ValueError(f'Invalid keys: {invalid_keys}')
    
    @staticmethod
    def unmarshal_items(dynamodb_items):
        return dynamodb_items
    
    @staticmethod
    def marshal_items(dynamodb_items):
        return dynamodb_items
    
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
        return product
        
    @classmethod
    def execute_and_log(cls, func, success_message, error_message, **kwargs):
        try:
            app.logger.info('Executing operation')
            response = func(**kwargs)
            app.logger.info(success_message)
            return response
        except Exception as e:
            app.logger.error(f'Execution error, {error_message}: {str(e)}')
            raise
    
    @classmethod
    def set_product_url(cls, product):
        if cls.web_root_url:
            product["url"] = f"{cls.web_root_url}/#/product/{product['id']}"
            
    @classmethod
    def set_category_url(cls, category):
        if cls.web_root_url:
            category["url"] = f"{cls.web_root_url}/#/category/{category['id']}"
            
    @classmethod
    def get_product_by_id(cls, product_id):
        product_id = str(product_id.lower())
        app.logger.info(f'Finding product with id: {product_id}, {cls.ddb_table_products}')
        response = cls.execute_and_log(
            cls.dynamo_client.get_item,
            f'Retrieved product with id: {product_id}',
            f'Error retrieving product with id: {product_id}',
            TableName=cls.ddb_table_products,
            Key={
                'id': {'S': product_id}
            }
        )
        if 'Item' in response:
            app.logger.info(f'Retrieved product: {response["Item"]}')
            product = cls.unmarshal_items(response['Item'])
            app.logger.info(f'Unmarshalled product: {product}')
            cls.set_product_url(product)
            cls.update_product_template(product)
            app.logger.info(f"Found product: {product}, category: {product['category']}")
            return product
        else:
            raise KeyError
        
    @classmethod
    def get_products_by_ids(cls, product_ids):
        if len(product_ids) > cls.MAX_BATCH_GET_ITEM:
            raise Exception("Cannot query more than 100 items at a time")
        
        app.logger.info(f"Finding products with ids: {product_ids}, {cls.ddb_table_products}")
        
        request_items = {
            cls.ddb_table_products: {
                'Keys': [{'id': product_id} for product_id in product_ids]
            }
        }
        response = cls.execute_and_log(
            cls.dynamo_client.batch_get_item,
            f'Retrieved products with ids: {product_ids}',
            f'Error retrieving products with ids: {product_ids}',
            RequestItems=request_items
        )
        products = [cls.unmarshal_items(item, cls.ALLOWED_PRODUCT_KEYS) for item in response.get('Responses', {}).get(cls.ddb_table_products, [])]
        return products
    
    @classmethod
    def get_category_by_id(cls, category_id):
        category_id = category_id.lower()
        app.logger.info(f"Finding category with id: {category_id}, {cls.ddb_table_categories}")
        response = cls.execute_and_log(
            cls.dynamo_client.get_item,
            f'Retrieved category with id: {category_id}',
            f'Error retrieving category with id: {category_id}',
            TableName=cls.ddb_table_categories,
            Key={'id': {'S': category_id}}
        )
        if 'Item' in response:
            category = cls.unmarshal_items(response['Item'])
            cls.set_category_url(category)
            app.logger.info(f"Found category: {category}")
            return category
        else:
            raise KeyError
        
    @classmethod
    def get_category_by_name(cls, category_name):
        app.logger.info(f"Finding category with name: {category_name}, {cls.ddb_table_categories}")
        response = cls.execute_and_log(
            cls.dynamo_client.query,
            f'Retrieved category with name: {category_name}',
            f'Error retrieving category with name: {category_name}',
            TableName=cls.ddb_table_categories,
            IndexName='name-index',
            ExpressionAttributeValues= {
                ':category_name': {'S': category_name}
            },
            KeyConditionExpression='#n = :category_name',
            ExpressionAttributeNames={'#n': 'name'},
            ProjectionExpression='id, #n, image'
        )
        if 'Items' in response:
            category = cls.unmarshal_items(response['Items'][0])
            cls.set_category_url(category)
            app.logger.info(f"Found category: {category}")
            return category
        else:
            raise KeyError
        
    @classmethod
    def get_product_by_category(cls, category):
        app.logger.info(f"Finding products by category: {category}, {cls.ddb_table_products}")
        
        response = cls.execute_and_log(
            cls.dynamo_client.query,
            f'Retrieved products by category: {category}',
            f'Error retrieving products by category: {category}',
            TableName=cls.ddb_table_products,
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
        if 'Items' in response:
            products = cls.unmarshal_items(response['Items'])
            for product in products:
                cls.set_product_url(product)
                cls.update_product_template(product)
            app.logger.info(f"Found products: {products}")
            return products
        
    @classmethod
    def get_featured_products(cls):
        app.logger.info(f"Finding featured products, {cls.ddb_table_products} | featured=true")
        
        
        response = cls.execute_and_log(
            cls.dynamo_client.query,
            'Retrieved featured products',
            'Error retrieving featured products',
            TableName=cls.ddb_table_products,
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
        if 'Items' in response:
            products = cls.unmarshal_items(response['Items'])
            for product in products:
                cls.set_product_url(product)
                cls.update_product_template(product)
                product['featured'] = 'true'
                app.logger.info(f"Found featured product: {product}")
            return products
        
    @classmethod
    def get_all_categories(cls):
        app.logger.info(f"Finding all categories, {cls.ddb_table_categories}")
        
        response = cls.execute_and_log(
            cls.dynamo_client.scan,
            'Retrieved all categories',
            'Error retrieving all categories',
            TableName=cls.ddb_table_categories
        )
        if 'Items' in response:
            app.logger.info(f"Found {len(response['Items'])} categories")
            categories = cls.unmarshal_items(response['Items'])
            for category in categories:
                cls.set_category_url(category)
            return categories
    
    @classmethod
    def get_all_products(cls):
        app.logger.info(f"Finding all products, {cls.ddb_table_products}")
        
        response = cls.execute_and_log(
            cls.dynamo_client.scan,
            'Retrieved all products',
            'Error retrieving all products',
            TableName=cls.ddb_table_products
        )
        if 'Items' in response:
            app.logger.info(f"Found {len(response['Items'])} products")
            products = cls.unmarshal_items(response['Items'])
            for product in products:
                cls.set_product_url(product)
                cls.update_product_template(product)
                if product['id'] == '8bffb5fb-624f-48a8-a99f-b8e9c64bbe29':
                    tshoot = product
            app.logger.info(f"Found products: {tshoot}")
            app.logger.info(f"Found products: {products[0:2]}")
            return products
        
    @classmethod
    def update_product(cls, original_product, updated_product):
        app.logger.info(f"Updating product: {original_product} to {updated_product}")
        updated_product['id'] = original_product['id']
        cls.set_product_url(updated_product)
        prep_for_marshal = []
        prep_for_marshal.append(updated_product)
        updated_product = cls.marshal_item(prep_for_marshal)
        
        
        app.logger.info(f"Updating product: {original_product} to {updated_product}")
        cls.execute_and_log(
            cls.dynamo_client.put_item,
            f'Updated product: {updated_product}',
            f'Error updating product: {updated_product}',
            TableName=cls.ddb_table_products,
            Item=updated_product
        )
        
    @classmethod
    def update_inventory_delta(cls, product, stock_delta):
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
        
        cls.execute_and_log(
            cls.dynamo_client.update_item,
            f'Updated product: {product}',
            f'Error updating product: {product}',
            **params)
        
        product['current_stock'] += stock_delta
        
    @classmethod
    def add_product(cls, product):
        product_temp = cls.get_product_template()
        app.logger.info(f"Adding product: {product}")
        product.update(product_temp)
        cls.update_product_template(product)
        cls.set_product_url(product)
        marshalled_product = cls.marshal_item([product])
        cls.execute_and_log(
            cls.dynamo_client.put_item,
            f'Added product: {marshalled_product}',
            f'Error adding product: {marshalled_product}',
            TableName=cls.ddb_table_products,
            Item=marshalled_product
        )
        
    @classmethod
    def delete_product(cls, product):
        app.logger.info(f"Deleting product: {product['name']}")
        
        cls.execute_and_log(
            cls.dynamo_client.delete_item,
            f'Deleted product: {product}',
            f'Error deleting product: {product}',
            TableName=cls.ddb_table_products,
            Key={'id': {'S': product['id']}, 'category': {'S': product['category']}}
        )