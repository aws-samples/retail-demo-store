#!/bin/bash

# Deploy to AWS with all default values. 
# You can use the following flags to pre create resources
#
# Example usage
# ./scripts/deploy-cloudformation-stacks.sh S3_BUCKET REGION [--pre-create-personalize] [--pre-index-elasticsearch]
#

set -e

########################################################################################################################################
# Parse arguments and flag
########################################################################################################################################
# The script parses the command line argument and extract these variables:
# 1. "args" contains an array of arguments (e.g. args[0], args[1], etc.) In this script, we use only 2 arguments (S3_BUCKET, REGION)
# 2. "pre_create_personalize" contains a boolean value whether "--pre-create-personalize" is presented 
# 3. "pre_index_elasticsearch" contains a boolean value whether "--pre-index-elasticsearch" is presented
########################################################################################################################################
args=()
pre_create_personalize=false
pre_index_elasticsearch=false

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
        if [ "$bool" == "pre-create-personalize" ]
        then
            pre_create_personalize=true
            echo Received a \"--pre-create-personalize\" flag. Will create personalize resources after deployment
        elif [ "$bool" == "pre-index-elasticsearch" ]
        then
            pre_index_elasticsearch=true
            echo Received a \"--pre-create-personalize\" flag. Will index ElasticSearch after deployment
        else
            echo Received an unknown flag \"$bool\"
            exit 1
        fi
      else
        # value=$1
        shift
        # echo \"$arg\" is flag with value \"$value\"
      fi
    else
      args+=("$arg")
      shift
      echo Received argument \"$arg\"
    fi
done

S3_BUCKET=${args[0]}
REGION=${args[1]}
STACK_NAME=${args[2]}

echo "=============================================="
echo "Executing the script with following arguments:"
echo "=============================================="
echo "S3_BUCKET = ${S3_BUCKET}"
echo "pre_create_personalize = ${pre_create_personalize}"
echo "pre_index_elasticsearch = ${pre_index_elasticsearch}"
echo "=============================================="

param_personalize="No"
param_elasticsearch="No"

if [ "$pre_create_personalize" = true ]; then
    param_personalize="Yes"
fi

if [ "$pre_index_elasticsearch" = true ]; then
    param_elasticsearch="Yes"
fi

aws cloudformation deploy \
  --template-file ./aws/cloudformation-templates/template.yaml \
  --stack-name ${STACK_NAME} \
  --capabilities CAPABILITY_NAMED_IAM \
  --region "${REGION}" \
  --parameter-overrides \
  ResourceBucket="${S3_BUCKET}" \
  SourceDeploymentType="CodeCommit" \
  AlexaSkillId="" \
  AlexaDefaultSandboxEmail="" \
  ResourceBucketRelativePath="" \
  mParticleSecretKey="" \
  AmazonPayPublicKeyId="" \
  mParticleApiKey="" \
  mParticleS2SSecretKey="" \
  mParticleS2SApiKey="" \
  mParticleOrgId="" \
  GoogleAnalyticsMeasurementId="" \
  PinpointSMSLongCode="" \
  PinpointEmailFromAddress="" \
  SegmentWriteKey="" \
  AmazonPayPrivateKey="" \
  AmazonPayStoreId="" \
  AmazonPayMerchantId="" \
  OptimizelySdkKey="" \
  GitHubToken="" \
  AmplitudeApiKey="" \
  CreateOpenSearchServiceLinkedRole="No" \
  ACMCertificateArn="" \
  PreCreatePersonalizeResources="${param_personalize}" \
  PreIndexElasticsearch="${param_elasticsearch}" \
  ResourceBucketImages="" \
  ResourceBucketImagesPrefix=""
  


# Wait until stack creation completes
aws cloudformation wait stack-create-complete \
  --region "${REGION}" \
  --stack-name "${STACK_NAME}"


[ $? -eq 255 ] && {
  echo "timeout aws cloudformation wait stack-create-complete.. waiting another iteration..."
  # Wait until stack creation completes
  aws cloudformation wait stack-create-complete \
    --region "${REGION}" \
    --stack-name "${STACK_NAME}"
}
