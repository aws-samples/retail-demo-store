import uuid
from pathlib import PurePath
from datetime import datetime, timezone
from boto3.dynamodb.conditions import Key

class RoomGenerationRequests():

    def __init__(self, table):
        self.table = table

    def update(self, id: str, **kwargs):
        if not kwargs:
            raise ValueError("Need to pass at least one attribute to update")
           
        expression_attr_values = {}
        update_expression = []

        if labels := kwargs.get('labels'):
            boxes = [{
                'name': label.name,
                'bounding_box': {key: str(value) for key, value in label.bounding_box.items()},
                'similar_items': [item.id for item in label.similar_items]
            } for label in labels]
            expression_attr_values[':labels'] = boxes
            update_expression.append('labels = :labels')
        if state := kwargs.get('state'):
            expression_attr_values[':state'] = state
            update_expression.append('room_state = :state')
        if prompt := kwargs.get('prompt'):
            expression_attr_values[':prompt'] = prompt
            update_expression.append('prompt = :prompt')
        if final_image_key := kwargs.get('final_image_key'):
            expression_attr_values[':final_image_key'] = final_image_key
            update_expression.append('final_image_key = :final_image_key')
        if task_token := kwargs.get('task_token'):
            expression_attr_values[':task_token'] = task_token
            update_expression.append('task_token = :task_token')
        if thumbnail_image_key := kwargs.get('thumbnail_image_key'):
            expression_attr_values[':thumbnail_image_key'] = thumbnail_image_key
            update_expression.append('thumbnail_image_key = :thumbnail_image_key')

        self.table.update_item(
            Key={'id': id},
            ExpressionAttributeValues=expression_attr_values,
            UpdateExpression=f'SET {",".join(update_expression)}')
    
    # Potentially make the user id part of the key. e.g the sort key
    def get(self, id: str, attrs: str):
        item = self.table.get_item(Key={'id': id}, ProjectionExpression=attrs)
        return item.get('Item')
    
    def create(self, room_owner: str, room_style:str, image_key:str) -> str:
        # Generate a unique id for this room generation request
        room_generation_id = str(uuid.uuid4())

        self.table.put_item(
            Item={
                'id': room_generation_id,
                'room_owner': room_owner,
                'dt': self.__current_date_time(),
                'room_style': room_style,
                'image_key': image_key,
                'image_prefix': self.__get_s3_prefix(image_key),
                'room_state': 'Uploaded'
            })
        return room_generation_id

    def list(self, room_owner: str, size: int = 12):
        return self.table.query(
            IndexName="room_owner-dt-index",
            KeyConditionExpression=Key('room_owner').eq(room_owner),
            ScanIndexForward=False,
            Limit=size
        )['Items']
        
    def __get_s3_prefix(self, s3_key: str) -> str:
        """
        Returns the s3 prefix for the passed in key.
        """    
        return PurePath(s3_key).parents[0].as_posix() + "/"

    def __current_date_time(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")