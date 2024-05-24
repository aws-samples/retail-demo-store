import random
from users.models import User, Address

claimed_users = set()

def get_all_users():
    return User.scan()

def get_user_by_id(user_id):
    return User.get(user_id)

def get_user_by_username(username):
    return User.query("username", username)

def get_user_by_identity_id(identity_id):
    return User.query("identity_id", identity_id)

def get_unclaimed_users():
    unclaimed_users = []
    for user in User.scan():
        if user.selectable_user and user.identity_id not in claimed_users:
            unclaimed_users.append(user)
    return unclaimed_users

def get_random_user(count):
    unclaimed_users = get_unclaimed_users()
    return random.sample(unclaimed_users, min(count, len(unclaimed_users)))

def claim_user(user_id):
    user = get_user_by_id(user_id)
    if user and user.selectable_user:
        claimed_users.add(user.identity_id)
        return True
    return False

def create_user(user_data):
    addresses = []
    for address_data in user_data.pop("addresses", []):
        address = Address(**address_data)
        address.save()
        addresses.append(address.address_id)
    user = User(**user_data, addresses=addresses)
    user.save()
    return user

def update_user(user_id, updated_data):
    user = get_user_by_id(user_id)
    if user:
        for key, value in updated_data.items():
            setattr(user, key, value)
        user.save()
        return user
    return None

def verify_and_update_phone(user_id, phone_number):
    user = get_user_by_id(user_id)
    if user:
        user.phone_number = phone_number
        user.save()
        return user
    return None
