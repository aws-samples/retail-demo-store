# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from uuid import uuid4

from flask import request
from server import app
from dynamo_setup import dynamo_client, ddb_table_orders

from boto3.dynamodb.types import TypeSerializer, TypeDeserializer
from decimal import Decimal
from werkzeug.exceptions import BadRequest


class OrderService:
    """
    Service class for handling operations related to orders.
    """
    dynamo_client = dynamo_client
    ddb_table_orders = ddb_table_orders
    
    serializer = TypeSerializer()
    deserializer = TypeDeserializer()
    
    ALLOWED_KEYS = {'id', 'items', 'total', 'username', 
                'billing_address', 'shipping_address', 'collection_phone',
                'delivery_type', 'delivery_status', 'delivery_complete',
                'channel', 'email', 'ttl', 'channel_detail'}
    
    @staticmethod
    def deserialize_item(item):
        """
        Deserializes a cart after retrieval from dynamodb

        Args:
            item: The item to be deserialized.

        Returns:
            The deserialized item.
        """
        def deserialize_value(k,v):
            if k == 'price':
                return float(OrderService.deserializer.deserialize(v))
            elif k == 'quantity' or k == 'channel_id':
                return int(OrderService.deserializer.deserialize(v))
            else:
                return OrderService.deserializer.deserialize(v)
            
        return {k: [{k2: deserialize_value(k2, v2) for k2, v2 in i['M'].items()} 
                    for i in v['L']] if k == 'items'
                else {k2: deserialize_value(k2, v2) 
                      for k2, v2 in v['M'].items()} if k == 'channel_detail'
                else float(OrderService.deserializer.deserialize(v)) if k == 'total'
                else OrderService.deserializer.deserialize(v) for k, v in item.items()}
        
        
    @staticmethod
    def serialize_item(item):
        """
        Serializes a cart to be compatible with dynamodb before put
        
        Args:
            item: The item to be serialized.

        Returns:
            The serialized item.
        """
        if isinstance(item, list):
            return {'L': [{'M': {k: OrderService.serializer.serialize(Decimal(str(v))) 
                                 if k=='price' or k=='quantity'
                     else OrderService.serializer.serialize(v) 
                     for k, v in i.items()}} for i in item]}
        if isinstance(item, dict) and item.get('channel_id') is not None:
            return {'M': {k: OrderService.serializer.serialize(Decimal(str(v))) 
                          if isinstance(v,float) or isinstance(v,int)
                     else OrderService.serializer.serialize(v) 
                     for k, v in item.items()}}
        else:
            return {k: OrderService.serialize_item(v) 
                    if k=='items' or k=='channel_detail'
                    else OrderService.serializer.serialize(v) if isinstance(v,bool)
                    else OrderService.serializer.serialize(Decimal(str(v))) 
                    if isinstance(v,float) or isinstance(v,int)
                    else OrderService.serializer.serialize(v) for k, v in item.items()}
           
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
        if 'items' not in order or not order['items']:
            order['items'] = []
        return order
        
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
        unmarshalled_orders = [cls.deserialize_item(order) 
                               for order in response['Items']]
        app.logger.info(f'Unmarshalled orders: {unmarshalled_orders}')
        return unmarshalled_orders
    
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
            ExpressionAttributeValues={':username': {'S': username}}
        )
        app.logger.info(f'Retrieved  orders: {response["Items"]}')
        unmarshalled_orders = [cls.deserialize_item(order) 
                               for order in response['Items']]
        app.logger.info(f'Unmarshalled orders: {unmarshalled_orders}')
        return unmarshalled_orders

    @classmethod
    def create_order(cls):
        """
        Creates a new order.

        Returns:
            The newly created order.
        """
        order = cls.get_order_template()
        order.update(request.get_json(force=True))
        cls.validate_order(order)
        app.logger.info(f'Order to create: {order}')
        app.logger.info('Marshalling order for dynamodb')
        marshalled_order = cls.serialize_item(order)
        app.logger.info(f'Marshalled order:{marshalled_order}')
        cls.execute_and_log(
            cls.dynamo_client.put_item,
            f'Order created with id: {order["id"]}',
            'Error creating order',
            TableName=cls.ddb_table_orders,
            Item=marshalled_order
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
            Key={'id': {'S': order_id}}
        )
        if 'Item' in response:
            order = cls.update_order_template(request.get_json(force=True))
            cls.validate_order(order)
            app.logger.info('Marshalling order for dynamodb')
            order['id'] = order_id
            marshalled_order = cls.serialize_item(order)
            cls.execute_and_log(
                cls.dynamo_client.put_item,
                f'Order updated with id: {order["id"]}',
                'Error updating order',
                TableName=cls.ddb_table_orders,
                Item=marshalled_order)
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
            Key={'id': {'S': order_id}}
        )
        if 'Item' in response:
            app.logger.info(f'Retrieved order: {response["Item"]}')
            result = cls.deserialize_item(response['Item'])
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
            Key={'id': {'S': order_id}}
        )