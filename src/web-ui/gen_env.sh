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
printf 'VUE_APP_LOCATION_SERVICE_DOMAIN=%s\n' "$LOCATION_SERVICE_URL" >> .env
printf 'VUE_APP_LOCATION_SERVICE_PORT=80\n' >> .env
printf 'VUE_APP_SEARCH_SERVICE_DOMAIN=%s\n' "$SEARCH_SERVICE_URL" >> .env
printf 'VUE_APP_SEARCH_SERVICE_PORT=80\n' >> .env
printf 'VUE_APP_VIDEOS_SERVICE_DOMAIN=%s\n' "$VIDEOS_SERVICE_URL" >> .env
printf 'VUE_APP_VIDEOS_SERVICE_PORT=80\n' >> .env
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
printf 'VUE_APP_LOCATION_RESOURCE_NAME=%s\n' "$LOCATION_RESOURCE_NAME" >> .env
printf 'VUE_APP_LOCATION_NOTIFICATION_URL=%s\n' "$LOCATION_NOTIFICATION_URL" >> .env
printf 'VUE_APP_AMAZON_PAY_PUBLIC_KEY_ID=%s\n' "$AMAZON_PAY_PUBLIC_KEY_ID" >> .env
printf 'VUE_APP_AMAZON_PAY_STORE_ID=%s\n' "$AMAZON_PAY_STORE_ID" >> .env
printf 'VUE_APP_AMAZON_PAY_MERCHANT_ID=%s\n' "$AMAZON_PAY_MERCHANT_ID" >> .env

printf 'VUE_APP_AMPLITUDE_API_KEY=%s\n' "$AMPLITUDE_API_KEY" >> .env
printf 'VUE_APP_OPTIMIZELY_SDK_KEY=%s\n' "$OPTIMIZELY_SDK_KEY" >> .env
printf 'VUE_APP_SEGMENT_WRITE_KEY=%s\n' "$SEGMENT_WRITE_KEY" >> .env

printf 'VUE_APP_GOOGLE_ANALYTICS_ID=%s\n' "$GOOGLE_ANALYTICS_ID" >> .env

printf 'VUE_APP_MPARTICLE_API_KEY=%s\n' "$MPARTICLE_API_KEY" >> .env
printf 'VUE_APP_MPARTICLE_SECRET_KEY=%s\n' "$MPARTICLE_SECRET_KEY" >> .env

# Layer0
printf 'VUE_APP_LAYER0_ENABLED=false\n' >> .env

# Fenix Settings variables
printf 'VUE_APP_FENIX_TENANT_ID=%s\n' "$FENIX_TENANT_ID" >> .env
printf 'VUE_APP_FENIX_ZIP_DETECT_URL=%s\n' "$FENIX_ZIP_DETECT_URL" >> .env
printf 'VUE_APP_FENIX_EDD_ENDPOINT=%s\n' "$FENIX_EDD_ENDPOINT" >> .env
printf 'VUE_APP_FENIX_MONETARY_VALUE=%s\n' "$FENIX_MONETARY_VALUE" >> .env
printf 'VUE_APP_FENIX_ENABLED_PDP=%s\n' "$FENIX_ENABLED_PDP" >> .env
printf 'VUE_APP_FENIX_ENABLED_CART=%s\n' "$FENIX_ENABLED_CART" >> .env
printf 'VUE_APP_FENIX_ENABLED_CHECKOUT=%s\n' "$FENIX_ENABLED_CHECKOUT" >> .env
