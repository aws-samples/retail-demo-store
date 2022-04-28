#!/bin/bash

# Deploy to AWS with all default values. 
# You can use the following flags to pre create resources
#
# Example usage
# ./scripts/deploy-cloudformation-stacks.sh S3_BUCKET REGION [--pre-create-personalize] [--pre-index-elasticsearch]
#

set -e


REGION="$1"
STACK_NAME="$2"

aws cloudformation delete-stack \
  --region "${REGION}" \
  --stack-name "${STACK_NAME}"

aws cloudformation wait stack-delete-complete \
  --region "${REGION}" \
  --stack-name "${STACK_NAME}"