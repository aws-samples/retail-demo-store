# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import datetime
from collections import UserList
from datagenerator.funnel import Funnel
import random
import numpy as np

class Sessions(UserList):
  def __init__(self, from_datetime, to_datetime, event_templates, num_sessions, user_pool):
    # defines % users for each 24 hour time slot, starting at midnight
    self.percent_users = (1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 19, 20, 20, 9, 5, 4, 3, 1, 1, 1, 1, 1)
    self.event_templates = event_templates
    self.num_sessions = num_sessions
    # Parse out the start date and turn it into a datetime - YYYY-mm-dd format
    self.from_datetime = from_datetime
    self.to_datetime = to_datetime
    self.data = []

    for hourly_users in self.user_time_slots():
      for i in range(hourly_users[1]):
        active_user = np.random.binomial(1, .5)
        user = user_pool.user(active_user)
        # Pick a random funnel - note that the same user can repeat the same funnel several times potentially
        funnel = random.choice(self.event_templates)  
        self.data.append(Funnel(hourly_users[0], funnel, user))

  # Generates a series of datetime stamps for events (default every minute from start)
  def user_time_slots(self):
    curr = self.from_datetime
    while curr < self.to_datetime:
      yield (curr, int(self.num_sessions * (self.percent_users[curr.hour] / 100)))
      curr += datetime.timedelta(hours=1)