#!/bin/bash

# Utility script to stage Docker images in a public ECR repository so they can
# referenced in Dockerfile's without depending on Docker Hub (and therefore
# at risk of being rate limited and failing builds).

# Prerequisites:
# 1. Credentials for the Retail Demo Store staging AWS account where public
#    images are staged.
# 2. Your local AWS CLI environment configured with credentials to access
#    the above mentioned account.
# 3. AWS CLI 2.16+ (for ecr-public commands).

set -e

NAMESPACE="s5z3t2n9"
REPO=$1
TAG=$2

if [ "$REPO" == "" ] | [ "$TAG" == "" ]; then
    echo "Usage: $0 REPO TAG"
    echo "  where REPO is the source repository for the image and TAG is the tag for the image"
    exit 1
fi

echo "Pulling and tagging image $REPO:$TAG"
docker pull $REPO:$TAG
docker tag $REPO:$TAG public.ecr.aws/$NAMESPACE/$REPO:$TAG

echo "Authenticating ECR with docker"
aws ecr-public get-login-password --region us-east-1 | docker login --username AWS --password-stdin public.ecr.aws

echo "Pushing image to public ECR repository"
docker push public.ecr.aws/$NAMESPACE/$REPO:$TAG