# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
from flask import current_app
from uuid import uuid4
from typing import Dict, Any
import yaml

from products_service import dynamodb
from products_service.personalisation import generate_personalised_description, Cache

MAX_BATCH_GET_ITEM = 100
ALLOWED_PRODUCT_KEYS = {
    'id', 'url', 'sk', 'name', 'category', 'style', 'description', 'aliases',
    'price', 'image', 'featured', 'gender_affinity', 'current_stock', 'promoted',
    'where_visible', 'related_items_theme', 'related_items'
}
missing_image_file = "product_image_coming_soon.png"

class PersonalisedDescriptionCache(Cache):

    def get(self, key: str):
        cached_item = dynamodb.personalised_products.get(key)

        return cached_item['generated_description'] if cached_item else None

    def put(self, key: str, obj):
        return dynamodb.personalised_products.upsert(
            {
                'id': key,
                'generated_description': obj
            }
        )

def get_product_by_id(product_id, fully_qualify_image_urls: bool | None = None, user: Dict[str, Any] | None = None):
    product = dynamodb.products.get(str(product_id.lower()))
    if not product:
        return None

    update_product_template(product, fully_qualify_image_urls)

    if user:
        current_app.logger.debug(f"Personalizing product description for product: {product['name']}")
        product['description'] = generate_personalised_description(product, user, PersonalisedDescriptionCache())

    return product

def get_products_by_ids(product_ids, fully_qualify_image_urls: bool):
    if len(product_ids) > MAX_BATCH_GET_ITEM:
        raise Exception("Cannot query more than 100 items at a time")

    products = dynamodb.products.gets(product_ids)
    for product in products:
        update_product_template(product, fully_qualify_image_urls)

    return products

def get_products_by_category(category, fully_qualify_image_urls: bool):
    products = dynamodb.products.get_by_category(category)
    for product in products:
        update_product_template(product, fully_qualify_image_urls)

    return products

def get_featured_products(fully_qualify_image_urls: bool):
    products = dynamodb.products.get_featured()
    for product in products:
        update_product_template(product, fully_qualify_image_urls)
        product['featured'] = 'true'

    return products

def get_all_products(fully_qualify_image_urls: bool):
    products = dynamodb.products.get_all()
    current_app.logger.debug(f"Found {len(products)} products")
    for product in products:
        update_product_template(product, fully_qualify_image_urls)

    return products

def update_product(original_product, updated_product):
    updated_product['id'] = original_product['id']
    validate_product(updated_product)
    current_app.logger.debug(f"Updating product: {original_product} to {updated_product}")
    dynamodb.products.upsert(updated_product)
    cast_price(updated_product)

def update_inventory_delta(product, stock_delta):
    if product['current_stock'] + stock_delta < 0:
        stock_delta = -product['current_stock']

    dynamodb.products.update_inventory(product['id'], product['current_stock'], stock_delta)
    product['current_stock'] += stock_delta

def add_product(product):
    product_temp = get_product_template()
    product.update(product_temp)
    validate_product(product)
    dynamodb.products.upsert(product)
    cast_price(product)

def delete_product(self, product):
    dynamodb.products.delete(product['id'])

def get_category_by_id(category_id, fully_qualify_image_urls: bool):
    category = dynamodb.categories.get(str(category_id.lower()))
    if category:
        set_category_url(category, fully_qualify_image_urls)

    return category

def get_category_by_name(category_name, fully_qualify_image_urls: bool):
    category = dynamodb.categories.get_by_name(category_name)
    if category:
        set_category_url(category, fully_qualify_image_urls)

    return category

def get_all_categories(fully_qualify_image_urls: bool):
    categories = dynamodb.categories.get_all()
    current_app.logger.debug(f"Found {len(categories)} categories")
    for category in categories:
        set_category_url(category, fully_qualify_image_urls)

    return categories

def validate_product(product):
    invalid_keys = set(product.keys()) - ALLOWED_PRODUCT_KEYS
    if invalid_keys:
        raise ValueError(f'Invalid keys: {invalid_keys}')
    category = get_category_by_name(product['category'], fully_qualify_image_urls=False)
    if not category:
        raise ValueError(f'Category {product["category"]} not found')
    product['price'] = str(product['price'])
    product['current_stock'] = int(product['current_stock'])
    set_product_url(product)

def get_product_template():
    return {
        'id': str(uuid4()),
        'aliases': []
    }

def update_product_template(product, fully_qualify_image_urls):
    if 'aliases' not in product or not product['aliases']:
        product['aliases'] = []
    if 'sk' not in product or product['sk'] is None:
        product['sk'] = ''
    product['current_stock'] = int(product['current_stock'])
    cast_price(product)
    if 'promoted' in product:
        product['promoted'] = str(product['promoted'])
    set_product_url(product)
    set_fully_qualified_product_image_url(fully_qualify_image_urls, product)

    return product

def get_fully_qualified_image_url(image: str, category_name: str) -> str:
    if image and image.find("://") > -1:
        return image
    elif image and image != missing_image_file:
        return f"{current_app.config['IMAGE_ROOT_URL']}{category_name}/{image}"
    else:
        return f"{current_app.config['IMAGE_ROOT_URL']}{missing_image_file}"

def set_fully_qualified_product_image_url(fully_qualify_image_url: bool, product: Dict[str, Any]):
    if fully_qualify_image_url:
        product["image"] = get_fully_qualified_image_url(product.get("image"), product.get("category"))
    elif not product.get("image") or product["image"] == missing_image_file:
        product["image"] = f"{current_app.config['IMAGE_ROOT_URL']}{missing_image_file}"

def set_product_url(product):
    if current_app.config['WEB_ROOT_URL']:
        product["url"] = f"{current_app.config['WEB_ROOT_URL']}/#/product/{product['id']}"

def set_category_url(category, fully_qualify_image_urls):
    if current_app.config['WEB_ROOT_URL']:
        category["url"] = f"{current_app.config['WEB_ROOT_URL']}/#/category/{category['id']}"
    if fully_qualify_image_urls:
        category["image"] = get_fully_qualified_image_url(category.get("image"), category.get("name"))
    elif not category.get("image") or category["image"] == missing_image_file:
        category["image"] = f"{current_app.config['IMAGE_ROOT_URL']}{missing_image_file}"

def cast_price(product):
    # Cast the price from a string back to a float for the frontend
    product['price'] = float(product['price'])

def init():
    dynamodb.init_tables()
    no_categories = load_categories()
    no_products = load_products()
    return no_products, no_categories

def load_products():
    products_file = current_app.config['PRODUCT_DATA']
    with open(products_file, 'r') as f:
        products = yaml.safe_load(f)

    current_app.logger.info("Updating products")
    for product in products:
        if product.get('price'):
            product['price'] = str(product['price'])
        if product.get('featured'):
            product['featured'] = str(product['featured']).lower()
        dynamodb.products.upsert(product)

    return len(products)

def load_categories():
    categories_file = current_app.config['CATEGORY_DATA']
    with open(categories_file, 'r') as f:
        categories = yaml.safe_load(f)

    current_app.logger.info("Updating categories")
    for category in categories:
        category['id'] = str(category['id'])
        dynamodb.categories.upsert(category)

    return len(categories)