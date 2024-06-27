from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from flask import current_app
import json
import gzip
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
import pytz
import random
from users_service.models import User, Address, get_age_range, get_valid_keys
from users_service import pinpoint

def init():
    User.init_tables()
    try:
        count = load_users_into_dynamodb(f"{current_app.config.get('DATA_DIR')}/users.json.gz")
        unclaimed_count = count_users_by_claimed_status(0)
        claimed_count = count_users_by_claimed_status(1)
        current_app.logger.debug(f"Loaded {claimed_count} claimed users and {unclaimed_count} unclaimed users.")
        return count
    except Exception as e:
        current_app.logger.error(f"Error in init: {str(e)}")
        raise e

def load_users_into_dynamodb(filename: str) -> int:
    count = 0
    with gzip.open(filename, 'rt', encoding='utf-8') as file:
        data = json.load(file)
        for user_data in data:
            upsert_user(user_data)
            count += 1
    return count

def upsert_user(user_data: Dict[str, Any], user_id: Optional[str] = None, conditions: Optional[Any] = None, expression_values: Optional[Any] = None) -> Tuple[Optional[User], bool]:
    current_app.logger.debug(f"Upserting user with data: {user_data}")
    if not user_id:
        user_id = user_data.pop('id', None)
    
    update_expression = "SET "
    expression_attribute_values = {}
    expression_attribute_names = {}

    valid_keys = get_valid_keys(User)
    complex_keys = {"addresses", "id", "claimed_user", "sign_up_date", "last_sign_in_date", "age", "age_range"}
    valid_keys = valid_keys - complex_keys

    for key, value in user_data.items():
        if key in valid_keys:
            update_expression += f"#{key} = :{key}, "
            expression_attribute_names[f"#{key}"] = key
            expression_attribute_values[f":{key}"] = value
        elif key in ["sign_up_date", "last_sign_in_date"]:
            if value:
                parsed_date = parse_iso_datetime(value)
            if parsed_date:
                update_expression += f"#{key} = :{key}, "
                expression_attribute_names[f"#{key}"] = key
                expression_attribute_values[f":{key}"] = parsed_date.isoformat()
            else:
                current_app.logger.warning(f"Invalid date format for '{key}': {value}")
        elif key not in complex_keys:
            current_app.logger.warning(f"Attribute '{key}' not found on User model; ignoring.")

    if "age" in user_data:
        age_range = get_age_range(user_data['age'])
        update_expression += "#age = :age, #age_range = :age_range, "
        expression_attribute_names["#age"] = "age"
        expression_attribute_names["#age_range"] = "age_range"
        expression_attribute_values[":age"] = user_data['age']
        expression_attribute_values[":age_range"] = age_range

    if "addresses" in user_data:
        addresses = [Address(**ad).to_dict() for ad in user_data['addresses']]
        update_expression += "#addresses = :addresses, "
        expression_attribute_names["#addresses"] = "addresses"
        expression_attribute_values[":addresses"] = addresses

    if "claimed_user" in user_data:
        update_expression += "#claimed_user = :claimed_user, "
        expression_attribute_names["#claimed_user"] = "claimed_user"
        expression_attribute_values[":claimed_user"] = user_data['claimed_user']
    else:
        update_expression += "#claimed_user = :claimed_user, "
        expression_attribute_names["#claimed_user"] = "claimed_user"
        expression_attribute_values[":claimed_user"] = 0

    update_expression = update_expression.rstrip(", ")

    if update_expression != "SET ":
        try:
            # Merge expression_values if provided
            if expression_values:
                expression_attribute_values.update(expression_values)
            
            params = {
                'Key': {'id': user_id},
                'UpdateExpression': update_expression,
                'ExpressionAttributeValues': expression_attribute_values,
                'ExpressionAttributeNames': expression_attribute_names,
                'ReturnValues': "ALL_NEW"
            }
            if conditions:
                params['ConditionExpression'] = conditions

            response = User.table.update_item(**params)
            current_app.logger.debug(f"response is {response['Attributes']}")
            updated_user = User.from_dict(response['Attributes'])
            current_app.logger.debug(f"User {updated_user.id} has been created or updated.")
            return updated_user, True
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
        return None, "No valid update actions"
def parse_iso_datetime(date_str: str) -> Optional[datetime]:
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00')).astimezone(pytz.utc)
    except ValueError as e:
        current_app.logger.error(f"Error parsing date: {e}")
        return None

def get_all_users() -> List[User]:
    response = User.table.scan()
    return [User.from_dict(item) for item in response.get('Items', [])]

def get_user_by_id(user_id: str) -> Optional[User]:
    try:
        response = User.table.get_item(Key={'id': user_id})
        item = response.get('Item')
        return User.from_dict(item) if item else None
    except ClientError as e:
        current_app.logger.error(f"Error getting user by id: {str(e)}")
        return None

def get_user_by_username(username: str) -> Optional[User]:
    try:
        response = User.table.query(
            IndexName='username-index',
            KeyConditionExpression=Key('username').eq(username)
        )
        items = response.get('Items', [])
        return User.from_dict(items[0]) if items else None
    except ClientError as e:
        current_app.logger.error(f"Error getting user by username: {str(e)}")
        return None

def get_user_by_identity_id(identity_id: str) -> Optional[User]:
    try:
        response = User.table.query(
            IndexName='identity_id-index',
            KeyConditionExpression=Key('identity_id').eq(identity_id)
        )
        items = response.get('Items', [])
        return User.from_dict(items[0]) if items else None
    except ClientError as e:
        current_app.logger.error(f"Error getting user by identity_id: {str(e)}")
        return None

def get_unclaimed_users(query: Optional[Dict[str, Any]] = None) -> List[User]:
    current_app.logger.debug(f"Querying for unclaimed users with query: {query}")
    try:
        key_condition_expression = Key('claimed_user').eq(0)
        filter_expression = None

        if query:
            if 'primaryPersona' in query:
                if filter_expression:
                    filter_expression &= Attr('persona').contains(query['primaryPersona'])
                else:
                    filter_expression = Attr('persona').contains(query['primaryPersona'])
            if 'ageRange' in query:
                if filter_expression:
                    filter_expression &= Attr('age_range').eq(query['ageRange'])
                else:
                    filter_expression = Attr('age_range').eq(query['ageRange'])

        query_params = {
            'IndexName': 'claimed-index',
            'KeyConditionExpression': key_condition_expression,
        }

        if filter_expression:
            query_params['FilterExpression'] = filter_expression

        response = User.table.query(**query_params)

        users = [User.from_dict(item) for item in response.get('Items', [])]

        # Pagination handling
        while 'LastEvaluatedKey' in response:
            query_params['ExclusiveStartKey'] = response['LastEvaluatedKey']
            response = User.table.query(**query_params)
            users.extend([User.from_dict(item) for item in response.get('Items', [])])

        return users
    except ClientError as e:
        current_app.logger.error(f"Error getting unclaimed users: {str(e)}")
        return []

def get_random_user(count: int) -> List[User]:
    unclaimed_users = get_unclaimed_users()
    current_app.logger.debug(f"Found {len(unclaimed_users)} unclaimed users")
    return random.sample(unclaimed_users, min(count, len(unclaimed_users)))

def claim_user(user_id: str) -> Tuple[Optional[User], str]:
    condition = "attribute_exists(id) AND selectable_user = :selectable AND claimed_user = :unclaimed"
    expression_values = {':selectable': True, ':unclaimed': 0}
    user, message = upsert_user(
        {"claimed_user": 1}, 
        user_id=user_id, 
        conditions=condition,
        expression_values=expression_values
    )
    return user, message

def verify_and_update_phone(user_id: str, phone_number: str) -> Optional[User]:
    user, _ = upsert_user({"phone_number": phone_number}, user_id=user_id)
    return user

def count_users_by_claimed_status(claimed_status: int) -> int:
    try:
        total_count = 0
        last_evaluated_key = None

        while True:
            query_params = {
                'IndexName': 'claimed-index',
                'KeyConditionExpression': Key('claimed_user').eq(claimed_status),
                'Select': 'COUNT'
            }

            if last_evaluated_key:
                query_params['ExclusiveStartKey'] = last_evaluated_key

            response = User.table.query(**query_params)
            
            total_count += response['Count']

            last_evaluated_key = response.get('LastEvaluatedKey')
            if not last_evaluated_key:
                break

        return total_count
    except ClientError as e:
        current_app.logger.error(f"Error counting users by claimed status: {str(e)}")
        return 0

def send_pinpoint_message(phone_number: str):
    pinpoint.send_pinpoint_message(phone_number)

def update_claimed_index():
    try:
        update_count = 0
        scan_kwargs = {}
        done = False
        start_key = None
        while not done:
            if start_key:
                scan_kwargs['ExclusiveStartKey'] = start_key
            response = User.table.scan(**scan_kwargs)
            for item in response.get('Items', []):
                user = User.from_dict(item)
                upsert_user({"claimed_user": user.claimed_user}, user_id=user.id)
                update_count += 1
            start_key = response.get('LastEvaluatedKey', None)
            done = start_key is None
        current_app.logger.debug(f"Updated {update_count} users to refresh the index")
        return {"updated_count": update_count}
    except Exception as e:
        current_app.logger.error(f"Error in update_claimed_index: {e}")
        return {"error": str(e)}

# Additional utility functions

def batch_write_users(users: List[User]) -> Tuple[int, int]:
    """
    Batch write users to DynamoDB table.
    Returns a tuple of (success_count, failure_count)
    """
    success_count = 0
    failure_count = 0
    with User.table.batch_writer() as batch:
        for user in users:
            try:
                batch.put_item(Item=user.to_dict())
                success_count += 1
            except ClientError as e:
                current_app.logger.error(f"Error batch writing user {user.id}: {str(e)}")
                failure_count += 1
    return success_count, failure_count

def delete_user(user_id: str) -> bool:
    """
    Delete a user from the DynamoDB table.
    Returns True if successful, False otherwise.
    """
    try:
        User.table.delete_item(Key={'id': user_id})
        return True
    except ClientError as e:
        current_app.logger.error(f"Error deleting user {user_id}: {str(e)}")
        return False

def get_users_by_age_range(age_range: str) -> List[User]:
    """
    Get users by age range using a secondary index.
    """
    try:
        response = User.table.query(
            IndexName='age_range-index',
            KeyConditionExpression=Key('age_range').eq(age_range)
        )
        return [User.from_dict(item) for item in response.get('Items', [])]
    except ClientError as e:
        current_app.logger.error(f"Error getting users by age range: {str(e)}")
        return []

def update_user_persona(user_id: str, new_persona: str) -> Optional[User]:
    """
    Update a user's persona.
    """
    return upsert_user({"persona": new_persona}, user_id=user_id)[0]

def get_users_by_persona(persona: str) -> List[User]:
    """
    Get users by persona using a scan operation with a filter.
    """
    try:
        response = User.table.scan(
            FilterExpression=Attr('persona').contains(persona)
        )
        users = [User.from_dict(item) for item in response.get('Items', [])]
        
        # Handle pagination
        while 'LastEvaluatedKey' in response:
            response = User.table.scan(
                FilterExpression=Attr('persona').contains(persona),
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            users.extend([User.from_dict(item) for item in response.get('Items', [])])
        
        return users
    except ClientError as e:
        current_app.logger.error(f"Error getting users by persona: {str(e)}")
        return []

