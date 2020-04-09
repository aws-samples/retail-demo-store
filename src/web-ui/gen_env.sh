#!/bin/bash

# This script is called during the build stage in CodePipeline to generate the 
# .env file based off environment variables. The .env file is loaded by the 
# web-ui service to set its configuration.

set -e

# Delete .env if it exists
[ -e ".env" ] && rm .env

printf 'VUE_APP_PRODUCTS_SERVICE_DOMAIN=%s\n' "$PRODUCTS_SERVICE_URL" >> .env
printf 'VUE_APP_PRODUCTS_SERVICE_PORT=%s\n' "80" >> .env
printf 'VUE_APP_USERS_SERVICE_DOMAIN=%s\n' "$USERS_SERVICE_URL" >> .env
printf 'VUE_APP_USERS_SERVICE_PORT=%s\n' "80" >> .env
printf 'VUE_APP_CARTS_SERVICE_DOMAIN=%s\n' "$CARTS_SERVICE_URL" >> .env
printf 'VUE_APP_CARTS_SERVICE_PORT=%s\n' "80" >> .env
printf 'VUE_APP_ORDERS_SERVICE_DOMAIN=%s\n' "$ORDERS_SERVICE_URL" >> .env
printf 'VUE_APP_ORDERS_SERVICE_PORT=%s\n' "80" >> .env
printf 'VUE_APP_RECOMMENDATIONS_SERVICE_DOMAIN=%s\n' "$RECOMMENDATIONS_SERVICE_URL" >> .env
printf 'VUE_APP_RECOMMENDATIONS_SERVICE_PORT=%s\n' "80" >> .env
printf 'VUE_APP_SEARCH_SERVICE_DOMAIN=%s\n' "$SEARCH_SERVICE_URL" >> .env
printf 'VUE_APP_SEARCH_SERVICE_PORT=80\n' >> .env
printf 'VUE_APP_AWS_REGION=%s\n' "$DEPLOYED_REGION" >> .env
printf 'VUE_APP_AWS_IDENTITY_POOL_ID=%s\n' "$COGNITO_IDENTITY_POOL_ID" >> .env
printf 'VUE_APP_AWS_USER_POOL_ID=%s\n' "$COGNITO_USER_POOL_ID" >> .env
printf 'VUE_APP_AWS_USER_POOL_CLIENT_ID=%s\n' "$COGNITO_USER_POOL_CLIENT_ID" >> .env
printf 'VUE_APP_WEB_ROOT_URL=%s\n' "$WEB_ROOT_URL" >> .env
printf 'VUE_APP_IMAGE_ROOT_URL=%s\n' "$IMAGE_ROOT_URL" >> .env
printf 'VUE_APP_BOT_NAME=%s\n' "RetailDemoStore" >> .env
printf 'VUE_APP_BOT_ALIAS=%s\n' "development" >> .env
printf 'VUE_APP_BOT_REGION=%s\n' "$DEPLOYED_REGION" >> .env
printf 'VUE_APP_PINPOINT_APP_ID=%s\n' "$PINPOINT_APP_ID" >> .env
printf 'VUE_APP_PINPOINT_REGION=%s\n' "$DEPLOYED_REGION" >> .env
printf 'VUE_APP_PERSONALIZE_TRACKING_ID=%s\n' "$PERSONALIZE_TRACKING_ID" >> .env

printf 'VUE_APP_AMPLITUDE_API_KEY=%s\n' "$AMPLITUDE_API_KEY" >> .env