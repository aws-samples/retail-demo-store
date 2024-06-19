import random
from users_service.models import User, Address
from flask import current_app
import json
import gzip
from pynamodb.exceptions import DoesNotExist
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
            create_or_update_user(user_data)

def create_or_update_user(user_data):
    try:
        user = User.get(user_data["id"])
        current_app.logger.info(f"User already exists: {user_data['id']}")
        #update_user_with_data(user, user_data)
    except DoesNotExist:
        current_app.logger.info(f"Creating new user: {user_data['id']}")
        user = User()
        update_user_with_data(user, user_data)
        user.save()

def update_user_with_data(user, user_data):
    current_app.logger.info(f"Updating user:{user} with data: {user_data}")
    addresses_data = user_data.pop("addresses", [])
    addresses = [Address(**ad) for ad in addresses_data]
    user.addresses = addresses
    for key, value in user_data.items():
        setattr(user, key, value)
    user.save()

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

def create_user(user_data):
    user = User()
    current_app.logger.info(f"Creating new user: {user_data}")
    update_user_with_data(user, user_data)
    return user

def update_user(user_id, updated_data):
    user = get_user_by_id(user_id)
    if user:
        update_user_with_data(user, updated_data)
        return user
    return User()

def verify_and_update_phone(user_id, phone_number):
    user = get_user_by_id(user_id)
    if user:
        user.phone_number = phone_number
        user.save()
        return user
    return None

def send_pinpoint_message(phone_number):
    pinpoint.send_pinpoint_message(phone_number)