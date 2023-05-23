#!/bin/bash
set -e 

LAMBDA_SOURCE=pinpoint-offers-recommender.py
PACKAGE_FILE=pinpoint-offers-recommender.zip

echo "Cleaning up intermediate files"
[ -e ${PACKAGE_FILE} ] && rm ${PACKAGE_FILE}
[ -e "package" ] && rm -rf package

echo "Installing Lambda dependencies"
pip install --target ./package requests "urllib3<2"

echo "Building Lambda deployment package"
cd package
zip -r9 ${OLDPWD}/${PACKAGE_FILE} .
cd ${OLDPWD}

echo "Adding Lambda function source code to package"
zip -g ${PACKAGE_FILE} ${LAMBDA_SOURCE}

echo "Done!"