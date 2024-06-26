# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
from flask import jsonify, request, current_app, Blueprint, g
from flask_cors import CORS
from werkzeug.exceptions import BadRequest, UnsupportedMediaType, NotFound, Unauthorized
from botocore.exceptions import BotoCoreError


from users_service.repository import (
    send_pinpoint_message, init, get_all_users, get_user_by_id,
    get_user_by_username, get_user_by_identity_id, get_unclaimed_users,
    get_random_user, claim_user, upsert_user, verify_and_update_phone
)
from users_service import auth

api = Blueprint('api', __name__)
CORS(api)

@api.before_request
def load_user():
    auth_header = request.headers.get('Authorization')
    if auth_header:
        token = auth_header.split()[1]
        g.user = auth.auth_user(token)

@api.route("/")
def index():
    return jsonify({"message": "Welcome to the Users Service"}), 200

@api.route('/users/init', methods=['POST'])
def initialise_users():
    users_loaded = init()
    return jsonify({"users": users_loaded}), 200

@api.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200

@api.route('/users/all', methods=['GET'])
def get_users():
    users = get_all_users()
    return [user.to_dict() for user in users], 200

@api.route("/users/id/<user_id>", methods=['GET'])
def get_user(user_id):
    if not user_id:
        raise BadRequest("User ID is required")
    user = get_user_by_id(user_id)
    if user:
        return jsonify(user.to_dict()), 200
    else:
        raise NotFound(f"User with ID {user_id} not found")

@api.route("/users/username/<username>", methods=['GET'])
def get_user_by_name(username):
    user = get_user_by_username(username)
    if user:
        return jsonify(user.to_dict()), 200
    else:
        raise NotFound(f"User with username {username} not found")

@api.route("/users/identityid/<identity_id>", methods=['GET'])
def get_user_by_identity(identity_id):
    user = get_user_by_identity_id(identity_id)
    if user:
        return jsonify(user.to_dict()), 200
    else:
        raise NotFound(f"User with identity ID {identity_id} not found")

@api.route("/users/unclaimed", methods=['GET'])
def get_unclaimed():
    users = get_unclaimed_users()
    return [user.to_dict() for user in users], 200

@api.route("/users/random", methods=['GET'])
def get_random(count: int = 1):
    users = get_random_user(count)
    result = [user.to_dict() for user in users]
    return result, 200

@api.route("/users/id/<user_id>/claim", methods=['PUT'])
def claim_user_route(user_id):
    user, message = claim_user(user_id)
    current_app.logger.debug(f"claim_user_route: Claiming user with ID {user_id}: {message}")
    if user:
        return jsonify({"message": message}), 200
    else:
        raise NotFound(f"User with ID {user_id} {message}")

@api.route("/users", methods=['POST'])
def create_user_route():
    user_data = request.get_json(force=True)
    new_user, message = upsert_user(user_data)
    return jsonify(new_user.to_dict()), 201

@api.route("/users/id/<user_id>", methods=['PUT'])
def update_user_route(user_id):
    updated_data = request.get_json(force=True)
    current_app.logger.debug(f"update_user_route: Updating user with ID {user_id}: {updated_data}")
    if not updated_data:
        raise BadRequest("No data provided")
    user,message = upsert_user(updated_data, user_id=user_id)
    if user:
        return jsonify(user.to_dict()), 200
    else:
        raise NotFound(f"User with ID {user_id} not found, Message: {message}")

@api.route("/users/id/<user_id>/verifyphone", methods=['PUT'])
def verify_and_update_phone_route(user_id):
    phone_data = request.get_json(force=True)
    phone_number = phone_data.get('phone_number')
    user = verify_and_update_phone(user_id, phone_number)
    if user:
        send_pinpoint_message(phone_number)
        return jsonify(user.to_dict()), 200
    else:
        raise NotFound(f"User with ID {user_id} not found")

# Errors

@api.errorhandler(BadRequest)
def handle_bad_request(e):
    current_app.logger.error(f'BadRequest: {str(e)}')
    return jsonify({"error": "Bad request, please check your input"}), 400

@api.errorhandler(BotoCoreError)
def handle_boto_core_error(e):
    current_app.logger.error(f'BotoCoreError: {str(e)}')
    return jsonify({"error": "Internal server error"}), 500

@api.errorhandler(NotFound)
def handle_not_found(e):
    current_app.logger.error(f'NotFound: {str(e)}')
    return jsonify({"error": "Not found"}), 404

@api.errorhandler(UnsupportedMediaType)
def handle_unsupported_media_type(e):
    current_app.logger.error(f'UnsupportedMediaType: {str(e)}')
    return jsonify({"error": "Unsupported media type"}), 415

@api.errorhandler(Unauthorized)
def handle_unauthorized(e):
    current_app.logger.error(f'Unauthorized: {str(e)}')
    return jsonify({"error": "Unauthorized"}), 401

@api.errorhandler(500)
def handle_internal_error(e):
    current_app.logger.error(f'InternalServerError: {str(e)}')
    return jsonify({"error": "Internal server error"}), 500
