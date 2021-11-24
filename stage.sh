#!/bin/bash

# Staging script for copying deployment resources to an S3 bucket. The resources
# copied here are used as part of the deployment process for this project as
# as some runtime dependencies such as product images and seed data for loading
# products and categories into DDB and CSVs for training Personalize models.

set -e

BUCKET=$1
#Path with trailing /
S3PATH=$2

# remove this line if you want to keep the objects private in your S3 bucket
export S3PUBLIC=" --acl public-read"

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
aws s3 cp aws/cloudformation-templates/ s3://${BUCKET}/${S3PATH}cloudformation-templates --recursive $S3PUBLIC
echo " For CloudFormation : https://${BUCKET_DOMAIN}/${BUCKET}/${S3PATH}cloudformation-templates/template.yaml"

echo " + Packaging Source"
[ -e "retaildemostore-source.zip" ] && rm retaildemostore-source.zip
zip -qr retaildemostore-source.zip ./src/ -x "*.DS_Store" "*__pycache__*" "*/aws-lambda/*" "*/node_modules/*" "*.zip"

echo " + Uploading Source"
aws s3 cp retaildemostore-source.zip s3://${BUCKET}/${S3PATH}source/retaildemostore-source.zip $S3PUBLIC

echo " + Upload seed data"
aws s3 cp src/products/src/products-service/data/ s3://${BUCKET}/${S3PATH}data --recursive  $S3PUBLIC
aws s3 cp src/users/src/users-service/data/ s3://${BUCKET}/${S3PATH}data --recursive $S3PUBLIC

echo " + Upload IVS videos"
aws s3 cp videos/ s3://${BUCKET}/${S3PATH}videos --recursive $S3PUBLIC

# Stage AWS Lambda functions
echo " + Staging AWS Lambda functions"

for function in ./src/aws-lambda/*/
do
    echo "  + Staging $function"
    cd $function
    chmod +x ./stage.sh
    ./stage.sh ${BUCKET} ${S3PATH} > ../../../local/stage.log
    cd -
done

# Sync product images
echo " + Copying product images"
aws s3 sync s3://retail-demo-store-code/datasets/1.3/images/  s3://${BUCKET}/${S3PATH}images/ $S3PUBLIC || echo "Skipping load of remote dataset 1.3"
aws s3 sync s3://retail-demo-store-code/datasets/1.4/images/  s3://${BUCKET}/${S3PATH}images/ $S3PUBLIC || echo "Skipping load of remote dataset 1.4"
aws s3 sync datasets/1.4/images/ s3://${BUCKET}/${S3PATH}images/ $S3PUBLIC || echo "Skipping load of local dataset 1.4"

# Sync location data files
echo " + Copying location location data"
aws s3 sync ./location_services s3://${BUCKET}/${S3PATH}location_services --only-show-errors $S3PUBLIC

echo " + Creating CSVs for Personalize model pre-create training"
python3 -m venv .venv
. .venv/bin/activate
pip install -r generators/requirements.txt
PYTHONPATH=. python3 generators/generate_interactions_personalize.py
PYTHONPATH=. python3 generators/generate_interactions_personalize_offers.py

# Sync CSVs used for Personalize pre-create campaign Lambda function
echo " + Copying CSVs for Personalize model pre-create training"
aws s3 sync src/aws-lambda/personalize-pre-create-campaigns/data/  s3://${BUCKET}/${S3PATH}csvs/ $S3PUBLIC

echo " + Done s3://${BUCKET}/${S3PATH} "
echo " For CloudFormation : https://${BUCKET_DOMAIN}/${BUCKET}/${S3PATH}cloudformation-templates/template.yaml"
