# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
from flask import Flask

from products_service.db import DynamoDB
from products_service.auth import Auth
import logging

dynamodb = DynamoDB()
auth = Auth()

def create_app(config) -> Flask:
    app = Flask(__name__)

    configure_logging()
    
    app.config.from_object(config)
    config.init_app(app)

    initialize_extensions(app)
    register_blueprints(app)
    
    return app

def initialize_extensions(app: Flask) -> None:
    dynamodb.init_app(app)
    auth.init_app(app)

def register_blueprints(app: Flask) -> None:
    from . import routes
    
    app.register_blueprint(routes.api)

def configure_logging():
    logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler()])