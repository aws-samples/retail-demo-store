from fastapi import APIRouter, HTTPException
from users.models import User, Address
from users.repository import get_all_users, get_user_by_id, get_user_by_username, get_user_by_identity_id, get_unclaimed_users, get_random_user, claim_user, create_user, update_user, verify_and_update_phone
from users.pinpoint import send_pinpoint_message

router = APIRouter()

@router.get("/")
def index():
    return {"message": "Welcome to the User Service"}

@router.get("/users/all")
def get_users():
    users = get_all_users()
    return [user.to_dict() for user in users]

@router.get("/users/id/{user_id}")
def get_user(user_id: str):
    user = get_user_by_id(user_id)
    if user:
        return user.to_dict()
    raise HTTPException(status_code=404, detail="User not found")

@router.get("/users/username/{username}")
def get_user_by_name(username: str):
    user = get_user_by_username(username)
    if user:
        return user.to_dict()
    raise HTTPException(status_code=404, detail="User not found")

@router.get("/users/identityid/{identity_id}")
def get_user_by_identity(identity_id: str):
    user = get_user_by_identity_id(identity_id)
    if user:
        return user.to_dict()
    raise HTTPException(status_code=404, detail="User not found")

@router.get("/users/unclaimed")
def get_unclaimed():
    users = get_unclaimed_users()
    return [user.to_dict() for user in users]

@router.get("/users/random")
def get_random(count: int = 1):
    users = get_random_user(count)
    return [user.to_dict() for user in users]

@router.put("/users/id/{user_id}/claim")
def claim_user_route(user_id: str):
    if claim_user(user_id):
        return {"message": f"User {user_id} claimed successfully"}
    raise HTTPException(status_code=404, detail="User not found")

@router.post("/users")
def create_user_route(user: dict):
    new_user = create_user(user)
    return new_user.to_dict()

@router.put("/users/id/{user_id}")
def update_user_route(user_id: str, updated_data: dict):
    user = update_user(user_id, updated_data)
    if user:
        return user.to_dict()
    raise HTTPException(status_code=404, detail="User not found")

@router.put("/users/id/{user_id}/verifyphone")
def verify_and_update_phone_route(user_id: str, phone_number: str):
    user = verify_and_update_phone(user_id, phone_number)
    if user:
        send_pinpoint_message(phone_number)
        return user.to_dict()
    raise HTTPException(status_code=404, detail="User not found")
