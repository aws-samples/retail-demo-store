# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import datagenerator
import json
import requests
import yaml

# Amplitude event support
# This follows the Amplitude V2 HTTP Bulk API spec, here:
# https://help.amplitude.com/hc/en-us/articles/360032842391-HTTP-API-V2
#
# These classes accept a user, platform, and general event properties and map them 
# into an Amplitude API compatible represenation.

class AmplitudeEvent:
  def __init__(self, timestamp, user, platform):
    self.time = int(timestamp.timestamp() * 1000) # Amplitude time is milliseconds since epoch
    self.user_id = f'{user.id:0>5}'  # Amplitude user ID is a string type, min length is 5 which is weird

    platform_data = user.get_platform_data(platform)
    self.device_id = platform_data['anonymous_id']
    if platform == 'ios':
        self.idfa = platform_data['advertising_id']
        self.platform = 'iOS'
        self.device_model = platform_data['model']
        self.os_version = platform_data['version']
    elif platform == 'android':
        self.adid = platform_data['advertising_id']
        self.device_model = platform_data['model']
        self.os_version = platform_data['version']

  def toJson(self):
        return self.__repr__()

  def __repr__(self):
    return json.dumps(self.__dict__)

class AmplitudeIdentifyEvent(AmplitudeEvent):
  def __init__(self, timestamp, user, platform):
    super().__init__(timestamp, user, platform)
    self.event_type = '$identify'
    self.user_properties = user.traits
    self.user_properties['name'] = user.name
    self.user_properties['email'] = user.email
    self.user_properties['age'] = user.age
    self.user_properties['gender'] = user.gender
    self.user_properties['persona'] = user.persona
    self.user_properties['username'] = user.username

class AmplitudeTrackEvent(AmplitudeEvent):
  def __init__(self, name, timestamp, user, platform, properties):
    super().__init__(timestamp, user, platform)
    self.event_type = name
    self.event_properties = properties

class AmplitudeSender:
  def __init__(self, config):
    self.config = config # MUST BE:  { 'api_key': <Amplitude API Key> }
    self.endpoint = 'https://api.amplitude.com/2/httpapi'

  def send_batch(self, platform, events, debug=False):
    batch_events = {
      "api_key": self.config['api_key'],
      "events": events
    }

    events_str = json.dumps(batch_events, default=lambda x: x.__dict__) 
    #print(f'Batch length bytes: {len(events_str)}')
    if debug:
      parsed = json.loads(events_str)
      print(f'{json.dumps(parsed, indent=4)}')
      response = None
    else:
      response = requests.post(self.endpoint, 
        data=events_str)
      #print(self.config_keys[platform])
      #print(json.dumps(batch_events, default=lambda x: x.__dict__))
      #print(f'Sent {len(batch_events["batch"])} events and got {response}')
    return response
