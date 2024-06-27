from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from flask import current_app
import json
import gzip
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
import pytz
import random
from users_service.models import User, get_age_range, get_valid_keys
from users_service import pinpoint
from decimal import Decimal

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
    batch_size = 25  
    users_batch = []
    
    with gzip.open(filename, 'rt', encoding='utf-8') as file:
        data = json.load(file)
        for user_data in data:
            user_data = create_valid_dict(user_data)
            users_batch.append(user_data)
            
            if len(users_batch) == batch_size:
                success, failure = batch_write_users(users_batch)
                count += success
                if failure > 0:
                    current_app.logger.warning(f"{failure} users failed to write in this batch")
                users_batch = []
        
        # Write any remaining users
        if users_batch:
            success, failure = batch_write_users(users_batch)
            count += success
            if failure > 0:
                current_app.logger.warning(f"{failure} users failed to write in the final batch")
    
    return count

def claim_user(user_id: str) -> Tuple[Optional[User], str]:
    condition = "attribute_exists(id) AND selectable_user = :selectable AND claimed_user = :unclaimed"
    expression_values = {':selectable': True, ':unclaimed': 0}
    update_data = {"claimed_user": 1}
    user, message = upsert_user(
        update_data, 
        user_id=user_id, 
        conditions=condition,
        expression_values=expression_values
    )
    return user, message

def create_user(user_data: Dict[str, Any]) -> Tuple[Optional[User], str]:
    current_app.logger.info(f"Creating user with raw data: {user_data}")
    user_data = create_valid_dict(user_data)
    current_app.logger.info(f"Creating user with updated data: {user_data}")
    user, message = upsert_user(user_data)
    return user, message

def create_valid_dict(user_data: Dict[str, Any]) -> Dict[str, Any]:
    empty_user = User()
    empty_user_dict= empty_user.to_dict()
    empty_user_dict.update(user_data)
    user_data = empty_user_dict
    return user_data

def upsert_user(user_data: Dict[str, Any], user_id: Optional[str] = None, conditions: Optional[Any] = None, expression_values: Optional[Any] = None) -> Tuple[Optional[User], bool]:
    current_app.logger.debug(f"Upserting user with data: {user_data}")
    if not user_id:
        user_id = user_data.pop('id', None)
    
    update_expression, expression_attribute_names, expression_attribute_values, _ = prepare_user_data_for_dynamodb(user_data)

    if update_expression != "SET ":
        try:
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
    
def batch_write_users(users: List[Dict[str, Any]]) -> Tuple[int, int]:
    success_count = 0
    failure_count = 0
    with User.table.batch_writer() as batch:
        for user_data in users:
            try:
                _, _, _, prepared_data = prepare_user_data_for_dynamodb(user_data)
                prepared_data['id'] = user_data['id']
                current_app.logger.debug(f"Writing user {user_data.get('id')}: {prepared_data}")
                batch.put_item(Item=prepared_data)
                success_count += 1
            except ClientError as e:
                current_app.logger.error(f"Error batch writing user {user_data.get('id')}: {str(e)}")
                failure_count += 1
    return success_count, failure_count

def prepare_user_data_for_dynamodb(user_data: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, str], Dict[str, Any]]:
    update_expression = "SET "
    expression_attribute_values = {}
    expression_attribute_names = {}
    expression_attribute_data = {}

    valid_keys = get_valid_keys(User)
    complex_keys = {"addresses", "id", "claimed_user", "sign_up_date", "last_sign_in_date",
                    "age_range", "primary_persona"}
    valid_keys = valid_keys - complex_keys

    for key, value in user_data.items():
        if key in valid_keys:
            update_expression += f"#{key} = :{key}, "
            expression_attribute_names[f"#{key}"] = key
            expression_attribute_data[key] = expression_attribute_values[f":{key}"] = value
        elif key in ["sign_up_date", "last_sign_in_date"]:
            parsed_date = None
            if value:
                parsed_date = parse_iso_datetime(value)
            if parsed_date:
                update_expression += f"#{key} = :{key}, "
                expression_attribute_names[f"#{key}"] = key
                expression_attribute_data[key] = expression_attribute_values[f":{key}"] = parsed_date.isoformat()
            else:
                current_app.logger.warning(f"Invalid date format for '{key}': {value}")
        elif key not in complex_keys:
            current_app.logger.warning(f"Attribute '{key}' not found on User model; ignoring.")

    if "age" in user_data:
        age_range = get_age_range(user_data['age'])
        update_expression += "#age_range = :age_range, "
        expression_attribute_names["#age_range"] = "age_range"
        expression_attribute_data["age_range"] = expression_attribute_values[":age_range"] = age_range

    if "addresses" in user_data:
        addresses = user_data['addresses']
        update_expression += "#addresses = :addresses, "
        expression_attribute_names["#addresses"] = "addresses"
        expression_attribute_data["addresses"] = expression_attribute_values[":addresses"] = addresses
        
    if "persona" in user_data:
        primary_persona = user_data["persona"].split("_")[0]
        update_expression += "#primary_persona = :primary_persona, "
        expression_attribute_names["#primary_persona"] = "primary_persona"
        expression_attribute_data["primary_persona"] = expression_attribute_values[":primary_persona"] = primary_persona

    if "claimed_user" in user_data:
        update_expression += "#claimed_user = :claimed_user, "
        expression_attribute_names["#claimed_user"] = "claimed_user"
        expression_attribute_data["claimed_user"] = expression_attribute_values[":claimed_user"] = Decimal(user_data['claimed_user'])
    else:
        update_expression += "claimed_user = if_not_exists(claimed_user, :claimed_user), "
        expression_attribute_data["claimed_user"] = expression_attribute_values[":claimed_user"] = Decimal(0)

    update_expression = update_expression.rstrip(", ")

    return update_expression, expression_attribute_names, expression_attribute_values, expression_attribute_data
    
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
        return User.from_dict(items[0]) if items else User()
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
        return User.from_dict(items[0]) if items else User()
    except ClientError as e:
        current_app.logger.error(f"Error getting user by identity_id: {str(e)}")
        return None

def get_unclaimed_users(query: Optional[Dict[str, Any]] = None) -> List[User]:
    current_app.logger.debug(f"Querying for unclaimed users with query: {query}")
    try:
        key_condition_expression = None
        filter_expression = None
        index_name = None

        if query and 'primaryPersona' in query:
            # Use primary_persona-index if primaryPersona is provided
            index_name = 'primary_persona-index'
            key_condition_expression = Key('primary_persona').eq(query['primaryPersona']) & Key('claimed_user').eq(Decimal(0))
            
            # Add age_range filter if provided
            if 'ageRange' in query:
                filter_expression = Attr('age_range').eq(query['ageRange'])
        elif query and 'ageRange' in query:
            # Use age_range-index if only ageRange is provided
            index_name = 'age_range-index'
            key_condition_expression = Key('age_range').eq(query['ageRange'])&Key('claimed_user').eq(Decimal(0))
        else:
            # Use claimed-index if neither primaryPersona nor ageRange is provided
            index_name = 'claimed-index'
            key_condition_expression = Key('claimed_user').eq(0)

        query_params = {
            'IndexName': index_name,
            'KeyConditionExpression': key_condition_expression,
        }

        if filter_expression:
            query_params['FilterExpression'] = filter_expression
        current_app.logger.debug(f"query_params is {query_params}")


        response = User.table.query(**query_params)
        users = [User.from_dict(item) for item in response.get('Items', [])]

        # Pagination handling
        while 'LastEvaluatedKey' in response:
            query_params['ExclusiveStartKey'] = response['LastEvaluatedKey']
            response = User.table.query(**query_params)
            users.extend([User.from_dict(item) for item in response.get('Items', [])])

        # Additional filtering for secondary persona if needed
        if query and 'secondaryPersona' in query:
            users = [user for user in users if query['secondaryPersona'] in user.persona]

        current_app.logger.debug(f"Found {len(users)} unclaimed users")
        return users
    except ClientError as e:
        current_app.logger.error(f"Error getting unclaimed users: {str(e)}")
        return []

def get_random_user(count: int) -> List[User]:
    unclaimed_users = get_unclaimed_users()
    current_app.logger.debug(f"Found {len(unclaimed_users)} unclaimed users")
    return random.sample(unclaimed_users, min(count, len(unclaimed_users)))


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