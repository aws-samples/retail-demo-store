#!/bin/bash

# ******* Dependencies ********
# This script requires the following local dependencies before the 
# Lambda function can be successfully compiled.
#
# 1. Install golang locally
#    https://golang.org/doc/install
# 2. Install dependencies of the Lambda function
#    $ go get github.com/aws/aws-lambda-go/lambda
#    $ go get github.com/aws/aws-lambda-go/cfn
#    $ go get github.com/aws/aws-sdk-go
#    $ go get gopkg.in/yaml.v2

BUCKET=$1
#Path with trailing /
S3PATH=$2

if [ "${BUCKET}" == "" ]; then
    echo "Usage: $0 BUCKET [S3PATH]"
    echo "  where S3_BUCKET is the S3 bucket to upload resources to and S3_PATH is optional path but if specified must have a trailing '/'"
    exit 1
fi

# Script will fail if error
set -e

mkdir -p bin
# for go compile for lambda

echo "building..."
cd bin
GOARCH=amd64 GOOS=linux go build ../src/main.go
echo "packaging..."

zip retaildemostore-lambda-load-products.zip main
#echo "uploading..."

echo Uploading to s3://$BUCKET/${S3PATH}aws-lambda/retaildemostore-lambda-load-products.zip
aws s3 cp retaildemostore-lambda-load-products.zip s3://$BUCKET/${S3PATH}aws-lambda/ $S3PUBLIC