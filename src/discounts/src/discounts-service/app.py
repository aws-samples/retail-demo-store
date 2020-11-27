# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from flask import Flask
from flask import abort, jsonify, request
from flask_cors import CORS

import json
import pprint

discounts = []


def load_discounts():
    global discounts
    with open('data/discounts.json') as f:
        discounts = json.load(f)


# -- Logging
class LoggingMiddleware(object):
    def __init__(self, app):
        self._app = app

    def __call__(self, environ, resp):
        errorlog = environ['wsgi.errors']
        pprint.pprint(('REQUEST', environ), stream=errorlog)

        def log_response(status, headers, *args):
            pprint.pprint(('RESPONSE', status, headers), stream=errorlog)
            return resp(status, headers, *args)

        return self._app(environ, log_response)
# -- End Logging


# -- Handlers
app = Flask(__name__)
corps = CORS(app)


@app.route('/')
def index():
    return 'Discounts Service'


@app.route('/discounts')
def get_discounts():
    return jsonify({'tasks': discounts})


@app.route('/discounts/<discount_id>')
def get_discount(discount_id):
    for discount in discounts:
        if discount['id'] == int(discount_id):
            return jsonify({'task': discount})
    abort(404)


if __name__ == '__main__':
    app.wsgi_app = LoggingMiddleware(app.wsgi_app)

    load_discounts()
    app.run(debug=True, host='0.0.0.0', port=80)