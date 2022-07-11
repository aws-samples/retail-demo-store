#!/bin/bash

# Delete CloudFormation stack
#
#
# Example usage
# ./scripts/delete-cloudformation-stacks.sh REGION S3_BUCKET
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