#!/bin/bash

# Delete services.json if it exists
[ -e "src/swagger-ui/services.json" ] && rm src/swagger-ui/services.json

# Replace variables inside template file with environment variables and write output to services.json
envsubst < src/swagger-ui/services.template.json > src/swagger-ui/services.json