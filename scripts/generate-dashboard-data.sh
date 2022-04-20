#!/bin/bash

aws lambda invoke \
  --cli-binary-format raw-in-base64-out \
  --function-name "metrics_calculator" \
  metrics_calculator_output.txt