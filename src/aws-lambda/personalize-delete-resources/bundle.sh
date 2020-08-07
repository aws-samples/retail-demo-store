#!/bin/bash
set -e 

LAMBDA_SOURCE=personalize-delete-resources.py
PACKAGE_FILE=personalize-delete-resources.zip

echo "Cleaning up intermediate files"
[ -e ${PACKAGE_FILE} ] && rm ${PACKAGE_FILE}
[ -e "models" ] && rm -rf models
[ -e "package" ] && rm -rf package

echo "Installing Lambda dependencies"
pip install -r requirements.txt --target ./package

echo "Building Lambda deployment package"
cd package
zip -r9 ${OLDPWD}/${PACKAGE_FILE} .
cd ${OLDPWD}

echo "Downloading Personalize SDK model files"
wget -q https://raw.githubusercontent.com/boto/botocore/e22aad94ba9f33bda7a0abea3a959fb1af56b25d/botocore/data/personalize-runtime/2018-05-22/service-2.json -P ./models/personalize-runtime/2018-05-22
wget -q https://raw.githubusercontent.com/boto/botocore/e22aad94ba9f33bda7a0abea3a959fb1af56b25d/botocore/data/personalize/2018-05-22/service-2.json -P ./models/personalize/2018-05-22

echo "Adding Lambda function source code to package"
zip -g ${PACKAGE_FILE} ${LAMBDA_SOURCE}
zip -gr ${PACKAGE_FILE} models

echo "Done!"