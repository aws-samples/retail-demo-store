#!/bin/bash

# This script is called during the build stage in CodePipeline.
# It deploys web-ui app on Amazon CloudFront.
# If $XDN_DEPLOY_TOKEN is present it deploys the app on Moovweb XDN.

if [ $XDN_DEPLOY_TOKEN = "NONE" ]; then
  echo Uploading to ${WEB_BUCKET_NAME}
  aws s3 cp --recursive ./dist s3://${WEB_BUCKET_NAME}/ 
  aws s3 cp --cache-control="max-age=0, no-cache, no-store, must-revalidate" ./dist/index.html s3://${WEB_BUCKET_NAME}/
  aws cloudfront create-invalidation --distribution-id ${CLOUDFRONT_DIST_ID} --paths /index.html
else
  echo Uploading to XDN
  npx xdn deploy --skip-build --token=$XDN_DEPLOY_TOKEN
fi