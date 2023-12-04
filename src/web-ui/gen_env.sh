#!/bin/bash

# This script is called during the build stage in CodePipeline to generate the
# .env file based off environment variables. The .env file is loaded by the
# web-ui service to set its configuration.

set -e

# Delete .env if it exists
[ -e ".env" ] && rm .env

printf 'VITE_PRODUCTS_SERVICE_DOMAIN=%s\n' "$PRODUCTS_SERVICE_URL" >> .env
printf 'VITE_USERS_SERVICE_DOMAIN=%s\n' "$USERS_SERVICE_URL" >> .env
printf 'VITE_CARTS_SERVICE_DOMAIN=%s\n' "$CARTS_SERVICE_URL" >> .env
printf 'VITE_ORDERS_SERVICE_DOMAIN=%s\n' "$ORDERS_SERVICE_URL" >> .env
printf 'VITE_RECOMMENDATIONS_SERVICE_DOMAIN=%s\n' "$RECOMMENDATIONS_SERVICE_URL" >> .env
printf 'VITE_LOCATION_SERVICE_DOMAIN=%s\n' "$LOCATION_SERVICE_URL" >> .env
printf 'VITE_SEARCH_SERVICE_DOMAIN=%s\n' "$SEARCH_SERVICE_URL" >> .env
printf 'VITE_VIDEOS_SERVICE_DOMAIN=%s\n' "$VIDEOS_SERVICE_URL" >> .env
printf 'VITE_AWS_REGION=%s\n' "$DEPLOYED_REGION" >> .env
printf 'VITE_AWS_IDENTITY_POOL_ID=%s\n' "$COGNITO_IDENTITY_POOL_ID" >> .env
printf 'VITE_AWS_USER_POOL_ID=%s\n' "$COGNITO_USER_POOL_ID" >> .env
printf 'VITE_AWS_USER_POOL_CLIENT_ID=%s\n' "$COGNITO_USER_POOL_CLIENT_ID" >> .env
printf 'VITE_WEB_ROOT_URL=%s\n' "$WEB_ROOT_URL" >> .env
printf 'VITE_IMAGE_ROOT_URL=%s\n' "$IMAGE_ROOT_URL" >> .env
printf 'VITE_BOT_NAME=%s\n' "RetailDemoStore" >> .env
printf 'VITE_BOT_ALIAS=%s\n' "development" >> .env
printf 'VITE_BOT_REGION=%s\n' "$DEPLOYED_REGION" >> .env
printf 'VITE_PINPOINT_APP_ID=%s\n' "$PINPOINT_APP_ID" >> .env
printf 'VITE_PINPOINT_REGION=%s\n' "$DEPLOYED_REGION" >> .env
printf 'VITE_PERSONALIZE_TRACKING_ID=%s\n' "$PERSONALIZE_TRACKING_ID" >> .env
printf 'VITE_LOCATION_RESOURCE_NAME=%s\n' "$LOCATION_RESOURCE_NAME" >> .env
printf 'VITE_LOCATION_NOTIFICATION_URL=%s\n' "$LOCATION_NOTIFICATION_URL" >> .env
printf 'VITE_AMAZON_PAY_PUBLIC_KEY_ID=%s\n' "$AMAZON_PAY_PUBLIC_KEY_ID" >> .env
printf 'VITE_AMAZON_PAY_STORE_ID=%s\n' "$AMAZON_PAY_STORE_ID" >> .env
printf 'VITE_AMAZON_PAY_MERCHANT_ID=%s\n' "$AMAZON_PAY_MERCHANT_ID" >> .env
printf 'VITE_BEDROCK_PRODUCT_PERSONALIZATION=%s\n' "$BEDROCK_PRODUCT_PERSONALIZATION" >> .env

printf 'VITE_AMPLITUDE_API_KEY=%s\n' "$AMPLITUDE_API_KEY" >> .env
printf 'VITE_OPTIMIZELY_SDK_KEY=%s\n' "$OPTIMIZELY_SDK_KEY" >> .env
printf 'VITE_SEGMENT_WRITE_KEY=%s\n' "$SEGMENT_WRITE_KEY" >> .env

printf 'VITE_GOOGLE_ANALYTICS_ID=%s\n' "$GOOGLE_ANALYTICS_ID" >> .env

printf 'VITE_MPARTICLE_API_KEY=%s\n' "$MPARTICLE_API_KEY" >> .env
printf 'VITE_MPARTICLE_SECRET_KEY=%s\n' "$MPARTICLE_SECRET_KEY" >> .env

# Layer0
printf 'VITE_LAYER0_ENABLED=false\n' >> .env

# Fenix Settings variables
printf 'VITE_FENIX_TENANT_ID=%s\n' "$FENIX_TENANT_ID" >> .env
printf 'VITE_FENIX_ZIP_DETECT_URL=%s\n' "$FENIX_ZIP_DETECT_URL" >> .env
printf 'VITE_FENIX_EDD_ENDPOINT=%s\n' "$FENIX_EDD_ENDPOINT" >> .env
printf 'VITE_FENIX_MONETARY_VALUE=%s\n' "$FENIX_MONETARY_VALUE" >> .env
printf 'VITE_FENIX_ENABLED_PDP=%s\n' "$FENIX_ENABLED_PDP" >> .env
printf 'VITE_FENIX_ENABLED_CART=%s\n' "$FENIX_ENABLED_CART" >> .env
printf 'VITE_FENIX_ENABLED_CHECKOUT=%s\n' "$FENIX_ENABLED_CHECKOUT" >> .env
printf 'VITE_FENIX_X_API_KEY=%s\n' "$FENIX_X_API_KEY" >> .env