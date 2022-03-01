#!/bin/bash

set -eo pipefail

BUCKET_ROOT_NAME=metric-calculator-deployments
ENV=dev
BUCKET_NAME="${BUCKET_ROOT_NAME}-${ENV}"

chalice package build

if aws s3api head-bucket --bucket "${BUCKET_NAME}" 2>&1 | grep -q 'Not Found'
then
  aws s3api create-bucket \
    --bucket "${BUCKET_NAME}" \
    --acl private \
    --create-bucket-configuration '{ "LocationConstraint": "eu-west-2" }'
  aws s3api wait bucket-exists --bucket "${BUCKET_NAME}"
  aws s3api put-public-access-block \
    --bucket "${BUCKET_NAME}" \
    --public-access-block-configuration BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
fi

aws cloudformation package \
  --template-file build/sam.json \
  --s3-bucket "${BUCKET_NAME}" \
  --output-template-file "./build/packaged-cf.json" \
  --use-json
aws cloudformation deploy \
  --template-file "./build/packaged-cf.json" \
  --stack-name "metrics-calculator-${ENV}" \
  --capabilities CAPABILITY_IAM

# Outputs to use in tfvars on the metrics calculator stack
JSON=$(cat "./build/packaged-cf.json")
echo "${JSON}" | jq .Resources.CalculateDashboardMetricsFromTelemetry.Properties.Handler
echo "${JSON}" | jq .Resources.CalculateDashboardMetricsFromTelemetry.Properties.CodeUri