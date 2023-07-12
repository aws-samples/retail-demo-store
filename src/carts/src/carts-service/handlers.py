# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from flask import jsonify
from werkzeug.exceptions import BadRequest
from botocore.exceptions import BotoCoreError
from server import app

@app.errorhandler(BadRequest)
def handle_bad_request(e):
    app.logger.error(f'BadRequest: {str(e)}')
    return jsonify({"error": "Bad request, please check your input"}), 400

@app.errorhandler(BotoCoreError)
def handle_boto_core_error(e):
    app.logger.error(f'BotoCoreError: {str(e)}')
    print(str(e))
    return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(KeyError)
def handle_key_error(e):
    app.logger.error(f'KeyError: {str(e)}')
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def handle_internal_error(e):
    app.logger.error(f'InternalServerError: {str(e)}')
    print(str(e))
    return jsonify({"error": "Internal server error"}), 500
