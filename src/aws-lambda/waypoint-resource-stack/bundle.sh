#!/bin/bash
set -e

pip () {
    command pip3 "$@"
}

LAMBDA_SOURCE=waypoint-resource-stack.py
PACKAGE_FILE=waypoint-resource-stack.zip

echo "Cleaning up intermediate files"
[ -e ${PACKAGE_FILE} ] && rm ${PACKAGE_FILE}
[ -e "package" ] && rm -rf package
[ -e "tmp" ] && rm -rf tmp

echo "Installing Lambda dependencies"
pip install -r requirements.txt --target ./package
pip install boto3 --target ./package
# While we don't have access to a pre-packaged version of Botocore with the latest Waypoint SDK, the script manually adds it to the package
echo "Manually adding Waypoint service description to botocore"
mkdir -p package/botocore/data/location/2020-11-19
cp service-description/service-2.json package/botocore/data/location/2020-11-19/service-2.json

echo "Building Lambda deployment package"
cd package
zip -r9 ${OLDPWD}/${PACKAGE_FILE} .
cd ${OLDPWD}

echo "Adding Lambda function source code to package"
zip -g ${PACKAGE_FILE} ${LAMBDA_SOURCE}


echo "Done!"