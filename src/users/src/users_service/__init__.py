# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
from flask import Flask

from users_service.auth import Auth
from users_service.pinpoint import Pinpoint
from users_service.models import User
import logging


auth = Auth()
pinpoint = Pinpoint()

def create_app(config) -> Flask:
    app = Flask(__name__)

    configure_logging()
    
    app.config.from_object(config)
    config.init_app(app)

    initialize_extensions(app)
    register_blueprints(app)
    
    return app

def initialize_extensions(app: Flask) -> None:
    auth.init_app(app)
    pinpoint.init_app(app)
    User.init_app(app)

def register_blueprints(app: Flask) -> None:
    from . import routes
    
    app.register_blueprint(routes.api)

def configure_logging():
    logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler()])