# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
#############################################
# Log Archive
#############################################

resource "aws_s3_bucket" "aft_logging_bucket" {
  provider = aws.log_archive
  bucket   = "${var.log_archive_bucket_name}-${var.log_archive_account_id}-${data.aws_region.current.name}"
}

resource "aws_s3_bucket_logging" "aft_logging_bucket_logging" {
  provider      = aws.log_archive
  bucket        = aws_s3_bucket.aft_logging_bucket.id
  target_bucket = aws_s3_bucket.aft_access_logs.id
  target_prefix = "log/"
}

resource "aws_s3_bucket_versioning" "aft_logging_bucket_versioning" {
  provider = aws.log_archive
  bucket   = aws_s3_bucket.aft_logging_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "aft_logging_bucket_encryption" {
  provider = aws.log_archive
  bucket   = aws_s3_bucket.aft_logging_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.aft_log_key.arn
      sse_algorithm     = "aws:kms"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "aft_logging_bucket_lifecycle_configuration" {
  provider = aws.log_archive
  bucket   = aws_s3_bucket.aft_logging_bucket.id
  rule {
    status = "Enabled"
    id     = "aft_logging_bucket_lifecycle_configuration_rule"

    noncurrent_version_expiration {
      noncurrent_days = var.log_archive_bucket_object_expiration_days
    }
  }

}

resource "aws_s3_bucket_policy" "aft_logging_bucket" {
  provider = aws.log_archive
  bucket   = aws_s3_bucket.aft_logging_bucket.id
  policy = templatefile("${path.module}/s3/bucket-policies/aft_logging_bucket.tpl", {
    aws_s3_bucket_aft_logging_bucket_arn                    = aws_s3_bucket.aft_logging_bucket.arn
    data_aws_organizations_organization_aft_organization_id = data.aws_organizations_organization.aft_organization.id
  })
}

resource "aws_s3_bucket_public_access_block" "aft_logging_bucket" {
  provider                = aws.log_archive
  bucket                  = aws_s3_bucket.aft_logging_bucket.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

#tfsec:ignore:aws-s3-enable-bucket-logging
resource "aws_s3_bucket" "aft_access_logs" {
  provider = aws.log_archive
  bucket   = "${var.log_archive_access_logs_bucket_name}-${var.log_archive_account_id}-${data.aws_region.current.name}"
}

resource "aws_s3_bucket_policy" "aft_access_logs" {
  provider = aws.log_archive
  bucket   = aws_s3_bucket.aft_access_logs.id
  policy = templatefile("${path.module}/s3/bucket-policies/aft_access_logs.tpl", {
    aws_s3_bucket_aft_access_logs_arn    = aws_s3_bucket.aft_access_logs.arn
    aws_s3_bucket_aft_logging_bucket_arn = aws_s3_bucket.aft_logging_bucket.arn
    log_archive_account_id               = var.log_archive_account_id
  })
}

resource "aws_s3_bucket_versioning" "aft_access_logs_versioning" {
  provider = aws.log_archive
  bucket   = aws_s3_bucket.aft_access_logs.id
  versioning_configuration {
    status = "Enabled"
  }
}

#tfsec:ignore:aws-s3-encryption-customer-key
resource "aws_s3_bucket_server_side_encryption_configuration" "aft_access_logs_encryption" {
  provider = aws.log_archive
  bucket   = aws_s3_bucket.aft_access_logs.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "aft_access_logs_lifecycle_configuration" {
  provider = aws.log_archive
  bucket   = aws_s3_bucket.aft_access_logs.id
  rule {
    status = "Enabled"
    filter {
      prefix = "log/"
    }
    id = "aft_access_logs_lifecycle_configuration_rule"

    noncurrent_version_expiration {
      noncurrent_days = var.log_archive_bucket_object_expiration_days
    }
  }

}

resource "aws_s3_bucket_public_access_block" "aft_access_logs" {
  provider                = aws.log_archive
  bucket                  = aws_s3_bucket.aft_access_logs.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
