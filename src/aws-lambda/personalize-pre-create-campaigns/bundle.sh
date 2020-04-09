#!/bin/bash
set -e 

LAMBDA_SOURCE=personalize-pre-create-campaigns.py
PACKAGE_FILE=personalize-pre-create-campaigns.zip

echo "Cleaning up intermediate files"
[ -e ${PACKAGE_FILE} ] && rm ${PACKAGE_FILE}

echo "Adding Lambda function source code to package"
zip ${PACKAGE_FILE} ${LAMBDA_SOURCE}

echo "Done!"