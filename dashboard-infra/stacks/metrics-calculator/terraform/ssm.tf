resource "aws_ssm_parameter" "splunk_api_token" {
  name        = var.splunk_api_token_param_name
  description = "API token to be used for authenticating with Splunk"
  type        = "SecureString"
  value       = "dummy-api-token-value"
  key_id      = aws_kms_key.splunk_api_token_encryption_key.id
}