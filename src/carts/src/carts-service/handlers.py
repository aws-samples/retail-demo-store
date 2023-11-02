# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from flask import jsonify,Blueprint
from werkzeug.exceptions import BadRequest, UnsupportedMediaType, NotFound
from botocore.exceptions import BotoCoreError
from server import app

handler_bp = Blueprint('handler_bp', __name__)

@app.errorhandler(BadRequest)
def handle_bad_request(e):
    app.logger.error(f'BadRequest: {str(e)}')
    return jsonify({"error": "Bad request, please check your input"}), 400

@app.errorhandler(BotoCoreError)
def handle_boto_core_error(e):
    app.logger.error(f'BotoCoreError: {str(e)}')
    return jsonify({"error": "Internal server error"}), 500

#error for user not found
@app.errorhandler(NotFound)
def handle_not_found(e):
    app.logger.error(f'NotFound: {str(e)}')
    return jsonify({"error": "User not found"}), 404

@app.errorhandler(KeyError)
def handle_key_error(e):
    app.logger.error(f'KeyError: {str(e)}')
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(UnsupportedMediaType)
def handle_unsupported_media_type(e):
    app.logger.error(f'UnsupportedMediaType: {str(e)}')
    return jsonify({"error": "Unsupported media type"}), 415

@app.errorhandler(500)
def handle_internal_error(e):
    app.logger.error(f'InternalServerError: {str(e)}')
    return jsonify({"error": "Internal server error"}), 500