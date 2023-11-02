# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from flask import request, jsonify, Blueprint
from server import app
from services import CartService
from flask import make_response

route_bp = Blueprint('route_bp', __name__)

cart_service = CartService()

def _build_cors_preflight_response():
    response = jsonify('')
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response

@app.route('/')
def index():
    app.logger.info('Processing default request')
    return "Welcome to the Carts Web Service", 200

@app.route('/carts', methods=['GET', 'POST', 'OPTIONS'])
def carts_index():
    app.logger.info('Processing request for /carts')
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    elif request.method == 'POST':
        response = make_response(jsonify(cart_service.create_cart()))
        response.status_code = 201
        response.content_type = 'application/json'
        return response
    return jsonify(cart_service.get_cart_by_username()), 200


@app.route('/carts/<cart_id>', methods=['GET', 'PUT', 'OPTIONS'])
def cart_operations(cart_id):
    app.logger.info(f'Processing request for /carts/{cart_id}')
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    elif request.method == 'PUT':
        return jsonify(cart_service.update_cart(cart_id)), 200
    return jsonify(cart_service.get_cart_by_id(cart_id)), 200

@app.route('/sign', methods=['POST', 'OPTIONS'])
def sign_payload():
    app.logger.info('Processing request for /sign')
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    return jsonify(cart_service.sign_amazon_pay_payload()), 200