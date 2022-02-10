# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#
#############################################
# Log Archive
#############################################

resource "aws_s3_bucket" "aft_logging_bucket" {
  provider = aws.log_archive
  bucket   = "${var.log_archive_bucket_name}-${var.log_archive_account_id}-${data.aws_region.current.name}"

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        kms_master_key_id = aws_kms_key.aft_log_key.arn
        sse_algorithm     = "aws:kms"
      }
    }
  }

  versioning {
    enabled = true
  }

  lifecycle_rule {
    enabled = true

    noncurrent_version_expiration {
      days = var.log_archive_bucket_object_expiration_days
    }
  }

  logging {
    target_bucket = aws_s3_bucket.aft_access_logs.id
    target_prefix = "log/"
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


resource "aws_s3_bucket" "aft_access_logs" {
  provider = aws.log_archive
  bucket   = "${var.log_archive_access_logs_bucket_name}-${var.log_archive_account_id}-${data.aws_region.current.name}"
  acl      = "log-delivery-write"

  versioning {
    enabled = true
  }

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }

  lifecycle_rule {
    enabled = true
    prefix  = true

    noncurrent_version_expiration {
      days = var.log_archive_bucket_object_expiration_days
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
