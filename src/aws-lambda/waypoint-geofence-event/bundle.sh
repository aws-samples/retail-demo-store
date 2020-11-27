#!/bin/bash
set -e 

LAMBDA_SOURCE=waypoint-geofence-event.py
PACKAGE_FILE=waypoint-geofence-event.zip

echo "Cleaning up intermediate files"
[ -e ${PACKAGE_FILE} ] && rm ${PACKAGE_FILE}
[ -e "package" ] && rm -rf package

echo "Installing Lambda dependencies"
pip install -r requirements.txt --target ./package

echo "Building Lambda deployment package"
cd package
zip -r9 ${OLDPWD}/${PACKAGE_FILE} .
cd ${OLDPWD}

echo "Adding Lambda function source code to package"
zip -g ${PACKAGE_FILE} ${LAMBDA_SOURCE}

echo "Done!"