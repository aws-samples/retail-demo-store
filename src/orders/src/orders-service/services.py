# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
from uuid import uuid4
from flask import request
from server import app
from dynamo_setup import dynamo_resource, ddb_table_orders
from decimal import Decimal
from werkzeug.exceptions import BadRequest
from copy import deepcopy


class OrderService:
    """
    Service class for handling operations related to orders.
    """
    dynamo_client = dynamo_resource.meta.client
    ddb_table_orders = ddb_table_orders
    
    ALLOWED_KEYS = {'id', 'items', 'total', 'username', 
                'billing_address', 'shipping_address', 'collection_phone',
                'delivery_type', 'delivery_status', 'delivery_complete',
                'channel', 'email', 'ttl', 'channel_detail'}
    

        
    @staticmethod
    def decimal_to_float(item):
        """
        Converts a decimal to a float

        Args:
            item: The item to be converted.

        Returns:
            The converted item.
        """
        new_item = deepcopy(item)
        if 'items' in new_item:
            for i in new_item['items']:
                i['price'] = float(i['price'])
                i['quantity'] = int(i['quantity'])
        if 'total' in new_item:
            new_item['total'] = float(new_item['total'])
        if 'channel_detail' in new_item:
            new_item['channel_detail']['channel_id'] = int(new_item['channel_detail']['channel_id'])
        return new_item
        
           
    @staticmethod
    def validate_order(order):
        """
        Validates an order.

        Args:
            order: The order to be validated.

        Returns:
            True if the order is valid, False otherwise.
        """
        invalid_keys = set(order.keys()) - OrderService.ALLOWED_KEYS
        if invalid_keys:
            app.logger.info(f'Invalid keys: {invalid_keys}')
            raise BadRequest
            
        
    @staticmethod
    def get_order_template():
        """
        Returns a template for an order.
        
        Returns:
            A dictionary representing an order.
        """
        return {
            'id': str(uuid4()),
            'items': []
            }
        
    @staticmethod
    def update_order_template(order):
        """
        Updates order template with necessary data before put to dynamo

        Args:
            order: The order to be updated.

        Returns:
            The updated order.
        """
        decimal_order = deepcopy(order)
        if 'items' not in decimal_order or not decimal_order['items']:
            decimal_order['items'] = []
            
        for item in decimal_order['items']:
            if 'price' in item:
                item['price'] = Decimal(str(item['price']))
        if 'total' in decimal_order:
            decimal_order['total'] = Decimal(str(decimal_order['total']))
        if 'channel_detail' in decimal_order:
            decimal_order['channel_detail']['channel_id'] = Decimal(str(decimal_order['channel_detail']['channel_id']))
        if 'delivery_status' not in decimal_order:
            decimal_order['delivery_status'] = 'pending'
        return decimal_order
        
    @classmethod
    def execute_and_log(cls, operation, success_message, error_message, **kwargs):
        """
        Executes a DynamoDB operation and logs the result.

        Args:
            operation: The DynamoDB operation to be executed.
            success_message: The message to be logged upon successful execution.
            error_message: The message to be logged upon unsuccessful execution.
            **kwargs: Additional keyword arguments for the operation.

        Returns:
            The response from the DynamoDB operation.

        Raises:
            Exception: If the operation fails.
        """
        try:
            app.logger.info('Executing operation')
            response = operation(**kwargs)
            app.logger.info(success_message)
            return response
        except Exception as e:
            app.logger.warning(f'{error_message}: {str(e)}')
            raise

    @classmethod
    def order_index(cls):
        """
        Retrieves all orders from DynamoDB.

        Returns:
            A list of all orders.
        """
        response = cls.execute_and_log(
            cls.dynamo_client.scan,
            'Retrieving all orders',
            'Error retrieving orders',
            TableName=cls.ddb_table_orders
        )
        app.logger.info(f'Retrieved all orders: {response["Items"]}')
        result = [cls.decimal_to_float(order) 
                               for order in response['Items']]
        app.logger.info(f'Unmarshalled orders: {result}')
        return result
    
    @classmethod
    def get_order_by_username(cls,username):
        """
        Retrieves an order by username.

        Returns:
            The orders associated with the username.
        """
        app.logger.info(f'Retrieving order by username: {username}')
        response = cls.execute_and_log(
            cls.dynamo_client.query,
            'Retrieving all orders',
            'Error retrieving orders',
            TableName=cls.ddb_table_orders,
            IndexName='username-index',
            KeyConditionExpression='username = :username',
            ExpressionAttributeValues={':username': username}
        )
        app.logger.info(f'Retrieved  orders: {response["Items"]}')
        result = [cls.decimal_to_float(order) 
                               for order in response['Items']]
        app.logger.info(f'Unmarshalled orders: {result}')
        return result

    @classmethod
    def create_order(cls):
        """
        Creates a new order.

        Returns:
            The newly created order.
        """
        order = cls.get_order_template()
        order.update(request.get_json(force=True))
        order['total'] = float(order['total'])
        decimal_order = cls.update_order_template(order)
        cls.validate_order(decimal_order)
        app.logger.info(f'Order to create: {order}')
        app.logger.info(f'decimal order:{decimal_order}')
        cls.execute_and_log(
            cls.dynamo_client.put_item,
            f'Order created with id: {order["id"]}',
            'Error creating order',
            TableName=cls.ddb_table_orders,
            Item=decimal_order
        )
        return order

    @classmethod
    def update_order(cls,order_id):
        """
        Updates an existing order.

        Returns:
            The updated order.
        """
        order_id = order_id.lower()
        response = cls.execute_and_log(
            cls.dynamo_client.get_item,
            f'Retrieved order with id: {order_id}',
            f'Error retrieving order with id: {order_id}',
            TableName=cls.ddb_table_orders,
            Key={'id': order_id}
        )
        if 'Item' in response:
            order = request.get_json(force=True)
            order['total'] = float(order['total'])
            decimal_order = cls.update_order_template(order)
            cls.validate_order(decimal_order)
            app.logger.info(f'order to update to :{order}')
            app.logger.info(f'decimal order to update to :{decimal_order}')
            decimal_order['id'] = order_id
            cls.execute_and_log(
                cls.dynamo_client.put_item,
                f'Order updated with id: {decimal_order["id"]}',
                'Error updating order',
                TableName=cls.ddb_table_orders,
                Item=decimal_order)
            return order
        else:
            raise KeyError('Order does not exist')

    @classmethod
    def get_order_by_id(cls, order_id):
        """
        Retrieves an order by its ID.

        Args:
            order_id: The ID of the order.

        Returns:
            The order associated with the ID.

        Raises:
            KeyError: If the order does not exist.
        """
        order_id = order_id.lower()
        response = cls.execute_and_log(
            cls.dynamo_client.get_item,
            f'Retrieved order with id: {order_id}',
            f'Error retrieving order with id: {order_id}',
            TableName=cls.ddb_table_orders,
            Key={'id': order_id}
        )
        if 'Item' in response:
            app.logger.info(f'Retrieved order: {response["Item"]}')
            result = cls.decimal_to_float(response['Item'])
            app.logger.info(f'Unmarshalled order: {result}')
            return result
        else:
            raise KeyError

    @classmethod
    def delete_order(cls, order_id):
        """
        Deletes an order by its ID.

        Args:
            order_id: The ID of the order.
        """
        cls.execute_and_log(
            cls.dynamo_client.delete_item,
            f'Order deleted with id: {order_id}',
            f'Error deleting order with id: {order_id}',
            TableName=cls.ddb_table_orders,
            Key={'id': order_id}
        )