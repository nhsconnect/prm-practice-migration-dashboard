resource "aws_s3_bucket" "dashboard_data" {
  bucket = var.telemetry_bucket_name
}

resource "aws_s3_bucket_public_access_block" "dashboard_data" {
  bucket = aws_s3_bucket.dashboard_data.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket" "asid_lookup_bucket" {
  bucket = var.asid_lookup_bucket_name
}

resource "aws_s3_bucket_public_access_block" "asid_lookup_bucket" {
  bucket = aws_s3_bucket.asid_lookup_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}