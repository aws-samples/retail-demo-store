# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
from datetime import datetime, timedelta
from uuid import uuid4

import boto3
from flask import request
from server import app
from dynamo_setup import dynamo_client, ddb_table_carts
from botocore.exceptions import ClientError

from werkzeug.exceptions import BadRequest


class CartService:
    dynamo_client = dynamo_client
    ddb_table_carts = ddb_table_carts
    cart_ttl_days = 7

    @staticmethod
    def marshal_item(data):
        app.logger.info(f"Marshalling item: {data}")
        if isinstance(data, dict):
            if  'items' in data:
                return {k: CartService.marshal_item(v) for k, v in data.items()}
            else:
                return {'M': {k: CartService.marshal_item(v) for k, v in data.items()}}
        elif isinstance(data, list):
            if all(isinstance(item, dict) for item in data):
                return {'L': [CartService.marshal_item(item) for item in data]}
            return {'L': [{'S': item} for item in data]}
        elif isinstance(data, (int, float)):
            return {'N': str(data)}
        else:
            return {'S': str(data)}

    @staticmethod
    def unmarshal_value(data):
        app.logger.info(f"Unmarshalling value: {data}")
        if 'N' in data:
            return float(data['N'])
        elif 'BOOL' in data:
            return data['BOOL']
        elif 'L' in data:
            return [CartService.unmarshal_value(item) for item in data['L']]
        elif 'M' in data:
            return CartService.unmarshal_item(data['M'])
        else:
            return data['S']

    @staticmethod
    def unmarshal_item(data):
        return {key: CartService.unmarshal_value(value) for key, value in data.items()}

    @staticmethod
    def get_cart_template():
        return {'items': [], 'id': str(uuid4()), 'ttl': int((datetime.utcnow() + timedelta(days=CartService.cart_ttl_days)).timestamp())}

    @staticmethod
    def update_cart_template(cart):
        if 'items' not in cart or not cart['items']:
            cart['items'] = []
        cart['id'] = cart['id']
        cart['ttl'] = int((datetime.utcnow() + timedelta(days=CartService.cart_ttl_days)).timestamp())
        return cart

    @classmethod
    def execute_and_log(cls, operation, success_message, error_message, **kwargs):
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
        response = cls.execute_and_log(
            cls.dynamo_client.scan,
            'Retrieving all carts',
            'Error retrieving carts',
            TableName=cls.ddb_table_carts
        )
        unmarshalled_carts = [cls.unmarshal_item(cart) for cart in response['Items']]
        app.logger.info(f'Unmarshalled carts: {unmarshalled_carts}')
        return unmarshalled_carts
    
    @classmethod
    def get_cart_by_username(cls):
        username = request.args.get('username')
        app.logger.info(f'Retrieving cart by username: {username}')
        """ if username == 'guest':
            return cls.get_cart_template() """
        response = cls.execute_and_log(
            cls.dynamo_client.query,
            'Retrieving all carts',
            'Error retrieving carts',
            TableName=cls.ddb_table_carts,
            IndexName='username-index',
            KeyConditionExpression='username = :username',
            ExpressionAttributeValues={':username': {'S': username}}
        )
        unmarshalled_carts = [cls.unmarshal_item(cart) for cart in response['Items']]
        app.logger.info(f'Unmarshalled carts: {unmarshalled_carts}')
        return unmarshalled_carts

    @classmethod
    def create_cart(cls):
        cart = cls.get_cart_template()
        cart.update(request.get_json())
        app.logger.info(f'Cart to create: {cart}')
        app.logger.info('Marshalling cart for dynamodb')
        marshalled_cart = cls.marshal_item(cart)
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
    def update_cart(cls):
        cart = cls.update_cart_template(request.get_json(force=True))
        app.logger.info('Marshalling cart for dynamodb')
        marshalled_cart = cls.marshal_item(cart)
        cls.execute_and_log(
            cls.dynamo_client.put_item,
            f'Cart updated with id: {cart["id"]}',
            'Error updating cart',
            TableName=cls.ddb_table_carts,
            Item=marshalled_cart
        )
        return cart

    @classmethod
    def get_cart_by_id(cls, cart_id):
        cart_id = cart_id.lower()
        response = cls.execute_and_log(
            cls.dynamo_client.get_item,
            f'Retrieved cart with id: {cart_id}',
            f'Error retrieving cart with id: {cart_id}',
            TableName=cls.ddb_table_carts,
            Key={'id': {'S': cart_id}}
        )
        if 'Item' in response:
            result = cls.unmarshal_item(response['Item'])
            app.logger.info(f'Unmarshalled cart: {result}')
            return result
        else:
            raise KeyError('Cart does not exist')

    @classmethod
    def delete_cart(cls, cart_id):
        cls.execute_and_log(
            cls.dynamo_client.delete_item,
            f'Cart deleted with id: {cart_id}',
            f'Error deleting cart with id: {cart_id}',
            TableName=cls.ddb_table_carts,
            Key={'id': {'S': cart_id}}
        )

    @staticmethod
    def sign_amazon_pay_payload():
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
