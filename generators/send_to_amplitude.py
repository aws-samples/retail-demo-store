# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
import requests
import sys

# Amplitude event support
# This follows the Amplitude V2 HTTP Bulk API spec, here:
# https://help.amplitude.com/hc/en-us/articles/360032842391-HTTP-API-V2
#
# These classes accept a user, platform, and general event properties and map them 
# into an Amplitude API compatible represenation.

amplitude_interactions_file = 'src/aws-lambda/personalize-pre-create-resources/data/amplitude/interactions.json'
conversion_events_file = 'src/aws-lambda/personalize-pre-create-resources/data/amplitude/conversion_events.json'
amplitude_key = 'f6cdf64a6db24778bb9ce82188c19a95'

class AmplitudeSender:
  def __init__(self, config):
    self.config = config # MUST BE:  { 'api_key': <Amplitude API Key> }
    self.endpoint = 'https://api.amplitude.com/2/httpapi'

  def send_batch(self, events, debug=False):
    batch_events = {
      "api_key": self.config['api_key'],
      "events": events
    }

    events_str = json.dumps(batch_events, default=lambda x: x.__dict__) 
    print(f'Batch length bytes: {len(events_str)}')
    if debug:
      parsed = json.loads(events_str)
      #print(f'{json.dumps(parsed, indent=4)}')
      response = None
    else:
      response = requests.post(self.endpoint, 
        data=events_str)
      #print(self.config_keys[platform])
      #print(json.dumps(batch_events, default=lambda x: x.__dict__))
      print(f'Sent {len(batch_events["events"])} events and got {response}')
    return response

def send_file(filename):
    with open(filename, 'r') as events_file:
        sender = AmplitudeSender( { 'api_key': amplitude_key })

        total_event_count = 0
        send_event_count = 0
        events = []
        
        for event in events_file:
            events.append(json.loads(event))
            send_event_count += 1
            total_event_count += 1
            if send_event_count == 1000:
                sender.send_batch(events)
                print(f'sending {len(events)} events')
                events = []
                send_event_count = 0


        if len(events) > 0:
            sender.send_batch(events)
            print(f'sending {len(events)} events')

def get_args(name='default', first='noop'):
    return first

if __name__ == '__main__':
  op = get_args(*sys.argv)
  if op == 'noop':
    print('SENDING EVENTS FILE')
    send_file(amplitude_interactions_file)
  elif op == 'conversion':
    print('SENDING CONVERSIONS FILE')
    send_file(conversion_events_file)
  else:
    print(f'INVALID OPTION {op} - USAGE:  send_to_amplitude.py [conversion - optional]')