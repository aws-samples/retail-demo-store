# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

class FileEvent:
  def __init__(self, name, timestamp, user, platform, properties):
    self.event = name
    self.timestamp = timestamp.isoformat()
    self.user_id = user.id
    self.anonymous_id = user.get_platform_data(platform)['anonymous_id']
    self.platform = platform
    self.traits = ''

    if len(user.traits.items()) > 0:
      for (k,v) in user.traits.items():
        self.traits += f',{v}'

  def str(self):
    return self.__repr__()

  def __repr__(self):
    output = f'{self.event},{self.timestamp},{self.user_id},{self.anonymous_id},{self.platform}'
    if len(self.traits) > 0:
      output += self.traits
    output += f'\n'
    return output