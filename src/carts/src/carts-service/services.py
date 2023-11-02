# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
from datetime import datetime, timedelta
from uuid import uuid4

import boto3
from flask import request
from server import app
from dynamo_setup import dynamo_client, ddb_table_carts

from boto3.dynamodb.types import TypeSerializer, TypeDeserializer
from decimal import Decimal
from werkzeug.exceptions import BadRequest


class CartService:
    """
    Service class for handling operations related to shopping carts.
    """
    dynamo_client = dynamo_client
    ddb_table_carts = ddb_table_carts
    cart_ttl_days = 7
    
    serializer = TypeSerializer()
    deserializer = TypeDeserializer()
    
    ALLOWED_KEYS = {'id', 'items', 'ttl', 'username'}
    
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
                return float(CartService.deserializer.deserialize(v))
            elif k == 'quantity':
                return int(CartService.deserializer.deserialize(v))
            else:
                return CartService.deserializer.deserialize(v)
            
        return {k: [{k2: deserialize_value(k2, v2) for k2, v2 in i['M'].items()} for i in v['L']] if k == 'items'
            else CartService.deserializer.deserialize(v) for k, v in item.items()}
        
    @staticmethod
    def validate_cart(cart):
        """
        Validates a cart before put to dynamodb

        Args:
            cart: The cart to be validated.
        """
        invalid_keys = set(cart.keys()) - CartService.ALLOWED_KEYS
        if invalid_keys:
            app.logger.info(f"Invalid keys in cart: {invalid_keys}")
            raise BadRequest
        
        
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
            return {'L': [{'M': {k: CartService.serializer.serialize(Decimal(str(v))) if k=='price' or k=='quantity'
                     else CartService.serializer.serialize(v) for k, v in i.items()}} for i in item]}
        else:
            return {k: CartService.serialize_item(v) if k=='items'
                    else CartService.serializer.serialize(v) for k, v in item.items()} 

    @staticmethod
    def get_cart_template():
        """
        Returns a template for a new shopping cart.

        Returns:
            A dictionary representing a new shopping cart.
        """
        return {'items': [], 'id': str(uuid4()), 'ttl': int((datetime.utcnow() + timedelta(days=CartService.cart_ttl_days)).timestamp())}
    

    @staticmethod
    def update_cart_template(cart):
        """
        Updates a shopping cart template with necessary data before put to dynamo

        Args:
            cart: The cart to be updated.

        Returns:
            The updated cart.
        """
        if 'items' not in cart or not cart['items']:
            cart['items'] = []
        cart['ttl'] = int((datetime.utcnow() + timedelta(days=CartService.cart_ttl_days)).timestamp())
        return cart
    
    
   
        
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
    def cart_index(cls):
        """
        Retrieves all shopping carts from DynamoDB.

        Returns:
            A list of all shopping carts.
        """
        response = cls.execute_and_log(
            cls.dynamo_client.scan,
            'Retrieving all carts',
            'Error retrieving carts',
            TableName=cls.ddb_table_carts
        )
        app.logger.info(f'Retrieved all carts: {response["Items"]}')
        unmarshalled_carts = [cls.deserialize_item(cart) for cart in response['Items']]
        app.logger.info(f'Unmarshalled carts: {unmarshalled_carts}')
        return unmarshalled_carts
    
    @classmethod
    def get_cart_by_username(cls):
        """
        Retrieves a shopping cart by username.

        Returns:
            The shopping cart associated with the username.
        """
        username = request.args.get('username')
        app.logger.info(f'Retrieving cart by username: {username}')
        response = cls.execute_and_log(
            cls.dynamo_client.query,
            'Retrieving all carts',
            'Error retrieving carts',
            TableName=cls.ddb_table_carts,
            IndexName='username-index',
            KeyConditionExpression='username = :username',
            ExpressionAttributeValues={':username': {'S': username}}
        )
        app.logger.info(f'Retrieved  carts: {response["Items"]}')
        unmarshalled_carts = [cls.deserialize_item(cart)  for cart in response['Items']]
        app.logger.info(f'Unmarshalled carts: {unmarshalled_carts}')
        return unmarshalled_carts

    @classmethod
    def create_cart(cls):
        """
        Creates a new shopping cart.

        Returns:
            The newly created shopping cart.
        """
        cart = cls.get_cart_template()
        cart.update(request.get_json(force=True))
        cls.validate_cart(cart)
        app.logger.info(f'Cart to create: {cart}')
        app.logger.info('Marshalling cart for dynamodb')
        marshalled_cart = cls.serialize_item(cart)
        app.logger.info(f'Marshalled cart:{marshalled_cart}')
        cls.execute_and_log(
            cls.dynamo_client.put_item,
            f'Cart created with id: {cart["id"]}',
            'Error creating cart',
            TableName=cls.ddb_table_carts,
            Item=marshalled_cart
        )
        return cart

    @classmethod
    def update_cart(cls,cart_id):
        """
        Updates an existing shopping cart.

        Returns:
            The updated shopping cart.
        """
        cart_id = cart_id.lower()
        response = cls.execute_and_log(
            cls.dynamo_client.get_item,
            f'Retrieved cart with id: {cart_id}',
            f'Error retrieving cart with id: {cart_id}',
            TableName=cls.ddb_table_carts,
            Key={'id': {'S': cart_id}}
        )
        if 'Item' in response:
            cart = cls.update_cart_template(request.get_json(force=True))
            cls.validate_cart(cart)
            if cart['id'] != cart_id:
                raise BadRequest
            app.logger.info('Marshalling cart for dynamodb')
            marshalled_cart = cls.serialize_item(cart)
            cls.execute_and_log(
                cls.dynamo_client.put_item,
                f'Cart updated with id: {cart["id"]}',
                'Error updating cart',
                TableName=cls.ddb_table_carts,
                Item=marshalled_cart)
            return cart
        else:
            raise KeyError

    @classmethod
    def get_cart_by_id(cls, cart_id):
        """
        Retrieves a shopping cart by its ID.

        Args:
            cart_id: The ID of the shopping cart.

        Returns:
            The shopping cart associated with the ID.

        Raises:
            KeyError: If the shopping cart does not exist.
        """
        cart_id = cart_id.lower()
        response = cls.execute_and_log(
            cls.dynamo_client.get_item,
            f'Retrieved cart with id: {cart_id}',
            f'Error retrieving cart with id: {cart_id}',
            TableName=cls.ddb_table_carts,
            Key={'id': {'S': cart_id}}
        )
        if 'Item' in response:
            app.logger.info(f'Retrieved cart: {response["Item"]}')
            result = cls.deserialize_item(response['Item'])
            app.logger.info(f'Unmarshalled cart: {result}')
            return result
        else:
            raise KeyError('Cart does not exist')

    @classmethod
    def delete_cart(cls, cart_id):
        """
        Deletes a shopping cart by its ID.

        Args:
            cart_id: The ID of the shopping cart.
        """
        cls.execute_and_log(
            cls.dynamo_client.delete_item,
            f'Cart deleted with id: {cart_id}',
            f'Error deleting cart with id: {cart_id}',
            TableName=cls.ddb_table_carts,
            Key={'id': {'S': cart_id}}
        )

    @staticmethod
    def sign_amazon_pay_payload():
        """
        Signs an Amazon Pay payload using a Lambda function.

        Returns:
            The signed Amazon Pay payload.
        """
        session = boto3.Session()
        client = session.client('lambda')
        payload = request.get_json()
        response = client.invoke(
            FunctionName='AmazonPaySigningLambda',
            Payload=json.dumps(payload)
        )
        response_payload = json.loads(response['Payload'].read())
        app.logger.info('Signed Amazon Pay payload')
        return response_payload