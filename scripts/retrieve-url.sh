#!/bin/bash

region="$1"
stack_name="$2"
output_key="$3"

aws cloudformation describe-stacks \
  --stack-name "$stack_name" \
  --region "$region" \
  --query "Stacks[0].Outputs[?OutputKey=='$output_key'].OutputValue" \
  --output text
