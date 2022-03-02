#!/bin/bash

aws lambda invoke \
  --cli-binary-format raw-in-base64-out \
  --function-name "metrics_calculator" \
  --payload "{\"oldAsid\": \"493013391039\", \"newAsid\": \"200000032719\", \"odsCode\": \"H84032\"}" \
  metrics_calculator_output.txt