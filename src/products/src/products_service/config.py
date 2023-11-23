# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import os
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.ext.flask.middleware import XRayMiddleware
from aws_xray_sdk.core import patch_all

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    DDB_TABLE_PRODUCTS              = os.environ['DDB_TABLE_PRODUCTS']
    DDB_TABLE_CATEGORIES            = os.environ['DDB_TABLE_CATEGORIES']
    DDB_TABLE_PERSONALISED_PRODUCTS = os.environ['DDB_TABLE_PERSONALISED_PRODUCTS']
    CACHE_PERSONALISED_PRODUCTS     = os.environ.get('CACHE_PERSONALISED_PRODUCTS', "True") == "True"
    IMAGE_ROOT_URL                  = os.environ.get('IMAGE_ROOT_URL')
    WEB_ROOT_URL                    = os.environ.get('WEB_ROOT_URL')
    USERS_SERVICE_HOST              = os.environ.get('USERS_SERVICE_HOST')
    USERS_SERVICE_PORT              = os.environ.get('USERS_SERVICE_PORT', 80)

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