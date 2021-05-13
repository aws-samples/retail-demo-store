#!/bin/bash

# This script is called during the build stage in CodePipeline.
# It generates ./dist output folder of web-ui Vue application.
# If $LAYER0_DEPLOY_TOKEN is present it generates ./.layer0 output folder for deployment on Layer0.

if [ $LAYER0_DEPLOY_TOKEN = "NONE" ]; then
  npm run build
else
  npm run build && npm run layer0:build
fi