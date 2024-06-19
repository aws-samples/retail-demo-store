# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import random
from users_service.models import User, Address
from flask import current_app
import json
import gzip
from typing import Optional
from users_service import pinpoint

claimed_users = {}

def init():
    User.init_tables()
    try:
        load_users_into_dynamodb(f"{current_app.config.get('DATA_DIR')}/users.json.gz")
        return True
    except Exception as e:
        raise e
    
    
def load_users_into_dynamodb(filename):
    with gzip.open(filename, 'rt', encoding='utf-8') as file:
        data = json.load(file)
        for user_data in data:
            upsert_user(user_data)

def upsert_user(user_data, user_id: Optional[str]=None):
    current_app.logger.info(f"Upserting user with data: {user_data}")
    if not user_id:
        user_id = user_data.pop('id', None)
    user = User(id=user_id) 
    
    update_actions = []

    valid_keys = {attr for attr in dir(User) if not callable(getattr(User, attr)) and not attr.startswith("__")}
    
    complex_keys = {"addresses","id"} 
    valid_keys = valid_keys - complex_keys

    for key, value in user_data.items():
        if key in valid_keys:
            attribute = getattr(User, key)
            if hasattr(attribute, 'set'):
                update_actions.append(attribute.set(value))
            else:
                current_app.logger.warning(f"Attribute '{key}' on User model does not support 'set' operation.")
        else:
            if key not in complex_keys:
                current_app.logger.warning(f"Attribute '{key}' not found on User model; ignoring.")

    if "addresses" in user_data:
        addresses = [Address(**ad) for ad in user_data['addresses']]
        update_actions.append(User.addresses.set(addresses))

    if update_actions:
        user.update(actions=update_actions)
        current_app.logger.info(f"User with ID {user_id} has been created or updated.")
    else:
        current_app.logger.warning(f"No valid update actions were found for user ID {user_id}.")

    return user




def get_all_users():
    return User.scan()

def get_user_by_id(user_id):
    user = User.get(user_id)
    if user:
            return user
    else:
        return User()

def get_user_by_username(username):
    try:
        return next(User.username_index.query(username), User())
    except Exception as e:
        current_app.logger.error(f"Error getting user by username: {e}")


def get_user_by_identity_id(identity_id):
    try:
        return next(User.identity_id_index.query(identity_id), User())
    except Exception as e:
        current_app.logger.error(f"Error getting user by username: {e}")


def get_unclaimed_users():
    unclaimed_users = []
    for user in User.scan():
        if user.selectable_user and not claimed_users.get(user.id, False):
            unclaimed_users.append(user)
    return unclaimed_users

def get_random_user(count):
    unclaimed_users = get_unclaimed_users()
    return random.sample(unclaimed_users, min(count, len(unclaimed_users)))

def claim_user(user_id):
    user = get_user_by_id(user_id)
    if user and user.selectable_user:
        claimed_users[user.id] = True
        return True
    return False


def verify_and_update_phone(user_id, phone_number):
    user = get_user_by_id(user_id)
    if user:
        user.phone_number = phone_number
        user.save()
        return user
    return None

def send_pinpoint_message(phone_number):
    pinpoint.send_pinpoint_message(phone_number)