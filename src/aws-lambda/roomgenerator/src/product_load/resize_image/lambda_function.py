
import boto3
from botocore.exceptions import ClientError
import os
from aws_lambda_powertools.utilities.data_classes import S3BatchOperationEvent, S3BatchOperationResponse, event_source
from aws_lambda_powertools.utilities.typing import LambdaContext
from PIL import Image
import io

s3 = boto3.client("s3")
destination_bucket = os.environ['DESTINATION_BUCKET']
    
@event_source(data_class=S3BatchOperationEvent)
def lambda_handler(event: S3BatchOperationEvent, context: LambdaContext):
    """
    Invoked by S3 Batch operation to resize the image in S3 bucket
    """
    response = S3BatchOperationResponse(event.invocation_schema_version, event.invocation_id, "PermanentFailure")

    task = event.task
    src_key: str = task.s3_key
    src_bucket: str = task.s3_bucket

    try:
        dest_bucket, dest_key = resize(src_bucket, src_key)
        result = task.build_task_batch_response("Succeeded", f"s3://{dest_bucket}/{dest_key}")
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_message = e.response["Error"]["Message"]
        if error_code == "RequestTimeout":
            result = task.build_task_batch_response("TemporaryFailure", "Retry request to Amazon S3 due to timeout.")
        else:
            result = task.build_task_batch_response("PermanentFailure", f"{error_code}: {error_message}")
    except Exception as e:
        result = task.build_task_batch_response("PermanentFailure", str(e))
    finally:
        response.add_result(result)

    return response.asdict()


def resize(src_bucket: str, src_key: str) -> tuple[str, str]:
  """
  Resize the image referenced by src_bucket and src_key
  Returns the destination bucket and key of the resized image.
  """
  # if we just have a folder, then no processing required.
  if src_key.endswith('/'):
    return 'skip', 'skip'
    
  image = fetch_image(src_bucket, src_key)
  max_width = 256
  aspect_ratio = image.height / image.width
  new_height = int(max_width * aspect_ratio)

  # Resize the image
  thumbnail_image = resize_image(image, (max_width,new_height))
  
  s3.put_object(Bucket=destination_bucket, ContentType="image/png", Key=src_key, Body=thumbnail_image)
  
  return destination_bucket, src_key
  
def fetch_image(bucket: str, key: str) -> Image:
  response = s3.get_object(Bucket=bucket, Key=key)
  image_bytes = response["Body"].read()
  return Image.open(io.BytesIO(image_bytes))
  
def resize_image(image, size: tuple[int, int]) -> bytes:
  resized_image = image.resize(size=size)
  buffered = io.BytesIO()
  resized_image.save(buffered, format="PNG")
  return buffered.getvalue()
  
