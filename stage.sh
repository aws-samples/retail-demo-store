#!/bin/bash

# Staging script for copying deployment resources to an S3 bucket. The resources
# copied here are used as part of the deployment process for this project as
# as some runtime dependencies such as product images and seed data for loading
# products and categories into DDB and CSVs for training Personalize models.
#
# Exammple usage:
# ./stage.sh S3_BUCKET [OPTIONAL_S3_PATH/] [--only-cfn-template] [--skip-generators]
#
# The S3_BUCKET/OPTIONAL_S3_PATH is where all resources and templates will be uploaded.
# If you don't specify the OPTIONAL_S3_PATH, it will be uploaded to the root of the bucket.
#
# The optional flags are:
# 1. "--only-cfn-template" to upload only CloudFormation templates (to speed up development time if you aren't changing any code)
# 2. "--skip-generators" to skip data generator steps

set -e

########################################################################################################################################
# Parse arguments and flag
########################################################################################################################################
# The script parses the command line argument and extract these variables:
# 1. "args" contains an array of arguments (e.g. args[0], args[1], etc.) In this case, we take 2 arguments for BUCKET and S3PATH
#  "private-s3" DEPRECATED. Default behaviour is private_s3=true
# 2. "only-cfn-template" contains a boolean value whether only CloudFormation templates should be copied to staging bucket (default = false).
# 3. "skip-generators" contains a boolean value whether the dataset generators should be skipped or not (default = false).
# 4. "skip-virtualenv" contains a boolean value to be used if stage.sh is called from inside a virtualenv 
########################################################################################################################################
args=()
private_s3=true # this is now on by default.
only_cfn_template=false
skip_generators=false

while [ "$1" ];
do
    arg=$1
    if [ "${1:0:2}" == "--" ]
    then
      shift
      rev=$(echo "$arg" | rev)
      if [ -z "$1" ] || [ "${1:0:2}" == "--" ] || [ "${rev:0:1}" == ":" ]
      then
        bool=$(echo ${arg:2} | sed s/://g)
        if [ "$bool" == "private-s3" ]
        then
            echo Received a \"--private-s3\" flag. this is not now the default behaviour, you don t have to use this parameter anymore
        elif [ "$bool" == "only-cfn-template" ]
        then
            only_cfn_template=true
            echo Received a \"--only-cfn-template\" flag. Will only upload CloudFormation templates.
        elif [ "$bool" == "skip-generators" ]
        then
            skip_generators=true
            echo Received a \"--skip-generators\" flag. Will skip dataset generators.
        elif [ "$bool" == "skip-virtualenv" ]
        then
            # flag is to be used if the script is called from already a specific virtualenv
            skip_virtualenv=true
            echo Received a \"--skip-virtualenv\" flag. Will skip virtualenv inside this script.            
        else
            echo Received an unknown flag \"$bool\"
            exit 1
        fi
      else
        value=$1
        shift
        # echo \"$arg\" is flag with value \"$value\"
      fi
    else
      args+=("$arg")
      shift
      echo Received argument \"$arg\"
    fi
done

BUCKET=${args[0]}
#Path with trailing /
S3PATH=${args[1]}

echo "=============================================="
echo "Executing the script with following arguments:"
echo "=============================================="
echo "BUCKET = ${BUCKET}"
echo "S3PATH = ${S3PATH}"
echo "private-s3 = ${private_s3}"
echo "only-cfn-template = ${only_cfn_template}"
echo "skip-generators = ${skip_generators}"
echo "skip-virtualenv = ${skip_virtualenv}"
echo "=============================================="
########################################################################################################################################

# Add suffix to "s3 cp" commands to upload public objects
# this is left for reference if you REALLY need staged public objects (you probably don't)
if [ "$private_s3" = false ]; then
    export S3PUBLIC=" --acl public-read"
fi

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
    BUCKET_LOCATION="us-east-1"
else
    BUCKET_DOMAIN="s3-${BUCKET_LOCATION}.amazonaws.com"
fi

# Remove Mac desktop storage files so they don't get packaged & uploaded
find . -name '.DS_Store' -type f -delete

echo " + Staging to $BUCKET in $S3PATH"

echo " + Uploading CloudFormation Templates"
aws s3 cp aws/cloudformation-templates/ s3://${BUCKET}/${S3PATH}cloudformation-templates --recursive $S3PUBLIC
echo " For CloudFormation : https://${BUCKET_DOMAIN}/${BUCKET}/${S3PATH}cloudformation-templates/template.yaml"

if [ "$only_cfn_template" = false ]; then
    echo " + Packaging Source"
    [ -e "retaildemostore-source.zip" ] && rm retaildemostore-source.zip
    zip -qr retaildemostore-source.zip ./src/ -x "*.DS_Store" "*__pycache__*" "*/aws-lambda/*" "*/node_modules/*" "*.zip" "*/venv*" "*/.venv*" "*/dist/*" "*/dist-layer0/*"

    echo " + Uploading Source"
    aws s3 cp retaildemostore-source.zip s3://${BUCKET}/${S3PATH}source/retaildemostore-source.zip $S3PUBLIC

    echo " + Upload seed data"
    aws s3 cp src/products/data/ s3://${BUCKET}/${S3PATH}data --recursive  $S3PUBLIC
    aws s3 cp src/users/src/users-service/data/ s3://${BUCKET}/${S3PATH}data --recursive $S3PUBLIC

    echo " + Upload IVS videos"
    aws s3 cp videos/ s3://${BUCKET}/${S3PATH}videos --recursive $S3PUBLIC

    if [ "$skip_generators" = false ]; then
        echo " + Generating CSVs for Personalize model pre-create training"
        if [ "$skip_virtualenv" = false ]; then
            python3 -m venv .venv
            . .venv/bin/activate
        fi
        pip install -r generators/requirements.txt
        PYTHONPATH=. python3 generators/generate_interactions_personalize.py
        PYTHONPATH=. python3 generators/generate_interactions_personalize_offers.py
    else
        echo " + Generators skipped!"
    fi

    # Sync product images
    echo " + Copying local product images (if any)"
    # at deploy time images will be downloaded from https://code.retaildemostore.retail.aws.dev/images.tar.gz
    # this can be configured in the cfn template with the parameter SourceImagesPackage
    aws s3 sync datasets/1.4/images/ s3://${BUCKET}/${S3PATH}images/ $S3PUBLIC || echo "Skipping load of local image dataset 1.4"

    aws s3 sync ./src/videos/src/videos-service/static s3://${BUCKET}/${S3PATH}images/videos/ $S3PUBLIC || echo "Skipping load of local video thumbnails"

    # Sync location data files
    echo " + Copying location location data"
    aws s3 sync ./location_services s3://${BUCKET}/${S3PATH}location_services --only-show-errors $S3PUBLIC

    # Sync CSVs used for Personalize pre-create resources Lambda function
    echo " + Copying CSVs for Personalize model pre-create resources"
    aws s3 sync src/aws-lambda/personalize-pre-create-resources/data/ s3://${BUCKET}/${S3PATH}csvs/ $S3PUBLIC

    # Stage AWS Lambda functions
    echo " + Staging AWS Lambda functions"

    for function in ./src/aws-lambda/*/
    do
        if [ -f ./${function}/stage.sh ]; then
            echo "  + Staging $function"
            cd $function
            chmod +x ./stage.sh
            ./stage.sh ${BUCKET} ${S3PATH} > ../../../local/stage.log
            cd -
        fi
    done
fi
echo " + Done s3://${BUCKET}/${S3PATH} "
echo " Launch CloudFormation stack: https://console.aws.amazon.com/cloudformation/home?region=${BUCKET_LOCATION}#/stacks/create/review?templateURL=https://${BUCKET_DOMAIN}/${BUCKET}/${S3PATH}cloudformation-templates/template.yaml&stackName=retaildemostore&param_ResourceBucket=${BUCKET}"
echo " For CloudFormation : https://${BUCKET_DOMAIN}/${BUCKET}/${S3PATH}cloudformation-templates/template.yaml"


