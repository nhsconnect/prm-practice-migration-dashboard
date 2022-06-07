resource "aws_lambda_function" "metrics_calculator_function" {
  function_name = var.metrics_calculator_function_name
  role          = aws_iam_role.metrics_calculator_function_role.arn
  handler       = var.metrics_calculator_handler_name
  timeout       = 900
  runtime       = "python3.9"
  reserved_concurrent_executions = 1

  vpc_config {
    security_group_ids = [aws_security_group.lambda_sg.id]
    subnet_ids         = [aws_subnet.private_subnet.id]
  }

  s3_bucket = var.metrics_calculator_deployment_bucket_name
  s3_key    = var.metrics_calculator_code_key

  environment {
    variables = {
      ASID_LOOKUP_BUCKET_NAME = var.asid_lookup_bucket_name
      METRICS_BUCKET_NAME     = var.metrics_bucket_name
      OCCURRENCES_BUCKET_NAME = var.migration_occurrences_bucket_name
      TELEMETRY_BUCKET_NAME   = var.telemetry_bucket_name
      PATIENT_REGISTRATIONS_BUCKET_NAME   = var.patient_registrations_bucket_name
    }
  }
}

resource "aws_lambda_function" "splunk_data_exporter_function" {
  function_name = var.splunk_data_exporter_function_name
  role          = aws_iam_role.splunk_data_exporter_function_role.arn
  handler       = var.splunk_data_exporter_handler_name
  timeout       = 900
  runtime       = "python3.9"
  reserved_concurrent_executions = 1

  vpc_config {
    security_group_ids = [aws_security_group.lambda_sg.id]
    subnet_ids         = [aws_subnet.private_subnet.id]
  }

  s3_bucket = var.metrics_calculator_deployment_bucket_name
  s3_key    = var.metrics_calculator_code_key

  environment {
    variables = {
      ASID_LOOKUP_BUCKET_NAME = var.asid_lookup_bucket_name
      OCCURRENCES_BUCKET_NAME = var.migration_occurrences_bucket_name
      TELEMETRY_BUCKET_NAME   = var.telemetry_bucket_name
      SPLUNK_HOST             = var.splunk_api_host
    }
  }
}

resource "aws_security_group" "lambda_sg" {
  vpc_id = aws_vpc.metrics_calculator_vpc.id

  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }
}

resource "aws_iam_role" "metrics_calculator_function_role" {
  name = "metrics_calculator_function_role"

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

resource "aws_iam_role" "splunk_data_exporter_function_role" {
  name = "splunk_data_exporter_function_role"

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
    },
    {
      "Sid": "AllowReadPatientRegistrationsBucket",
      "Effect": "Allow",
      "Action": "s3:ListBucket",
      "Resource": "arn:aws:s3:::${var.patient_registrations_bucket_name}"
    },
    {
      "Sid": "AllowReadPatientRegistrationsObjects",
      "Effect": "Allow",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::${var.patient_registrations_bucket_name}/*"
    }
  ]
}
EOF
}

resource "aws_iam_policy" "splunk_data_exporter_function_policy" {
  name        = "AllowSplunkDataExporterS3Access"
  description = "Grant the splunk data exporter function the required S3 permissions"

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
      "Sid": "AllowWriteTelemetryData",
      "Effect": "Allow",
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::${var.telemetry_bucket_name}/*"
    },
    {
      "Sid": "AllowReadTelemetryBucket",
      "Effect": "Allow",
      "Action": "s3:ListBucket",
      "Resource": "arn:aws:s3:::${var.telemetry_bucket_name}"
    }
  ]
}
EOF
}

resource "aws_iam_policy" "splunk_api_token_access_policy" {
  name        = "AllowAccessToSplunkApiToken"
  description = "Grant read access to the API token used to authenticate with Splunk"
  policy      = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
          "ssm:GetParameter*"
      ],
      "Resource": "arn:aws:ssm:${var.region}:${data.aws_caller_identity.current.account_id}:parameter${var.splunk_api_token_param_name}"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "metrics_calculator_function_execution_policy" {
  role       = aws_iam_role.metrics_calculator_function_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

resource "aws_iam_role_policy_attachment" "splunk_data_exporter_function_execution_policy" {
  role       = aws_iam_role.splunk_data_exporter_function_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

resource "aws_iam_role_policy_attachment" "metrics_calculator_function_s3_policy" {
  role       = aws_iam_role.metrics_calculator_function_role.name
  policy_arn = aws_iam_policy.metrics_calculator_function_policy.arn
}

resource "aws_iam_role_policy_attachment" "splunk_data_exporter_function_s3_policy" {
  role       = aws_iam_role.splunk_data_exporter_function_role.name
  policy_arn = aws_iam_policy.splunk_data_exporter_function_policy.arn
}

resource "aws_iam_role_policy_attachment" "splunk_data_exporter_splunk_api_token_policy" {
  role       = aws_iam_role.splunk_data_exporter_function_role.name
  policy_arn = aws_iam_policy.splunk_api_token_access_policy.arn
}