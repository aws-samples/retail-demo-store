#!/bin/bash
set -e 

LAMBDA_SOURCE=pinpoint-auto-workshop.py
PACKAGE_FILE=pinpoint-auto-workshop.zip

echo "Cleaning up intermediate files"
[ -e ${PACKAGE_FILE} ] && rm ${PACKAGE_FILE}
[ -e "pinpoint-templates" ] && rm -rf pinpoint-templates

echo "Copying Pinpoint message templates"
cp -R ../../../workshop/4-Messaging/pinpoint-templates .

echo "Building Lambda deployment package"
zip ${PACKAGE_FILE} ${LAMBDA_SOURCE}
zip -gr ${PACKAGE_FILE} pinpoint-templates

echo "Done!"