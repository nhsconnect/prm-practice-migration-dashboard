resource "aws_kms_key" "splunk_api_token_encryption_key" {
  description = "KMS key to use for encrypting/decrypting the Splunk API token"
  policy      = <<EOF
{
  "Version" : "2012-10-17",
  "Statement" : [
    {
      "Sid": "SplunkApiTokenKmsKeyAdmin",
      "Effect": "Allow",
      "Principal": {"AWS": "${data.aws_iam_role.nhsd_admin_role.arn}"},
      "Action": [
        "kms:Create*",
        "kms:Describe*",
        "kms:Enable*",
        "kms:List*",
        "kms:Put*",
        "kms:Update*",
        "kms:Revoke*",
        "kms:Disable*",
        "kms:Get*",
        "kms:Delete*",
        "kms:TagResource",
        "kms:UntagResource",
        "kms:ScheduleKeyDeletion",
        "kms:CancelKeyDeletion"
      ],
      "Resource": "*"
    },
    {
      "Sid": "SplunkApiTokenKmsKeyAdminUse",
      "Effect": "Allow",
      "Principal": {"AWS": "${data.aws_iam_role.nhsd_admin_role.arn}"},
      "Action": [
        "kms:Decrypt",
        "kms:Encrypt"
      ],
      "Resource": "*"
    },
    {
      "Sid" : "AllowSplunkDataExporterToDecryptUsingSplunkTokenEncryptionKey",
      "Effect" : "Allow",
      "Principal" : {
        "AWS" : "${aws_iam_role.splunk_data_exporter_function_role.arn}"
      },
      "Action" : "kms:Decrypt",
      "Resource" : "*"
    }
  ]
}
EOF
}