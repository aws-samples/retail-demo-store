#!/bin/bash
set -e 

LAMBDA_SOURCE=pinpoint-sms-alerts.py
PACKAGE_FILE=pinpoint-sms-alerts.zip

echo "Cleaning up intermediate files"
[ -e ${PACKAGE_FILE} ] && rm ${PACKAGE_FILE}

echo "Building Lambda deployment package"
zip ${PACKAGE_FILE} ${LAMBDA_SOURCE}

echo "Done!"