# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import os
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.ext.flask.middleware import XRayMiddleware
from aws_xray_sdk.core import patch_all

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    DDB_TABLE_USERS                 = os.environ.get('DDB_TABLE_USERS', 'users')
    DATA_DIR                        = os.environ.get('DATA_DIR', '/src/data')
    AWS_DEFAULT_REGION              = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
    USER_POOL_ID                    = os.environ.get('COGNITO_USER_POOL_ID', 'xxxx')
    TOKEN_AUDIENCE                  = os.environ.get('COGNITO_USER_POOL_CLIENT_ID', 'xxxx')
    VERIFY_IDENTITY_TOKEN           = os.environ.get('VERIFY_IDENTITY_TOKEN', 'true').lower() == 'true'
    PINPOINT_APP_ID                 = os.environ.get("PINPOINT_APP_ID", 'xxxx')

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
        xray_recorder.configure(service='Users Service')
        XRayMiddleware(app, xray_recorder)

config = {
    'Development': Development,
    'Production': ProductionConfig
}