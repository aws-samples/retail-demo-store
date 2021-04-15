#!/bin/bash

# This script is called during the build stage in CodePipeline.
# It generates ./dist output folder of web-ui Vue application.
# If $XDN_DEPLOY_TOKEN is present it generates ./.xdn output folder for deployment on Moovweb XDN.

if [ $XDN_DEPLOY_TOKEN = "NONE" ]; then
  npm run build
else
  npm run build && npm run xdn:build
fi