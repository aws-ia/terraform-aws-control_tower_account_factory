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
    bucket_key_enabled = true
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

# Random suffix so the plan-output bucket name is not guessable from the account
# id alone (mitigates bucket-sniping / pre-registration). Matches the existing
# random_string pattern used elsewhere in the repo (e.g. aft-lambda-layer).
resource "random_string" "aft_plan_output_suffix" {
  length  = 8
  lower   = true
  upper   = false
  special = false
}

#tfsec:ignore:aws-s3-enable-bucket-logging
resource "aws_s3_bucket" "aft_plan_output" {
  bucket = "aft-plan-output-${data.aws_caller_identity.current.account_id}-${random_string.aft_plan_output_suffix.result}"
}

resource "aws_s3_bucket_policy" "aft_plan_output_bucket_policy" {
  bucket = aws_s3_bucket.aft_plan_output.id
  policy = templatefile("${path.module}/s3/bucket-policies/aft_plan_output_bucket.tpl", {
    aft_plan_output_bucket_arn = aws_s3_bucket.aft_plan_output.arn
    # Only the AFT customizations CodeBuild role should write plan output (the sole
    # writer in both the OSS `aws s3 cp` and HCP `boto3` paths). Matched on the IAM
    # role ARN because aws:PrincipalArn resolves to the role ARN
    # (arn:<partition>:iam::<account>:role/<name>), NOT the STS assumed-role session
    # ARN -- so an assumed-role wildcard never matches and the deny fires against the
    # role it is meant to exempt. Reads are intentionally left unrestricted since
    # customers may consume the plan output in ways AFT does not control.
    aft_codebuild_customizations_role_arn = aws_iam_role.aft_codebuild_customizations_role.arn
  })
}

resource "aws_s3_bucket_public_access_block" "aft-plan-output-block-public-access" {
  bucket = aws_s3_bucket.aft_plan_output.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "aft-plan-output-bucket-versioning" {
  bucket = aws_s3_bucket.aft_plan_output.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "aft-plan-output-bucket-encryption" {
  bucket = aws_s3_bucket.aft_plan_output.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = var.aft_kms_key_id
      sse_algorithm     = "aws:kms"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "aft_plan_output_lifecycle_configuration" {
  bucket = aws_s3_bucket.aft_plan_output.id
  rule {
    id = "plan-output-expiration"
    filter {
      prefix = ""
    }
    expiration {
      days = var.aft_plan_output_retention_days
    }
    status = "Enabled"
  }
}
