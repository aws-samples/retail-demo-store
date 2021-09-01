# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import yaml
from collections import UserList

class RDSCatalog(UserList):
  def __init__(self, file):
    self.data = []
    f = open(file)
    self.data = yaml.safe_load(f)

  def subcategory_sample(self, categories):
    return list(filter(lambda item: item['category'] in categories, self.data))