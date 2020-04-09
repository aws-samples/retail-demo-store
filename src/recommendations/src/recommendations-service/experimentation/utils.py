# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
import numpy as np
import decimal

class CompatEncoder(json.JSONEncoder):
    """ Compatible encoder that supports numpy types and Decimal type

    json.dumps(data, cls=CompatEncoder)
    """
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, decimal.Decimal):
            if obj % 1 > 0:
                return float(obj)
            else:
                return int(obj)
        else:
            return super(CompatEncoder, self).default(obj)
