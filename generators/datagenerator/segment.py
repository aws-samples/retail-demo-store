# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import datagenerator
import json
import requests

# Segment event support
# This follows the Segment HTTP API spec, here:
# https://segment.com/docs/connections/sources/catalog/libraries/server/http-api/
#
# These classes accept a user, platform, and general event properties and map them 
# a Segment API compatible representation.  This does not support implicit identify 
# traits

class SegmentEvent:
  def __init__(self, timestamp, user, platform):
    self.timestamp = timestamp.isoformat()
    self.sentAt = timestamp.isoformat()
    self.userId = user.id

    context = {
      'library': {
        'version': datagenerator.aws_datagenerator_version,
        'name': 'AWSEventGen'
      }
    }

    platform_data = user.get_platform_data(platform)
    self.anonymousId = platform_data['anonymous_id']
    if platform == 'ios':
      context['device'] = {
        'advertisingId': platform_data['advertising_id'],
        'manufacturer': 'tim_apple',
        'model': platform_data['model'],
        'version': platform_data['version']
      }
    elif platform == 'android':
      context['device'] = {
        'advertisingId': platform_data['advertising_id'],
        'manufacturer': 'google',
        'model': platform_data['model'],
        'version': platform_data['version']
      }
    else:
      context['userAgent'] = platform_data['user_agent']

    self.context = context

    self.integrations = {
        'All': True
    }

  def toJson(self):
        return self.__repr__()

  def __repr__(self):
    return json.dumps(self.__dict__)

class SegmentIdentifyEvent(SegmentEvent):
  def __init__(self, timestamp, user, platform):
    super().__init__(timestamp, user, platform)
    self.type = 'identify'
    self.traits = user.traits
    self.traits['name'] = user.name
    self.traits['email'] = user.email
    self.traits['age'] = user.age
    self.traits['gender'] = user.gender
    self.traits['persona'] = user.persona
    self.traits['username'] = user.username

class SegmentTrackEvent(SegmentEvent):
  def __init__(self, name, timestamp, user, platform, properties):
    super().__init__(timestamp, user, platform)
    self.event = name
    self.type = 'track'
    self.properties = properties

class SegmentSender:
  def __init__(self, config):
   self.config_keys = config # MUST BE: { 'ios': <write key | none>, 'android': <write key | none>, 'web': <write key | none> }
   self.endpoint = 'https://api.segment.io/v1/batch'

  def send_batch(self, platform, events, debug=False):
    batch_events = {
      "batch": events
    }

    key = self.config_keys[platform]
    if key is not None:
      events_str = json.dumps(batch_events, default=lambda x: x.__dict__) 
      #print(f'Batch length bytes: {len(events_str)}')
      if debug:
        parsed = json.loads(events_str)
        print(f'{json.dumps(parsed, indent=4)}')
        response = None
      else:
        response = requests.post(self.endpoint, 
          data=events_str, 
          auth=(self.config_keys[platform], ''))
        #print(self.config_keys[platform])
        #print(json.dumps(batch_events, default=lambda x: x.__dict__))
        #print(f'Sent {len(batch_events["batch"])} events and got {response}')
      return response
    else:
      return None

