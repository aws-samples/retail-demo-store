#!/bin/bash

# Staging script for copying deployment resources to an S3 bucket. The resources
# copied here are used as part of the deployment process for this project as 
# as some runtime dependencies such as product images and seed data for loading 
# products and categories into DDB and CSVs for training Personalize models.

set -e 

BUCKET=$1
#Path with trailing /
S3PATH=$2

if [ ! -d "local" ]; then
    mkdir local
fi
touch local/stage.log

if [ "$BUCKET" == "" ]; then
    echo "Usage: $0 BUCKET [S3PATH]"
    echo "  where BUCKET is the S3 bucket to upload resources to and S3PATH is optional path but if specified must have a trailing '/'"
    exit 1
fi

BUCKET_LOCATION="$(aws s3api get-bucket-location --bucket ${BUCKET}|grep ":"|cut -d\" -f4)"
if [ -z "$BUCKET_LOCATION" ]; then
    BUCKET_DOMAIN="s3.amazonaws.com"
else
    BUCKET_DOMAIN="s3-${BUCKET_LOCATION}.amazonaws.com"
fi

# Remove Mac desktop storage files so they don't get packaged & uploaded
find . -name '.DS_Store' -type f -delete

echo " + Staging to $BUCKET in $S3PATH"

echo " + Uploading CloudFormation Templates"
aws s3 cp aws/cloudformation-templates/ s3://${BUCKET}/${S3PATH}cloudformation-templates --recursive --quiet
echo " For CloudFormation : https://${BUCKET_DOMAIN}/${BUCKET}/${S3PATH}cloudformation-templates/template.yaml"

echo " + Packaging Notebooks"
[ -e "retaildemostore-notebooks.zip" ] && rm retaildemostore-notebooks.zip
zip -qr retaildemostore-notebooks.zip ./workshop/ -x "*.DS_Store" "*.ipynb_checkpoints*" "*.csv"

echo " + Uploading Notebooks"
aws s3 cp retaildemostore-notebooks.zip s3://${BUCKET}/${S3PATH}notebooks/retaildemostore-notebooks.zip

echo " + Packaging Source"
[ -e "retaildemostore-source.zip" ] && rm retaildemostore-source.zip
zip -qr retaildemostore-source.zip ./src/ -x "*.DS_Store" "*__pycache__*" "*/aws-lambda/*" "*/node_modules/*" "*.zip"

echo " + Uploading Source"
aws s3 cp retaildemostore-source.zip s3://${BUCKET}/${S3PATH}source/retaildemostore-source.zip

echo " + Upload seed data"
aws s3 cp src/products/src/products-service/data/ s3://${BUCKET}/${S3PATH}data --recursive 
aws s3 cp src/users/src/users-service/data/ s3://${BUCKET}/${S3PATH}data --recursive

# Sync CSVs used for Personalize pre-create campaign Lambda function
echo " + Copying CSVs for Personalize model pre-create training"
aws s3 sync s3://theglobalstore-code/csvs s3://${BUCKET}/${S3PATH}csvs --only-show-errors

# Stage AWS Lambda functions
echo " + Staging AWS Lambda functions"

for function in retaildemostore-lambda-load-products elasticsearch-pre-index personalize-pre-create-campaigns personalize-delete-resources pinpoint-recommender
do
    echo "  + Staging $function"
    cd src/aws-lambda/$function
    chmod +x ./stage.sh
    ./stage.sh ${BUCKET} ${S3PATH} > ../../../local/stage.log
    cd -
done

# Sync product images
echo " + Copying product images"
aws s3 sync ./images s3://${BUCKET}/${S3PATH}images --only-show-errors

echo " + Done s3://${BUCKET}/${S3PATH} "
echo " For CloudFormation : https://${BUCKET_DOMAIN}/${BUCKET}/${S3PATH}cloudformation-templates/template.yaml"
