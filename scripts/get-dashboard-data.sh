#!/bin/bash

bucket_name="prm-pracmig-metrics-dev"
metrics_dir_path="src/data/metrics/"
mkdir -p "${metrics_dir_path}"
aws s3api get-object --bucket "${bucket_name}" --key "migrations.json" "${metrics_dir_path}/migrations.json" > /dev/null
