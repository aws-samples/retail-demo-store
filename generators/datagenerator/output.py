# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from datagenerator.segment import SegmentIdentifyEvent, SegmentTrackEvent, SegmentSender
from datagenerator.amplitude import AmplitudeIdentifyEvent, AmplitudeTrackEvent, AmplitudeSender
from datagenerator.file import FileEvent

# TODO: Add Personalize output file formatter
# TODO: Add Amplitude output formatter

class OutputFormatter:
  def __init__(self, timestamp, user, platform, properties, name = None):
    self.event = name
    self.timestamp = timestamp
    self.user = user
    self.properties = properties
    self.platform = platform

  def amplitude_identify(self):
    return AmplitudeIdentifyEvent(self.timestamp, self.user, self.platform)

  def amplitude_event(self):
    return AmplitudeTrackEvent(self.event, self.timestamp, self.user, self.platform, self.properties)

  def segment_track(self):
    return SegmentTrackEvent(self.event, self.timestamp, self.user, self.platform, self.properties)

  def segment_identify(self):
    return SegmentIdentifyEvent(self.timestamp, self.user, self.platform)

  def file_event(self):
    return FileEvent(self.event, self.timestamp, self.user, self.platform, self.properties)

class OutputWriter:
  def __init__(self, sessions):
    self.sessions = sessions

  def to_file(self, file_name):
    # Write to the specified file using the FileEvent output formatter
    f = open(file_name, 'w')
    for funnel in self.sessions:
      for formatter in funnel:
        event = formatter.file_event()
        f.write(event.str())
  
  def to_amplitude(self, config, debug=False):
    sender = AmplitudeSender(config)
    print(f'Send config is: {config}.')
    count = 0
    for funnel in self.sessions:
      batch =[]
      count += 1
      for formatter in funnel:
        if funnel.identify:
         # Send an identify call if specified in the funnel
          event = formatter.amplitude_identify()
          batch.append(event)
        event = formatter.amplitude_event()
        batch.append(event)
      if len(batch) > 0:
        response = sender.send_batch(funnel.platform, batch, debug)
        if response != None and response.status_code > 200:
          print(f'Error sending to Amplitude: {response.text}')
    print(f'Processed {count} funnels...') 

  def to_segment(self, config_file, debug=False):
    # Write to Segment, using the specified config file
    sender = SegmentSender('segment_config.yaml')
    print(f'Send config is: {sender.config_keys}')
    count = 0
    for funnel in self.sessions:
      batch = []
      count += 1
      for formatter in funnel:
        if funnel.identify:
          # Send an identify call if specified in the funnel
          event = formatter.segment_identify()
          batch.append(event)
        event = formatter.segment_track()
        batch.append(event)
      if len(batch) > 0:
        response = sender.send_batch(funnel.platform, batch, debug)
        if response != None and response.status_code > 200:
          print(f'Error sending to Segment: {response.text}')
    print(f'Processed {count} funnels...')