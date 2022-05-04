data "aws_caller_identity" "current" {}

data "aws_iam_role" "nhsd_admin_role" {
  name = "NHSDAdminRole"
}