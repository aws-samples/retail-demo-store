#!/bin/bash
set -e 

LAMBDA_SOURCE=mparticle-personalize.js
PACKAGE_FILE=mparticle-personalize.zip

echo "Cleaning up intermediate files"
[ -e ${PACKAGE_FILE} ] && rm ${PACKAGE_FILE}
[ -e "package" ] && rm -rf package
[ -e "node_modules" ] && rm -rf node_modules

npm install

echo "Adding Lambda function source code to package"
zip -g ${PACKAGE_FILE} ${LAMBDA_SOURCE}

echo "Done!"