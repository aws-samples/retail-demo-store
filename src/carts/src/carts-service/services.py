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


class CartService:
    """
    Service class for handling operations related to shopping carts.
    """
    dynamo_client = dynamo_client
    ddb_table_carts = ddb_table_carts
    cart_ttl_days = 7
    
    serializer = TypeSerializer()
    deserializer = TypeDeserializer()
    
    @staticmethod
    def deserialize_item(item):
        """
        Deserializes a DynamoDB item.

        Args:
            item: The item to be deserialized.

        Returns:
            The deserialized item.
        """
        return {k: CartService.deserializer.deserialize(v) for k, v in item.items()}

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
        Updates a shopping cart template with new data.

        Args:
            cart: The cart to be updated.

        Returns:
            The updated cart.
        """
        if 'items' not in cart or not cart['items']:
            cart['items'] = []
        else:
            cart['items'] = [{k: Decimal(str(v)) if isinstance(v, float) else v for k, v in item.items()} for item in cart['items']]
        cart['id'] = cart['id']
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
        cart.update(request.get_json())
        cart = cls.update_cart_template(cart)
        app.logger.info(f'Cart to create: {cart}')
        app.logger.info('Marshalling cart for dynamodb')
        marshalled_cart = cls.serializer.serialize(cart)
        app.logger.info(f'Marshalled cart:{marshalled_cart["M"]}')
        cls.execute_and_log(
            cls.dynamo_client.put_item,
            f'Cart created with id: {cart["id"]}',
            'Error creating cart',
            TableName=cls.ddb_table_carts,
            Item=marshalled_cart['M']
        )
        return cart

    @classmethod
    def update_cart(cls):
        """
        Updates an existing shopping cart.

        Returns:
            The updated shopping cart.
        """
        cart = cls.update_cart_template(request.get_json(force=True))
        app.logger.info('Marshalling cart for dynamodb')
        marshalled_cart = cls.serializer.serialize(cart)
        cls.execute_and_log(
            cls.dynamo_client.put_item,
            f'Cart updated with id: {cart["id"]}',
            'Error updating cart',
            TableName=cls.ddb_table_carts,
            Item=marshalled_cart['M']
        )
        return cart

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
