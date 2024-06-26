# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
from datetime import datetime
import random
import pytz
from users_service.models import User, Address
from flask import current_app
import json
import gzip
from typing import Optional
from users_service import pinpoint
from botocore.exceptions import ClientError
from typing import Any, Dict





def init():
    User.init_tables()
    try:
        count = load_users_into_dynamodb(f"{current_app.config.get('DATA_DIR')}/users.json.gz")
        unclaimed_count = User.claimed_index.count(0)
        claimed_count = User.claimed_index.count(1)
        current_app.logger.debug(f"Loaded {claimed_count} claimed users and {unclaimed_count} unclaimed users.")
        return count
    except Exception as e:
        raise e

def load_users_into_dynamodb(filename):
    count = 0
    with gzip.open(filename, 'rt', encoding='utf-8') as file:
        data = json.load(file)
        for user_data in data:
            upsert_user(user_data)
            count += 1
    return count

def upsert_user(user_data: Dict[str, Any], user_id: Optional[str] = None, conditions: Optional[Any] = None):
    current_app.logger.debug(f"Upserting user with data: {user_data}")
    if not user_id:
        user_id = user_data.pop('id', None)
    user = User(id=user_id) 
    
    update_actions = []

    valid_keys = {attr for attr in dir(User) if not callable(getattr(User, attr)) and not attr.startswith("__")}
    
    complex_keys = {"addresses", "id", "claimed_user"} 
    valid_keys = valid_keys - complex_keys

    for key, value in user_data.items():
        if key in valid_keys:
            attribute = getattr(User, key)
            if hasattr(attribute, 'set'):
                try:
                    update_actions.append(attribute.set(value))
                except Exception as e:
                    current_app.logger.error(f"Error setting attribute '{key}' on User model: {e}")
            else:
                current_app.logger.warning(f"Attribute '{key}' on User model does not support 'set' operation.")
        else:
            if key not in complex_keys:
                current_app.logger.warning(f"Attribute '{key}' not found on User model; ignoring.")

    if "addresses" in user_data:
        addresses = [Address(**ad) for ad in user_data['addresses']]
        update_actions.append(User.addresses.set(addresses))
        
    if "claimed_user" in user_data:
        update_actions.append(User.claimed_user.set(user_data['claimed_user']))
    else:
        update_actions.append(User.claimed_user.set(0))

    if update_actions:
        try:
            user.update(actions=update_actions, condition=conditions)
            current_app.logger.debug(f"User {user} has been created or updated.")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                current_app.logger.error(f"Conditional check failed for user {user_id}")
                return None, "Condition check failed"
            else:
                current_app.logger.error(f"Unexpected ClientError for user {user_id}: {str(e)}")
                return None, "Unexpected error during upsert"
        except Exception as e:
            current_app.logger.error(f"Unexpected error during upsert for user {user_id}: {str(e)}")
            return None, "Unexpected error during upsert"
    else:
        current_app.logger.warning(f"No valid update actions were found for user ID {user_id}.")

    return user, True

def get_all_users():
    return User.scan()

def get_user_by_id(user_id):
    try:
        return User.get(user_id)
    except User.DoesNotExist:
        return None

def get_user_by_username(username):
    try:
        return next(User.username_index.query(username), User())
    except Exception as e:
        current_app.logger.error(f"Error getting user by username: {e}")
        return None

def get_user_by_identity_id(identity_id):
    try:
        return next(User.identity_id_index.query(identity_id), User())
    except Exception as e:
        current_app.logger.error(f"Error getting user by identity_id: {e}")
        return None
    

'''def update_claimed_index():
    try:
        update_count = 0
        for user in User.scan():
            # Force an update to trigger index recalculation
            user.update(actions=[User.claimed_user.set(user.claimed_user)])
            update_count += 1
        current_app.logger.debug(f"Updated {update_count} users to refresh the index")
        return {"updated_count": update_count}
    except Exception as e:
        current_app.logger.error(f"Error in update_claimed_index: {e}")
        return {"error": str(e)}'''

def get_unclaimed_users():
    try:
        unclaimed_users = list(User.claimed_index.query(0))
        current_app.logger.debug(f"Found {len(unclaimed_users)} unclaimed users")
        return unclaimed_users
    except Exception as e:
        current_app.logger.error(f"Error getting unclaimed users: {e}")
        return []


def get_random_user(count):
    unclaimed_users = get_unclaimed_users()
    current_app.logger.debug(f"Found {len(unclaimed_users)} unclaimed users")
    return random.sample(unclaimed_users, min(count, len(unclaimed_users)))



def claim_user(user_id):
    user, message = upsert_user({"claimed_user": 1},user_id=user_id, conditions=(User.selectable_user == True)&(User.claimed_user == 0)) # noqa: E712
    return user, message

def verify_and_update_phone(user_id, phone_number):
    user = get_user_by_id(user_id)
    if user:
        user.update(actions=[User.phone_number.set(phone_number)])
        return user
    return None

def send_pinpoint_message(phone_number):
    pinpoint.send_pinpoint_message(phone_number)