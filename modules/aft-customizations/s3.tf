# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

#tfsec:ignore:aws-s3-enable-bucket-logging
resource "aws_s3_bucket" "aft_codepipeline_customizations_bucket" {
  bucket = "aft-customizations-pipeline-${data.aws_caller_identity.current.account_id}"
}

resource "aws_s3_bucket_policy" "aft_codepipeline_customizations_bucket" {
  bucket = aws_s3_bucket.aft_codepipeline_customizations_bucket.id
  policy = templatefile("${path.module}/s3/bucket-policies/aft_codepipeline_customizations_bucket.tpl", {
    aft_codepipeline_customizations_bucket_arn = aws_s3_bucket.aft_codepipeline_customizations_bucket.arn
  })
}

resource "aws_s3_bucket_public_access_block" "aft-codepipeline-customizations-block-public-access" {
  bucket = aws_s3_bucket.aft_codepipeline_customizations_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "aft-codepipeline-customizations-bucket-versioning" {
  bucket = aws_s3_bucket.aft_codepipeline_customizations_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "aft-codepipeline-customizations-bucket-encryption" {
  bucket = aws_s3_bucket.aft_codepipeline_customizations_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = var.aft_kms_key_id
      sse_algorithm     = "aws:kms"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "aft_codepipeline_customizations_bucket" {
  bucket = aws_s3_bucket.aft_codepipeline_customizations_bucket.id
  rule {
    id = "sfn-data"
    filter {
      prefix = "sfn/"
    }
    expiration {
      days = var.sfn_s3_bucket_object_expiration_days
    }
    status = "Enabled"
  }
}
