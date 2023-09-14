# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)