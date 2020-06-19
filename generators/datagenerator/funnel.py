# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import random
import numpy as np
import datetime
import inspect
from datagenerator.output import OutputFormatter
from collections.abc import Mapping, Iterable

class Funnel:
  def __init__(self, timestamp, funnel, user):
    self.funnel = funnel
    self.event_index = 0
    self.timestamp = timestamp
    self.platform = self.funnel['platform']
    self.user = user

    if 'user_props' in self.funnel:
      self.user.set_traits(self.funnel['user_props'])
      self.identify = True
    else:
      self.identify = False

    if 'state' in self.funnel:
      self.state = self.funnel['state'](self.user)  # Passes the user to the state lambda
    else:
      self.state = None

  def __iter__(self):
    return self

  def __next__(self):
    success_percent = min(100, 50 + (self.event_index * 10)) / 100
    proceed = self.proceed(success_percent)
    at_start = self.event_index == 0
    not_at_end = self.event_index < len(self.funnel['templates'])
    # This is to make sure that you always get at least the first event in a funnel,
    # rest will be stochastic
    if (proceed and not_at_end) or at_start:
      formatter = OutputFormatter(
        self.timestamp, 
        self.user,
        self.platform,
        self.generate_props(self.event_index),
        self.funnel['templates'][self.event_index][0])
      self.timestamp += datetime.timedelta(seconds=random.randint(30, 600))
      self.event_index += 1
      return formatter
    else:
        raise StopIteration

  def generate_props(self, index):
    template = self.funnel['templates'][index]
    props = {}
    for (k,v) in template[1].items():
      if k == 'expand' and callable(v):
        props = {**props, **v(self.state)}
      elif callable(v):
        props[k] = v(self.state)
      elif isinstance(v, Iterable):
        props[k] = random.choice(v)
      else:
        props[k] = v
    return props  
    
  def proceed(self, p):
    return np.random.binomial(1, p)