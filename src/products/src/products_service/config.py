# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import os
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.ext.flask.middleware import XRayMiddleware
from aws_xray_sdk.core import patch_all

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    DDB_TABLE_PRODUCTS              = os.environ.get('DDB_TABLE_PRODUCTS', 'products')
    DDB_TABLE_CATEGORIES            = os.environ.get('DDB_TABLE_CATEGORIES', 'categories')
    DDB_TABLE_PERSONALISED_PRODUCTS = os.environ.get('DDB_TABLE_PERSONALISED_PRODUCTS', 'personalisedproducts')
    CACHE_PERSONALISED_PRODUCTS     = os.environ.get('CACHE_PERSONALISED_PRODUCTS', "True") == "True"
    IMAGE_ROOT_URL                  = os.environ.get('IMAGE_ROOT_URL')
    WEB_ROOT_URL                    = os.environ.get('WEB_ROOT_URL')
    DATA_DIR                        = os.environ.get('DATA_DIR', '/src/data')
    CATEGORY_DATA                   = os.path.join(DATA_DIR, os.environ.get('CATEGORY_DATA', "categories.yaml"))
    PRODUCT_DATA                    = os.path.join(DATA_DIR, os.environ.get('PRODUCT_DATA', "products.yaml"))
    AWS_DEFAULT_REGION              = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
    USER_POOL_ID                    = os.environ.get('COGNITO_USER_POOL_ID', 'xxxx')
    TOKEN_AUDIENCE                  = os.environ.get('COGNITO_USER_POOL_CLIENT_ID', 'xxxx')
    VERIFY_IDENTITY_TOKEN           = os.environ.get('VERIFY_IDENTITY_TOKEN', 'true').lower() == 'true'

    @staticmethod
    def init_app(app):
        pass


class Development(Config):
    DEBUG                           = True
    DDB_ENDPOINT_OVERRIDE           = os.environ.get('DDB_ENDPOINT_OVERRIDE')

class ProductionConfig(Config):
    DEBUG                           = False

    @staticmethod
    def init_app(app):
        patch_all()
        xray_recorder.configure(service='Products Service')
        XRayMiddleware(app, xray_recorder)

config = {
    'Development': Development,
    'Production': ProductionConfig
}