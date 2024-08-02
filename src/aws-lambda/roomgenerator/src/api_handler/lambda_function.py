import os
from typing import Any
from enum import StrEnum
from pathlib import PurePath
import boto3
from botocore.exceptions import ClientError
from aws_lambda_powertools.event_handler.exceptions import UnauthorizedError, NotFoundError, BadRequestError
from aws_lambda_powertools.event_handler import APIGatewayHttpResolver, Response, content_types
from aws_lambda_powertools.event_handler.openapi.exceptions import RequestValidationError
from aws_lambda_powertools.event_handler.middlewares import NextMiddleware
from aws_lambda_powertools import Logger, Metrics
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.utilities.typing import LambdaContext
from pydantic import BaseModel
from room_generator.db import RoomGenerationRequests

input_image_bucket = os.environ['INPUT_IMAGE_BUCKET']
signed_s3_url_expiry = os.environ.get('SIGNED_S3_URL_EXPIRY', 600)

def populate_user_sub(app: APIGatewayHttpResolver, next_middleware: NextMiddleware) -> Response:
    """
    Middleware to extract user sub from cognito and add to context
    """
    cognito_amr = app.current_event.request_context.authorizer.iam.cognito_amr
    cognito_signin = [sign_in for sign_in in cognito_amr if "CognitoSignIn" in sign_in]
    _, _, user_sub = cognito_signin[0].split(":")
    app.append_context(user_sub=user_sub)
    app.append_context(user_identity=app.current_event.request_context.authorizer.iam.cognito_identity_id)
    
    result = next_middleware(app)

    return result

app = APIGatewayHttpResolver(enable_validation=True)
app.use(middlewares=[populate_user_sub]) 

dynamodb = boto3.resource('dynamodb')
db = RoomGenerationRequests(dynamodb.Table(os.environ['DYNAMODB_TABLE_NAME']))
s3_client = boto3.client('s3')

logger = Logger(utc=True)
metrics = Metrics()

Style = StrEnum('Style', ['minimalist', 'cozy', 'bohemian', 'modern', 'rustic', 'industrial', 'scandanavian'])

class RoomGenerationRequest(BaseModel):
    """
    Represents the room generation request submitted from the frontend
    Args:
        s3_key (str): The s3 key under which the original room image was uploaded
        style (Style): The style to transform the room into 
    """
    s3_key: str
    style: Style

@app.exception_handler(RequestValidationError)  
def handle_validation_error(ex: RequestValidationError) -> Response:
    """
    Validation Error handler
    Returns http status code 422 for room request validation errors
    """
    logger.error("Request failed validation", path=app.current_event.path, errors=ex.errors())

    return Response(
        status_code=422,
        content_type=content_types.APPLICATION_JSON,
        body="Invalid data",
    )

def __verify_s3_key(s3_key: str) -> None:
    """
    S3 Key should be of format: private/{token.sub}/{uuid}/filename.suffix
    Performs a number of verification checks on the S3 key:
    1. The key conforms to the expected key format
    2. The current user matches token.sub
    3. The image exists
    Raises the following excepts if validation fails 
     - Not Found if the room image does not exist
     - Bad request error if key format incorrect
     - Not authorized error if there is a user identity mismatch
    """
    path = PurePath(s3_key)
    if len(path.parts) != 4 or path.parts[0] != 'private':
        raise BadRequestError(f"S3 key should be of format private/token.sub/uuid/filename, received: {s3_key}")
    if path.parts[1] != app.context['user_identity']:
        raise UnauthorizedError(f"Unauthorized access to image path: {s3_key}")

    try:
        s3_client.head_object(
            Bucket=input_image_bucket,
            Key=s3_key)
    except ClientError as error:
        if error.response['Error']['Code'] == 'NoSuchKey':
            logger.info(f"Image was not uploaded to s3: {s3_key}")
            raise NotFoundError(f"Image: {s3_key} not found in S3")
    
@app.post("/rooms")
def create_room(request: RoomGenerationRequest):
    __verify_s3_key(request.s3_key)
    
    room_generation_id = db.create(room_owner=app.context['user_sub'], room_style=request.style, image_key=request.s3_key)

    metrics.add_metric(name="RoomRequest", unit=MetricUnit.Count, value=1)
    return {'room_generation_id': room_generation_id}, 201


@app.get("/rooms")
def get_rooms():
    return db.list(app.context['user_sub'])
        
@app.get("/rooms/<id>")
def get_room(id: str):
    room = db.get(id, attrs="id, room_owner, room_state, room_style, prompt, labels, image_key, final_image_key, thumbnail_image_key")
    
    if not room:
        raise NotFoundError('Room details not found')
    
    if app.context['user_sub'] != room['room_owner']:
        raise UnauthorizedError('Unauthorized access')
    
    return room

@metrics.log_metrics(capture_cold_start_metric=True)
def lambda_handler(event: dict[str, Any], context: LambdaContext) -> dict:
    return app.resolve(event, context)