# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from flask import make_response, jsonify, Blueprint
from server import app
from services import OrderService
from flask import request

routes_bp = Blueprint('routes', __name__)

order_service = OrderService()

def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response

@app.route('/')
def index():
    app.logger.info('Processing default request')
    return jsonify("Welcome to the Orders Web Service"),200

@app.route('/orders/all', methods=['GET'])
def order_index():
    app.logger.info("Processing request to get all orders")
    return jsonify(order_service.order_index()), 200

@app.route('/orders/username/<username>', methods=['GET'])
def order_index_by_username(username):
    app.logger.info(f"Processing request to get all orders for user {username}")
    return jsonify(order_service.get_order_by_username(username)), 200

@app.route('/orders/id/<order_id>', methods=['GET'])
def order_index_by_id(order_id):
    app.logger.info(f"Processing request to get order {order_id}")
    return jsonify(order_service.get_order_by_id(order_id)), 200

@app.route('/orders', methods=['POST', 'OPTIONS'])
def order_create():
    app.logger.info("Processing request to create an order")
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    return jsonify(order_service.create_order()), 201

@app.route('/orders/id/<order_id>', methods=['PUT', 'OPTIONS'])
def order_update(order_id):
    app.logger.info(f"Processing request to update order with id {order_id}")
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    return jsonify(order_service.update_order(order_id)), 200