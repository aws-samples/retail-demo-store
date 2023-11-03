# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import logging
import os
from server import app
from handlers import handler_bp
from routes import route_bp

# Set up logging
logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler()])
app.register_blueprint(handler_bp)
app.register_blueprint(route_bp)
# Log a message at the start of the script
app.logger.info('Starting app.py')


if __name__ == '__main__':
    try:
        port = os.getenv('PORT', '80')
        app.run(host='0.0.0.0', port=int(port))
    except Exception as e:
        # Log the error message and the type of the exception
        app.logger.error(f'Error starting server: {str(e)}')
        app.logger.error(f'Type of error: {type(e)}')
