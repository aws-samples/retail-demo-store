#!/bin/bash

# This script is called during the build stage in CodePipeline to generate the 
# .env file based off environment variables. The .env file is loaded by the 
# web-ui service to set its configuration.

set -e

# Delete .env if it exists
[ -e ".env" ] && rm .env

printf 'VUE_APP_PRODUCTS_SERVICE_DOMAIN=%s\n' "https://products.retail-store.retail.sa.aws.dev" >> .env
printf 'VUE_APP_PRODUCTS_SERVICE_PORT=%s\n' "443" >> .env
printf 'VUE_APP_USERS_SERVICE_DOMAIN=%s\n' "https://users.retail-store.retail.sa.aws.dev" >> .env
printf 'VUE_APP_USERS_SERVICE_PORT=%s\n' "443" >> .env
printf 'VUE_APP_CARTS_SERVICE_DOMAIN=%s\n' "https://carts.retail-store.retail.sa.aws.dev" >> .env
printf 'VUE_APP_CARTS_SERVICE_PORT=%s\n' "443" >> .env
printf 'VUE_APP_ORDERS_SERVICE_DOMAIN=%s\n' "https://orders.retail-store.retail.sa.aws.dev" >> .env
printf 'VUE_APP_ORDERS_SERVICE_PORT=%s\n' "443" >> .env
printf 'VUE_APP_RECOMMENDATIONS_SERVICE_DOMAIN=%s\n' "https://recommendations.retail-store.retail.sa.aws.dev" >> .env
printf 'VUE_APP_RECOMMENDATIONS_SERVICE_PORT=%s\n' "443" >> .env
printf 'VUE_APP_WAYPOINT_SERVICE_DOMAIN=%s\n' "https://waypoint.retail-store.retail.sa.aws.dev" >> .env
printf 'VUE_APP_WAYPOINT_SERVICE_PORT=443\n' >> .env
printf 'VUE_APP_SEARCH_SERVICE_DOMAIN=%s\n' "https://search.retail-store.retail.sa.aws.dev" >> .env
printf 'VUE_APP_SEARCH_SERVICE_PORT=443\n' >> .env
printf 'VUE_APP_VIDEOS_SERVICE_DOMAIN=%s\n' "https://videos.retail-store.retail.sa.aws.dev" >> .env
printf 'VUE_APP_VIDEOS_SERVICE_PORT=443\n' >> .env
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
printf 'VUE_APP_WAYPOINT_RESOURCE_NAME=%s\n' "$WAYPOINT_RESOURCE_NAME" >> .env
printf 'VUE_APP_WAYPOINT_NOTIFICATION_URL=%s\n' "$WAYPOINT_NOTIFICATION_URL" >> .env
printf 'VUE_APP_AMAZON_PAY_PUBLIC_KEY_ID=%s\n' "$AMAZON_PAY_PUBLIC_KEY_ID" >> .env
printf 'VUE_APP_AMAZON_PAY_STORE_ID=%s\n' "$AMAZON_PAY_STORE_ID" >> .env
printf 'VUE_APP_AMAZON_PAY_MERCHANT_ID=%s\n' "$AMAZON_PAY_MERCHANT_ID" >> .env

printf 'VUE_APP_AMPLITUDE_API_KEY=%s\n' "$AMPLITUDE_API_KEY" >> .env
printf 'VUE_APP_OPTIMIZELY_SDK_KEY=%s\n' "$OPTIMIZELY_SDK_KEY" >> .env
printf 'VUE_APP_SEGMENT_WRITE_KEY=%s\n' "$SEGMENT_WRITE_KEY" >> .env