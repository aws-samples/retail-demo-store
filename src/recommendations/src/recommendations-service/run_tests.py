# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import os, sys, unittest

sys.argv += ['discover', os.path.dirname(sys.argv[0]), 'test_*.py']

unittest.main(module=None)