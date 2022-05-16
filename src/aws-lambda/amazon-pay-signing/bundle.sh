#!/bin/bash
set -e

LAMBDA_SOURCE=amazon-pay-signing.js
PACKAGE_FILE=amazon-pay-signing.zip

echo "Cleaning up intermediate files"
[ -e ${PACKAGE_FILE} ] && rm ${PACKAGE_FILE}
[ -e "package" ] && rm -rf package

echo "Installing Lambda dependencies"
npm ci 

echo "Building Lambda deployment package"
zip -r9 ${PACKAGE_FILE} . -x "*.sh"

echo "Adding Lambda function source code to package"
zip -g ${PACKAGE_FILE} ${LAMBDA_SOURCE}


echo "Done!"