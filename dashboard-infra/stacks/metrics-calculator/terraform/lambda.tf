resource "aws_lambda_function" "metrics_calculator_function" {
  function_name = var.metrics_calculator_function_name
  role          = aws_iam_role.iam_for_lambda.arn
  handler       = var.metrics_calculator_handler_name

  runtime       = "python3.9"

  s3_bucket     = var.metrics_calculator_deployment_bucket_name
  s3_key        = var.metrics_calculator_code_key

  environment {
    variables = {
      TELEMETRY_BUCKET_NAME = var.telemetry_bucket_name
      METRICS_BUCKET_NAME   = var.metrics_bucket_name
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