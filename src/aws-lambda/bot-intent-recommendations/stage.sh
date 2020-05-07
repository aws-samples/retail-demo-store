#!/bin/bash

S3_BUCKET=$1
#Path with trailing /
S3_PATH=$2

if [ "${S3_BUCKET}" == "" ]; then
    echo "Usage: $0 S3_BUCKET [S3_PATH]"
    echo "  where S3_BUCKET is the S3 bucket to upload resources to and S3_PATH is optional path but if specified must have a trailing '/'"
    exit 1
fi

source ./bundle.sh

echo "Staging bundle to S3"
aws s3 cp ${PACKAGE_FILE} s3://${S3_BUCKET}/${S3_PATH}aws-lambda/${PACKAGE_FILE} $S3PUBLIC