# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

# AWS X-ray support
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.ext.flask.middleware import XRayMiddleware
from aws_xray_sdk.core import patch_all

patch_all()

xray_recorder.begin_segment("Videos-init")

import logging
import json
import os
import pathlib
import pprint
import subprocess
import threading
import time

import boto3
import srt
from flask import Flask, jsonify, Response
from flask_cors import CORS


# -- Environment variables - defined by CloudFormation when deployed
VIDEO_BUCKET = os.environ.get('RESOURCE_BUCKET')
SSM_VIDEO_CHANNEL_MAP_PARAM = os.environ.get('PARAMETER_IVS_VIDEO_CHANNEL_MAP', 'retaildemostore-ivs-video-channel-map')

USE_DEFAULT_IVS_STREAMS = os.environ.get('USE_DEFAULT_IVS_STREAMS') == 'true'

DEFAULT_THUMB_FNAME = 'default_thumb.png'
STATIC_FOLDER = '/app/static'
STATIC_URL_PATH = '/static'
SUBTITLE_FORMAT = 'srt'
LOCAL_VIDEO_DIR = '/app/video-files/'
DEFAULT_STREAMS_CONFIG_S3_PATH = 'videos/default_streams/default_streams.json'

# -- Parameterised ffmpeg commands
FFMPEG_STREAM_CMD = """ffmpeg -loglevel panic -hide_banner -re -stream_loop -1 -i \"{video_filepath}\" \
                           -r 30 -c:v copy -f flv rtmps://{ingest_endpoint}:443/app/{stream_key} -map 0:s -f {subtitle_format} -"""
FFMPEG_SUBS_COMMAND = "ffmpeg -i \"{video_filepath}\" \"{subtitle_path}\""


# Globally accessed variable to store stream metadata (URLs & associated product IDs). Returned via `stream_details`
# endpoint
stream_details = {}

ivs_client = boto3.client('ivs')
ssm_client = boto3.client('ssm')
s3_client = boto3.client('s3')


# -- Load default streams config
def load_default_streams_config():
    app.logger.info(f"Downloading default streams config from from bucket {VIDEO_BUCKET} with key {DEFAULT_STREAMS_CONFIG_S3_PATH}.")

    config_response = s3_client.get_object(Bucket=VIDEO_BUCKET, Key=DEFAULT_STREAMS_CONFIG_S3_PATH)
    config = json.loads(config_response['Body'].read().decode('utf-8'))
    for (key, entry) in config.items():
        app.logger.info(f"{key}, {entry}")
        config[key] = {**entry, 'thumb_url': STATIC_URL_PATH + '/' + entry['thumb_fname']}
        config[key].pop('thumb_fname', None)

    app.logger.info("Pulled config:")
    app.logger.info(config)

    return config


# -- Video streaming
def download_video_file(s3_key):
    """
        Downloads a video file and associated thumbnail from S3. Thumbnails are identified by a .png file with the same
        name and in the same location as the video.
    """
    local_path = LOCAL_VIDEO_DIR + s3_key.split('/')[-1]
    app.logger.info(f"Downloading file {s3_key} from bucket {VIDEO_BUCKET} to {local_path}.")
    s3_client.download_file(Bucket=VIDEO_BUCKET, Key=s3_key, Filename=local_path)
    app.logger.info(f"File {s3_key} downloaded from bucket {VIDEO_BUCKET} to {local_path}.")

    thumbnail_path = None
    thumbnail_key = '.'.join(s3_key.split('.')[:-1]) + '.png'
    try:
        local_thumbnail_fname = thumbnail_key.split('/')[-1]
        local_thumbnail_path = app.static_folder + '/' + local_thumbnail_fname
        s3_client.download_file(Bucket=VIDEO_BUCKET, Key=thumbnail_key, Filename=local_thumbnail_path)
        app.logger.info(f"File {thumbnail_key} downloaded from bucket {VIDEO_BUCKET} to {local_thumbnail_path}.")
        thumbnail_path = app.static_url_path + '/' + local_thumbnail_fname
    except Exception as e:
        app.logger.warning(f'No thumbnail available for {VIDEO_BUCKET}/{s3_key} as {VIDEO_BUCKET}/{thumbnail_key} - '
                           f'exception: {e}')
    return local_path, thumbnail_path


def get_ffmpeg_stream_cmd(video_filepath, ingest_endpoint, stream_key, subtitle_format):
    """
        Returns the command to start streaming a video using ffmpeg.
    """
    return FFMPEG_STREAM_CMD.format(**locals())


def get_ffmpeg_subs_cmd(video_filepath, subtitle_path):
    """
        Returns the ffmpeg command to rip subtitles (ie. metadata) from a video file.
    """
    return FFMPEG_SUBS_COMMAND.format(**locals())


def get_featured_products(video_filepath, channel_id):
    """
        Extracts a list of product IDs from the metadata attached to a video file. The values are saved in the global
        `stream_details` dict.
    """
    subtitle_path = pathlib.Path(video_filepath).with_suffix('.srt')
    get_subs_command = get_ffmpeg_subs_cmd(video_filepath, subtitle_path)
    process = subprocess.run(
                    get_subs_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, shell=True)
    with open(subtitle_path) as f:
        subtitle_content = srt.parse(f)
        for line in subtitle_content:
            product_id = json.loads(line.content)['productId']
            if 'products' not in stream_details[channel_id]:
                stream_details[channel_id]['products'] = [product_id]
            else:
                if product_id not in stream_details[channel_id]['products']:
                    stream_details[channel_id]['products'].append(product_id)


def is_ssm_parameter_set(parameter_name):
    """
        Returns whether an SSM parameter with a given name has been set (ie. value is not 'NONE')
    """
    try:
        response = ssm_client.get_parameter(Name=parameter_name)
        return response['Parameter']['Value'] != 'NONE'
    except ssm_client.exceptions.ParameterNotFound:
        return False


def log_ffmpeg_processes():
    app.logger.info('Running ffmpeg processes:')
    app.logger.info(os.system("ps aux|grep 'PID\|ffmpeg'"))


def put_ivs_metadata(channel_arn, line):
    """
        Sends metadata to a given IVS stream. Metadata can be any string, but the AWS Retail Demo Store UI expects
        metadata of the format {"productId":"<product-id>"}
    """
    try:
        app.logger.info(f'Sending metadata to stream: {line}')
        ivs_client.put_metadata(
            channelArn=channel_arn,
            metadata=line
        )
    except ivs_client.exceptions.ChannelNotBroadcasting as ex:
        app.logger.warning(f'Channel not broadcasting. Waiting for 5 seconds. Exception: {ex}')
        log_ffmpeg_processes()
        time.sleep(5)
    except ivs_client.exceptions.InternalServerException as ex:
        app.logger.error(f'We have an internal error exception. Waiting for 30 seconds. Exception: {ex}')
        log_ffmpeg_processes()
        time.sleep(30)


def get_stream_state(channel_arn):
    """
        Returns the state of a stream given it's ARN. One of 'LIVE', 'OFFLINE' (from API response)
        or 'NOT_BROADCASTING' (inferred).
    """
    try:
        stream_response = ivs_client.get_stream(channelArn=channel_arn)['stream']
        stream_state = stream_response['state']
    except ivs_client.exceptions.ChannelNotBroadcasting:
        stream_state = "NOT_BROADCASTING"
    return stream_state


def start_streams():
    """
        Initiates all IVS streams based on environment variables. If the SSM_VIDEO_CHANNEL_MAP_PARAM (map of videos in
        S3 to IVS channels) is set and the user has not requested to use the default IVS streams
        (USE_DEFAULT_IVS_STREAMS, defined by CloudFormation input) then one stream will be started per video described
        in the video to IVS channel map. Each stream runs in a separate thread.

        If streams are not started, then `stream_details` will be set to the details of a collection of existing streams
    """
    if is_ssm_parameter_set(SSM_VIDEO_CHANNEL_MAP_PARAM) and not USE_DEFAULT_IVS_STREAMS:
        video_channel_param_value = ssm_client.get_parameter(Name=SSM_VIDEO_CHANNEL_MAP_PARAM)['Parameter']['Value']
        app.logger.info(f"Found IVS channel map: {video_channel_param_value}")
        video_channel_map = json.loads(video_channel_param_value)

        for idx, (s3_video_key, ivs_channel_arn) in enumerate(video_channel_map.items()):
            threading.Thread(target=stream, args=(s3_video_key, ivs_channel_arn, idx)).start()

    else:
        global stream_details
        stream_details = load_default_streams_config()


def stream(s3_video_key, ivs_channel_arn, channel_id):
    """
        Starts the stream for a given video file and IVS channel. The video file is streamed on a loop using ffmpeg, and
        any attached metadata (from the subtitles embedded in the video file) is sent to the channel's `put_metadata`
        endpoint.
    """
    video_filepath, thumb_url = download_video_file(s3_video_key)
    if thumb_url is None:
        thumb_url = app.static_url_path + '/' + DEFAULT_THUMB_FNAME

    channel_response = ivs_client.get_channel(arn=ivs_channel_arn)['channel']
    ingest_endpoint = channel_response['ingestEndpoint']
    playback_endpoint = channel_response['playbackUrl']
    stream_details[channel_id] = {'playback_url': playback_endpoint,
                                  'thumb_url': thumb_url}

    get_featured_products(video_filepath, channel_id)

    stream_state = get_stream_state(ivs_channel_arn)
    stream_arn = ivs_client.list_stream_keys(channelArn=ivs_channel_arn)['streamKeys'][0]['arn']
    stream_key = ivs_client.get_stream_key(arn=stream_arn)['streamKey']['value']
    app.logger.info(f"Stream details:\nIngest endpoint: {ingest_endpoint}\nStream state: {stream_state}")

    if SUBTITLE_FORMAT == 'srt':
        while True:
            if stream_state != "NOT_BROADCASTING":
                app.logger.info(f"Stream {stream_arn} is currently in state {stream_state}. Waiting for state NOT_BROADCASTING")
                sleep_time = 20
                app.logger.info(f"Waiting for {sleep_time} seconds")
                time.sleep(sleep_time)
                stream_state = get_stream_state(ivs_channel_arn)
                continue

            app.logger.info('Starting video stream')
            ffmpeg_stream_cmd = get_ffmpeg_stream_cmd(video_filepath, ingest_endpoint, stream_key, SUBTITLE_FORMAT)
            app.logger.info(f'ffmpeg command: {ffmpeg_stream_cmd}')

            process = subprocess.Popen(
                ffmpeg_stream_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, shell=True)
            app.logger.info('Running ffmpeg processes:')
            app.logger.info(os.system("ps aux|grep 'PID\|ffmpeg'"))

            lines = iter(process.stdout)
            app.logger.info('Starting event stream')
            while True:
                try:
                    int(next(lines).strip())
                    time_range = next(lines).strip()
                    if not '-->' in time_range:
                        raise ValueError(f'Expected a time range instead of {time_range}')
                    send_text = ''
                    while True:
                        text = next(lines).strip()
                        if len(text) == 0: break
                        if len(send_text)>0: send_text+='\n'
                        send_text += text
                    put_ivs_metadata(ivs_channel_arn, send_text)
                except StopIteration:
                    app.logger.warning('Video iteration has stopped unexpectedly. Attempting restart in 10 seconds.')
                    time.sleep(10)
                    break
    else:
        raise NotImplementedError(f'{SUBTITLE_FORMAT} is not currently supported by this demo.')
# -- End Video streaming


# -- Logging
class LoggingMiddleware(object):
    def __init__(self, app):
        self._app = app

    def __call__(self, environ, resp):
        errorlog = environ['wsgi.errors']
        pprint.pprint(('REQUEST', environ), stream=errorlog)

        def log_response(status, headers, *args):
            pprint.pprint(('RESPONSE', status, headers), stream=errorlog)
            return resp(status, headers, *args)

        return self._app(environ, log_response)
# -- End Logging


# -- Exceptions
class BadRequest(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


# -- Handlers
app = Flask(__name__,
            static_folder=STATIC_FOLDER,
            static_url_path=STATIC_URL_PATH)
corps = CORS(app)


xray_recorder.configure(service='Videos Service')
XRayMiddleware(app, xray_recorder)

@app.errorhandler(BadRequest)
def handle_bad_request(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route('/')
def index():
    return 'Videos Service'


@app.route('/stream_details')
def streams():
    response_data = []
    for value in stream_details.values():
        response_data.append(value)
    response = {
        "streams": response_data
    }
    return Response(json.dumps(response), content_type = 'application/json')


@app.route('/health')
def health():
    return 'OK'


if __name__ == '__main__':
    app.wsgi_app = LoggingMiddleware(app.wsgi_app)
    app.logger.setLevel(level=logging.INFO)

    app.logger.info(f"VIDEO_BUCKET: {VIDEO_BUCKET}")
    app.logger.info(f"SSM_VIDEO_CHANNEL_MAP_PARAM: {SSM_VIDEO_CHANNEL_MAP_PARAM}")
    app.logger.info(f"USE_DEFAULT_IVS_STREAMS: {USE_DEFAULT_IVS_STREAMS}")

    app.logger.info("Starting video streams")
    start_streams()

    app.logger.info("Starting API")
    app.run(debug=False, host='0.0.0.0', port=80)
