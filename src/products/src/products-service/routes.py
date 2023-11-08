# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import os
from decimal import Decimal
from flask import  jsonify, Blueprint
from server import app
from services import ProductService
from flask import request, abort, Response
from typing import List, Dict, Any
from http import HTTPStatus
from werkzeug.exceptions import HTTPException
import json


route_bp = Blueprint('route_bp', __name__)
product_service = ProductService()

image_root_url = os.getenv('IMAGE_ROOT_URL')
missing_image_file = "product_image_coming_soon.png"



def should_fully_qualify_image_urls() -> bool:
    param = request.args.get("fullyQualifyimageUrls", "1")
    return param.lower() in ["1", "true"]

def fully_qualify_image_url(image: str, category_name: str) -> str:
    if image and image != missing_image_file:
        return f"{image_root_url}{category_name}/{image}"
    else:
        return f"{image_root_url}{missing_image_file}"


def set_fully_qualified_category_image_url(category: Dict[str, Any]):
    if should_fully_qualify_image_urls():
        category["image"] = fully_qualify_image_url(category.get("image"), category.get("name"))
    elif not category.get("image") or category["image"] == missing_image_file:
        category["image"] = f"{image_root_url}{missing_image_file}"


def set_fully_qualified_product_image_url(product: Dict[str, Any]):
    if should_fully_qualify_image_urls():
        product["image"] = fully_qualify_image_url(product.get("image"), product.get("category"))
    elif not product.get("image") or product["image"] == missing_image_file:
        product["image"] = f"{image_root_url}{missing_image_file}"


def set_fully_qualified_category_image_urls(categories: List[Dict[str, Any]]):
    for category in categories:
        set_fully_qualified_category_image_url(category)


def set_fully_qualified_product_image_urls(products: List[Dict[str, Any]]):
    for product in products:
        set_fully_qualified_product_image_url(product)
        
def custom_serializer(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError("Type not serializable")    

@app.route('/')
def index():
    app.logger.info('Processing default request')
    return jsonify("Welcome to the Products Web Service"),200

@app.route('/products/all', methods=['GET'])
def get_all_products():
    app.logger.info('Processing get all products request')
    products = product_service.get_all_products()
    set_fully_qualified_product_image_urls(products)
    return Response(json.dumps(products, default=custom_serializer), mimetype='application/json'), 200

@app.route('/products/id/<product_ids>', methods=['GET', 'PUT', 'DELETE'])
def get_products_by_id(product_ids):
    if request.method == 'GET':
        app.logger.info('Processing get products by ID request')
        product_ids = product_ids.split(",")
        if len(product_ids) > product_service.MAX_BATCH_GET_ITEM:
            return jsonify({"error": f"Maximum number of product IDs per request is {product_service.MAX_BATCH_GET_ITEM}"}), HTTPStatus.UNPROCESSABLE_ENTITY
        if len(product_ids) > 1:
            products = product_service.get_products_by_ids(product_ids)
            set_fully_qualified_product_image_urls(products)
            return jsonify(products), 200
            
        else:
            product = product_service.get_product_by_id(product_ids[0])
            if not product:
                abort(HTTPStatus.NOT_FOUND)
            set_fully_qualified_product_image_url(product)
            app.logger.info(f"retrieved product: {product}")
            return jsonify(product), 200
    elif request.method == 'PUT':
        app.logger.info('Processing update products by ID request')
        product = request.get_json(force=True)
        app.logger.info(f"retrieving existing product with id: {product_ids}")
        existing_product = product_service.get_product_by_id(product_ids)
        
        if not existing_product:
            return jsonify({"error": "Product does not exist"}), 404
        
        try:
            product_service.update_product(existing_product, product)
        except Exception as e:
            return jsonify({"error": e}), 422
        
        set_fully_qualified_product_image_url(existing_product)
        return jsonify(existing_product), 200
    elif request.method == 'DELETE':
        app.logger.info('Processing delete product by ID request')
        
        product = product_service.get_product_by_id(product_ids)
        
        if not product:
            return jsonify({"error": "Product does not exist"}), 404
        
        try:
            product_service.delete_product(product)
        except Exception as e:
            return jsonify({"error": e.description}), 422
        
@app.route('/products/featured', methods=['GET'])
def get_featured_products():
    app.logger.info('Processing get featured products request')
    products = product_service.get_featured_products()
    set_fully_qualified_product_image_urls(products)
    return jsonify(products), 200

@app.route('/products/category/<category_name>', methods=['GET'])
def get_products_by_category(category_name):
    app.logger.info('Processing get products by category request')
    products = product_service.get_product_by_category(category_name)
    set_fully_qualified_product_image_urls(products)
    return jsonify(products), 200

@app.route('/products', methods=['POST'])
def create_product():
    app.logger.info('Processing create product request')
    product = request.get_json()
    try:
        product_service.add_product(product)
    except Exception as e:
        return jsonify({"error": e.description}), 422
    
    set_fully_qualified_product_image_url(product)
    return jsonify(product), 201

@app.route('/products/id/<productID>/inventory', methods=['PUT'])
def update_product_inventory(product_id):
    app.logger.info('Processing update product inventory request')
    inventory = request.get_json()
    app.logger.info(f"UpdateInventory --> {inventory}")
    
    product = product_service.get_product_by_id(product_id)
    
    if not product:
        return jsonify({"error": "Product does not exist"}), 404
    
    try:
        product_service.update_inventory_delta(product, inventory['stock_delta'])
    except Exception as e:
        return jsonify({"error": e.description}), 422
    
    set_fully_qualified_category_image_url(product)
    
    return jsonify(product), 200
    

@app.route('/categories/all', methods=['GET'])
def get_all_categories():
    app.logger.info('Processing get all categories request')
    categories = product_service.get_all_categories()
    set_fully_qualified_category_image_urls(categories)
    return jsonify(categories), 200

@app.route('/categories/id/<category_id>', methods=['GET'])
def get_categories_by_id(category_id):
    app.logger.info('Processing get category by ID request')
    
    try:
        category = product_service.get_category_by_id(category_id)
    except Exception as e:
        return jsonify({"error": e.description}), 422
    
    set_fully_qualified_category_image_url(category)
    
    return jsonify(category), 200