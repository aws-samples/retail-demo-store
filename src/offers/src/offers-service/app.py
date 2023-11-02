# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from flask import Flask
from flask import abort, jsonify
from flask_cors import CORS

import json
import pprint

offers = []


def load_offers():
    global offers
    with open('data/offers.json') as f:
        offers = json.load(f)


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
    return 'Offers Service'


@app.route('/offers')
def get_offers():
    return jsonify({'tasks': offers})


@app.route('/offers/<offer_id>')
def get_offer(offer_id):
    for offer in offers:
        if offer['id'] == int(offer_id):
            return jsonify({'task': offer})
    abort(404)


if __name__ == '__main__':
    app.wsgi_app = LoggingMiddleware(app.wsgi_app)

    load_offers()
    app.run(debug=True, host='0.0.0.0', port=80)