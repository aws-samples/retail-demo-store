#!/bin/bash
set -e 

LAMBDA_SOURCE=segment-personalize-events-destination.py
PACKAGE_FILE=segment-personalize-events-destination.zip

echo "Cleaning up intermediate files"
[ -e ${PACKAGE_FILE} ] && rm ${PACKAGE_FILE}
[ -e "package" ] && rm -rf package

echo "Adding Lambda function source code to package"
zip -g ${PACKAGE_FILE} ${LAMBDA_SOURCE}

echo "Done!"