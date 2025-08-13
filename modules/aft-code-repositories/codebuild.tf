# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

data "local_file" "account_request_buildspec" {
  filename = "${path.module}/buildspecs/ct-aft-account-request.yml"
}
data "local_file" "account_provisioning_customizations_buildspec" {
  filename = "${path.module}/buildspecs/ct-aft-account-provisioning-customizations.yml"
}

resource "aws_codebuild_project" "account_provisioning_customizations_pipeline" {
  depends_on     = [aws_cloudwatch_log_group.account_request, time_sleep.iam_eventual_consistency]
  name           = "ct-aft-account-provisioning-customizations"
  description    = "Deploys the Account Provisioning Customizations terraform project"
  build_timeout  = tostring(var.global_codebuild_timeout)
  service_role   = aws_iam_role.account_provisioning_customizations_codebuild_role.arn
  encryption_key = var.aft_kms_key_arn

  artifacts {
    type = "CODEPIPELINE"
  }

  environment {
    compute_type                = var.codebuild_compute_type
    image                       = "aws/codebuild/amazonlinux2-x86_64-standard:5.0"
    type                        = "LINUX_CONTAINER"
    image_pull_credentials_type = "CODEBUILD"

    environment_variable {
      name  = "AWS_PARTITION"
      value = data.aws_partition.current.partition
      type  = "PLAINTEXT"
    }
  }

  logs_config {
    cloudwatch_logs {
      group_name = aws_cloudwatch_log_group.account_provisioning_customizations.name
    }

    s3_logs {
      status   = "ENABLED"
      location = "${var.codepipeline_s3_bucket_name}/ct-aft-account-provisioning-customization-logs"
    }
  }

  source {
    type      = "CODEPIPELINE"
    buildspec = data.local_file.account_provisioning_customizations_buildspec.content
  }

  dynamic "vpc_config" {
    for_each = var.aft_enable_vpc ? [1] : []
    content {
      vpc_id             = var.vpc_id
      subnets            = var.subnet_ids
      security_group_ids = var.security_group_ids
    }
  }

  lifecycle {
    ignore_changes = [project_visibility]
  }

}

resource "aws_cloudwatch_log_group" "account_request" {
  name              = "/aws/codebuild/ct-aft-account-request"
  retention_in_days = var.cloudwatch_log_group_retention
  kms_key_id        = var.cloudwatch_log_group_enable_cmk_encryption ? var.aft_kms_key_arn : null
}

resource "aws_cloudwatch_log_group" "account_provisioning_customizations" {
  name              = "/aws/codebuild/ct-aft-account-provisioning-customizations"
  retention_in_days = var.cloudwatch_log_group_retention
  kms_key_id        = var.cloudwatch_log_group_enable_cmk_encryption ? var.aft_kms_key_arn : null
}
