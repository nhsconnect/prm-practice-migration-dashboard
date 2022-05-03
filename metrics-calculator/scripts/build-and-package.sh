#!/bin/bash

set -o pipefail

BUCKET_ROOT_NAME=prm-pracmig-metrics-calculator-deployments
ENV=dev
BUCKET_NAME="${BUCKET_ROOT_NAME}-${ENV}"

aws s3api head-bucket --bucket "${BUCKET_NAME}" 2>&1 | grep -q 'Not Found'
BUCKET_EXISTS=$?

set -e

chalice package build/

if [ "${BUCKET_EXISTS}" -ne 1 ]; then
  echo "Deployment bucket does not exist, creating..."
  aws s3api create-bucket \
    --bucket "${BUCKET_NAME}" \
    --acl private \
    --create-bucket-configuration '{ "LocationConstraint": "eu-west-2" }'
  aws s3api wait bucket-exists --bucket "${BUCKET_NAME}"
  aws s3api put-public-access-block \
    --bucket "${BUCKET_NAME}" \
    --public-access-block-configuration BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
else
  echo "Deployment bucket already exists"
fi

aws cloudformation package \
  --template-file build/sam.json \
  --s3-bucket "${BUCKET_NAME}" \
  --output-template-file "./build/packaged-cf.json" \
  --use-json

# Outputs to use in tfvars on the metrics calculator stack
JSON=$(cat "./build/packaged-cf.json")
METRICS_CALC_HANDLER=$(echo "${JSON}" | jq .Resources.CalculateDashboardMetricsFromTelemetry.Properties.Handler | tr -d '"')
SPLUNK_EXPORTER_HANDLER=$(echo "${JSON}" | jq .Resources.SplunkDataExporter.Properties.Handler | tr -d '"')
CODE_URI=$(echo "${JSON}" | jq .Resources.CalculateDashboardMetricsFromTelemetry.Properties.CodeUri | tr -d '"' | cut -c 7-)
OBJECT_KEY="${CODE_URI#*/}"
echo "Merge the below into the metrics calculator stack's Terraform vars file:"
echo "{ \"metrics_calculator_deployment_bucket_name\": \"${BUCKET_NAME}\", \"metrics_calculator_code_key\": \"${OBJECT_KEY}\", \"metrics_calculator_handler_name\": \"${METRICS_CALC_HANDLER}\", \"splunk_data_exporter_handler_name\": \"${SPLUNK_EXPORTER_HANDLER}\" }" | jq
