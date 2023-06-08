#!/bin/bash
set -e 

LAMBDA_SOURCE=index.js
PACKAGE_FILE=apigw-authorizer.zip

echo "Cleaning up intermediate files"
[ -e ${PACKAGE_FILE} ] && rm ${PACKAGE_FILE}
[ -e "node_modules" ] && rm -rf node_modules

echo "Installing Lambda dependencies"
npm install

echo "Building Lambda deployment package"
zip -r9 ${PACKAGE_FILE} node_modules

echo "Adding Lambda function source code to package"
zip -g ${PACKAGE_FILE} ${LAMBDA_SOURCE}

echo "Done!"