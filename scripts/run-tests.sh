#!/bin/bash

# Get service endpoints and un integration tests.

# Update service endpoint environment variables to match CloudFormation output.
set_env () {
  source .venv/bin/activate
  python3 update_env.py "$1" "$2"
  deactivate
}

cd ../src/run-tests || exit
make setup

# The keys for each service endpoint in CloudFormation.
services=("ProductsServiceUrl" "OrdersServiceUrl" "RecommendationsServiceUrl" "UsersServiceUrl")
# The keys for each service endpoint environment variable used for running tests.
# The indexes of these lists must match so the correct variables get updated.
env_vars=("PRODUCTS_API_URL" "ORDERS_API_URL" "RECOMMENDATIONS_API_URL" "USERS_API_URL")

for i in "${!services[@]}"; do
  endpoint=$(aws cloudformation describe-stacks \
  --region "${REGION}" \
  --stack-name ${STACK_NAME} \
  --query "Stacks[0].Outputs[?OutputKey=='${services[$i]}'].OutputValue" --output text)

  set_env "${env_vars[$i]}" "$endpoint"
done

make integ
make clean
