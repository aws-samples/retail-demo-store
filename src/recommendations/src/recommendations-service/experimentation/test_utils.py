# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import unittest
import numpy as np
import json

from experimentation.utils import CompatEncoder
from decimal import Decimal

class TestCompatEncoder(unittest.TestCase):

    def test_numpy(self):
        a = np.zeros(5)

        dict = {
            'this': 'that',
            'array': a
        }

        json.dumps(dict, cls=CompatEncoder)

    def test_decimal(self):
        dict = {
            'this': 'that',
            'dec': Decimal(12.54)
        }

        json.dumps(dict, cls=CompatEncoder)