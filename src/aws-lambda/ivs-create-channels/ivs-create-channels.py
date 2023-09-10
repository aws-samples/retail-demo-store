# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
from crhelper import CfnResource
import boto3
import botocore.exceptions

import json
import logging
import os
import re
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

helper = CfnResource()

SSM_VIDEO_CHANNEL_MAP_PARAM = os.environ.get('ssm_video_channel_map_param')
S3_BUCKET = os.environ.get('bucket')
VIDEO_PATH = os.environ.get('videos_path')

ivs_client = boto3.client('ivs')
ssm_client = boto3.client('ssm')
s3_client = boto3.client('s3')


def is_ssm_parameter_set(parameter_name):
    """
        Returns boolean stating whether an SSM parameter with a given name has been set (ie. value is not 'NONE').
    """
    try:
        response = ssm_client.get_parameter(Name=parameter_name)
        return response['Parameter']['Value'] != 'NONE'
    except ssm_client.exceptions.ParameterNotFound:
        return False


def list_video_file_keys():
    """
        Returns the S3 keys of all .mkv files in the 'video path' of the staging S3 bucket.
    """
    objects = s3_client.list_objects_v2(Bucket=S3_BUCKET, Prefix=VIDEO_PATH)['Contents']
    # TODO: Ensure the fact we are only handling mkv files is captured in the README
    video_file_keys = [s3_object['Key'] for s3_object in objects if s3_object['Key'].endswith('.mkv')]
    return video_file_keys


def channel_config_exists(video_s3_key):
    """
        Returns boolean stating whether an IVS channel already has a value (ie. a video file to IVS channel association)
        in the SSM_VIDEO_CHANNEL_MAP_PARAM.
    """
    if not is_ssm_parameter_set(SSM_VIDEO_CHANNEL_MAP_PARAM):
        return False

    video_channel_param_value = ssm_client.get_parameter(Name=SSM_VIDEO_CHANNEL_MAP_PARAM)['Parameter']['Value']
    video_channel_map = json.loads(video_channel_param_value)

    if video_s3_key in video_channel_map:
        return True
    return False


def channel_exists(arn):
    """
        Returns boolean stating whether an IVS channel with given ARN exists.
    """
    try:
        ivs_client.get_channel(arn=arn)
        return True
    except ivs_client.exceptions.ResourceNotFoundException:
        return False


def remove_channel(arn):
    """
        Stops and removes all resources for a given IVS channel. This is done by:
            1. Deleting all stream keys from the channel to prevent any further streaming to the channel.
            2. Calling the `stop_stream` endpoint on the channel.
            3. Deleting the channel itself.
    """
    logger.info(f'Deleting channel {arn}')

    try:
        logger.info(f"Retrieving stream keys for channel {arn}")
        stream_keys = ivs_client.list_stream_keys(channelArn=arn)['streamKeys']
        logger.info(f"Found stream keys {stream_keys} for channel {arn}")
        for stream_key in stream_keys:
            logger.info(f"Deleting stream key {stream_key['arn']}")
            ivs_client.delete_stream_key(arn=stream_key['arn'])
            logger.info(f"Stream key {stream_key['arn']} deleted")
    except ivs_client.exceptions.ResourceNotFoundException:
        logger.info(f"IVS channel {arn} not found, no stream keys to delete")

    try:
        logger.info(f"Stopping stream for IVS channel {arn}")
        ivs_client.stop_stream(channelArn=arn)
        logger.info(f"Stream stopped for IVS channel {arn}")
    except ivs_client.exceptions.ResourceNotFoundException:
        logger.info(f"IVS channel {arn} not found, nothing to delete")
        return
    except ivs_client.exceptions.ChannelNotBroadcasting:
        logger.info(f"IVS channel {arn} is not broadcasting.")

    try:
        logger.info(f"Deleting channel {arn}")
        ivs_client.delete_channel(arn=arn)
        logger.info(f"IVS channel {arn} deleted")
    except ivs_client.exceptions.ResourceNotFoundException:
        logger.info(f"IVS channel {arn} not found, nothing to delete")
        

def get_video_channel(video_s3_key):
    """
        Returns the IVS channel ARN for a given S3 video key.
    """
    if not is_ssm_parameter_set(SSM_VIDEO_CHANNEL_MAP_PARAM):
        return None

    video_channel_param_value = ssm_client.get_parameter(Name=SSM_VIDEO_CHANNEL_MAP_PARAM)['Parameter']['Value']
    video_channel_map = json.loads(video_channel_param_value)
    return video_channel_map.get(video_s3_key)


@helper.create
def create_ivs_channels(event, _):
    """
        Creates IVS channels. One channel is created per video in the 'video path' of the S3 staging bucket. A mapping
        of video to channel ARN is stored in SSM.
    """
    video_file_keys = list_video_file_keys()
    logger.info(f"Found video file keys: {video_file_keys}")

    for video_file_key in video_file_keys:
        if channel_config_exists(video_file_key):
            video_channel_arn = get_video_channel(video_file_key)
            if channel_exists(video_channel_arn):
                logger.info(f"Video with key {video_file_key} is already associated with IVS channel {video_channel_arn}")
                continue
        
        # Note: IVS does not mind identical channel names and accepts the below characters
        channel_name = 'retail-demo-store-' + \
                       re.subn(r"[^A-z|0-9|\-]", '', video_file_key+'-'+datetime.now().isoformat())[0][:127]
        logger.info(f"Creating IVS channel for video {video_file_key} with name {channel_name}")

        try:
            created_channel_arn = ivs_client.create_channel(name=channel_name, latencyMode='NORMAL')['channel']['arn']
            logger.info(f"IVS channel created with ARN {created_channel_arn}")

            if is_ssm_parameter_set(SSM_VIDEO_CHANNEL_MAP_PARAM):
                video_channel_param_value = ssm_client.get_parameter(Name=SSM_VIDEO_CHANNEL_MAP_PARAM)['Parameter']['Value']
                video_channel_map = json.loads(video_channel_param_value)

                video_channel_map[video_file_key] = created_channel_arn

                ssm_client.put_parameter(
                    Name=SSM_VIDEO_CHANNEL_MAP_PARAM,
                    Value=json.dumps(video_channel_map),
                    Type='String',
                    Overwrite=True
                )
    
            else:
                ssm_client.put_parameter(
                    Name=SSM_VIDEO_CHANNEL_MAP_PARAM,
                    Value=json.dumps({video_file_key: created_channel_arn}),
                    Type='String',
                    Overwrite=True
                )
        except botocore.exceptions.EndpointConnectionError:
            logger.error("Could not create any IVS channels - probably because IVS is not supported in region. "
                         f"Channel name: {channel_name}. Region: {ivs_client.meta.region_name}")


@helper.update
def update_channels(event, _):
    """
        Updates IVS channels. If a video in the 'video path' of the S3 staging bucket does not have an associated
        channel then it will be created. If a config entry is present for a video file which no longer exists in the
        channel & associated config entry will be removed.
    """
    create_ivs_channels(event, _)

    video_channel_param_value = ssm_client.get_parameter(Name=SSM_VIDEO_CHANNEL_MAP_PARAM)['Parameter']['Value']
    video_channel_map = json.loads(video_channel_param_value)
    video_file_keys = list_video_file_keys()

    deleted_video_keys = []
    for video_path, channel_arn in video_channel_map.items():
        if video_path not in video_file_keys:
            logger.info(f"Video with key {video_path} no longer exists. Associated IVS channel {channel_arn} will be deleted")
            remove_channel(channel_arn)
            deleted_video_keys.append(video_path)

    if deleted_video_keys:
        for video_key in deleted_video_keys:
            del video_channel_map[video_key]

        ssm_client.put_parameter(
            Name=SSM_VIDEO_CHANNEL_MAP_PARAM,
            Value=json.dumps(video_channel_map),
            Type='String',
            Overwrite=True
        )


@helper.delete
def delete_all_channels(event, _):
    """
        Deletes all IVS channels referenced in the SSM_VIDEO_CHANNEL_MAP_PARAM.
    """
    logger.info("Deleting all IVS channels in stack")
    if is_ssm_parameter_set(SSM_VIDEO_CHANNEL_MAP_PARAM):
        video_channel_param_value = ssm_client.get_parameter(Name=SSM_VIDEO_CHANNEL_MAP_PARAM)['Parameter']['Value']
        video_channel_map = json.loads(video_channel_param_value)
    else:
        logger.info("No channels to delete")
        return

    new_video_channel_map = {}
    for video_path, channel_arn in video_channel_map.items():
        try:
            remove_channel(channel_arn)
        except ivs_client.exceptions.ConflictException as ex:
            new_video_channel_map[video_path] = channel_arn
            logger.error(f'Could not delete {channel_arn} - probably still streaming.'
                         f'. Exception: {ex}')

    ssm_client.put_parameter(
        Name=SSM_VIDEO_CHANNEL_MAP_PARAM,
        Value="NONE" if len(new_video_channel_map)==0 else json.dumps(new_video_channel_map),
        Type='String',
        Overwrite=True
    )


def lambda_handler(event, context):
    logger.info('ENVIRONMENT VARIABLES')
    logger.info(os.environ)
    logger.info('EVENT')
    logger.info(event)

    helper(event, context)
