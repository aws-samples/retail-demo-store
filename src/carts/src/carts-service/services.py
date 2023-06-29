# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from flask import request
from server import app
from werkzeug.exceptions import BadRequest
import json
import boto3

class CartService:
    def __init__(self):
        self.carts = {}
        self.current_id = 0

    def cart_index(self):
        app.logger.info('Retrieved all carts')
        return list(self.carts.values())

    def create_cart(self):
        try:
            cart = request.get_json(force=True)
            self.current_id += 1
            cart['id'] = str(self.current_id)
            if 'items' not in cart:
                cart['items'] = []
            self.carts[cart['id']] = cart
            app.logger.info(f'Created cart with id {self.current_id}')
            return cart
        except BadRequest as e:
            app.logger.warning(f'Error creating cart: {str(e)}')
            raise 

    def update_cart(self, cart_id):
        try:
            cart = request.get_json(force=True)
            cart_id_str = str(cart_id)
            if cart_id_str in self.carts:
                cart['id'] = cart_id_str
                if 'items' not in cart:
                    cart['items'] = []
                self.carts[cart_id_str] = cart
                app.logger.info(f'Updated cart with id {cart_id}')
                return cart
            else:
                app.logger.warning(f'Attempt to update non-existent cart with id {cart_id}')
                raise KeyError('Cart not found')
        except BadRequest as e:
            app.logger.warning(f'Error updating cart: {str(e)}')
            raise

    def get_cart_by_id(self, cart_id):
        try:
            cart = self.carts[cart_id]
            app.logger.info(f'Retrieved cart with id {cart_id}')
            return cart
        except KeyError:
            app.logger.warning(f'Attempt to retrieve non-existent cart with id {cart_id}')
            raise

    def sign_amazon_pay_payload(self):
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
