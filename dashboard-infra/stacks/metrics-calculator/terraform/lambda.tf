resource "aws_lambda_function" "metrics_calculator_function" {
  function_name = var.metrics_calculator_function_name
  role          = aws_iam_role.iam_for_lambda.arn
  handler       = var.metrics_calculator_handler_name
  timeout       = 120

  runtime = "python3.9"

  s3_bucket = var.metrics_calculator_deployment_bucket_name
  s3_key    = var.metrics_calculator_code_key

  environment {
    variables = {
      ASID_LOOKUP_BUCKET_NAME = var.asid_lookup_bucket_name
      METRICS_BUCKET_NAME     = var.metrics_bucket_name
      OCCURRENCES_BUCKET_NAME = var.migration_occurrences_bucket_name
      TELEMETRY_BUCKET_NAME   = var.telemetry_bucket_name
    }
  }
}
    }
  }
}

resource "aws_iam_role" "iam_for_lambda" {
  name = "iam_for_lambda"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_policy" "metrics_calculator_function_policy" {
  name        = "AllowMetricsCalculatorS3Access"
  description = "Grant the metrics calculator function the required S3 permissions"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowReadOccurrencesBucket",
      "Effect": "Allow",
      "Action": "s3:ListBucket",
      "Resource": "arn:aws:s3:::${var.migration_occurrences_bucket_name}"
    },
    {
      "Sid": "AllowReadOccurrencesObjects",
      "Effect": "Allow",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::${var.migration_occurrences_bucket_name}/*"
    },
    {
      "Sid": "AllowReadAsidLookupBucket",
      "Effect": "Allow",
      "Action": "s3:ListBucket",
      "Resource": "arn:aws:s3:::${var.asid_lookup_bucket_name}"
    },
    {
      "Sid": "AllowReadAsidLookupObjects",
      "Effect": "Allow",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::${var.asid_lookup_bucket_name}/*"
    },
    {
      "Sid": "AllowReadTelemetryBucket",
      "Effect": "Allow",
      "Action": "s3:ListBucket",
      "Resource": "arn:aws:s3:::${var.telemetry_bucket_name}"
    },
    {
      "Sid": "AllowReadTelemetryObjects",
      "Effect": "Allow",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::${var.telemetry_bucket_name}/*"
    },
    {
      "Sid": "AllowWriteMigrationData",
      "Effect": "Allow",
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::${var.metrics_bucket_name}/*"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "metrics_calculator_function_execution_policy" {
  role       = aws_iam_role.iam_for_lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "metrics_calculator_function_s3_policy" {
  role       = aws_iam_role.iam_for_lambda.name
  policy_arn = aws_iam_policy.metrics_calculator_function_policy.arn
}