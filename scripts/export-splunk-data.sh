#!/bin/bash

aws lambda invoke \
  --cli-binary-format raw-in-base64-out \
  --function-name "splunk_data_exporter" \
  splunk_data_exporter_output.txt