# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import os

from products_service import create_app
from products_service.config import config

config_mode = os.getenv('FLASK_CONFIG') or 'Production'

try:
    app_config = config[config_mode.capitalize()]
except KeyError:
    exit('Error: Invalid <FLASK_CONFIG>. Expected values [Development, Production] ')

app = create_app(app_config)

# Print out the config
if config_mode == 'Development':
    for name, value in app.config.items():
        if not name.startswith('_'):
            app.logger.info(f"{name:<35} =  {value}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=os.getenv('FLASK_RUN_PORT', 8001))