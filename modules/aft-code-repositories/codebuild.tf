# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

data "local_file" "account_request_buildspec" {
  filename = "${path.module}/buildspecs/ct-aft-account-request.yml"
}
data "local_file" "account_provisioning_customizations_buildspec" {
  filename = "${path.module}/buildspecs/ct-aft-account-provisioning-customizations.yml"
}

resource "aws_codebuild_project" "account_request" {
  depends_on     = [aws_cloudwatch_log_group.account_request]
  name           = "ct-aft-account-request"
  description    = "Job to apply Terraform for Account Requests"
  build_timeout  = tostring(var.global_codebuild_timeout)
  service_role   = aws_iam_role.account_request_codebuild_role.arn
  encryption_key = var.aft_key_arn

  artifacts {
    type = "CODEPIPELINE"
  }

  environment {
    compute_type                = "BUILD_GENERAL1_MEDIUM"
    image                       = "aws/codebuild/amazonlinux2-x86_64-standard:3.0"
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
      group_name = aws_cloudwatch_log_group.account_request.name
    }

    s3_logs {
      status   = "ENABLED"
      location = "${var.codepipeline_s3_bucket_name}/ct-aft-account-request-logs"
    }
  }

  source {
    type      = "CODEPIPELINE"
    buildspec = data.local_file.account_request_buildspec.content
  }

  dynamic "vpc_config" {
    for_each = var.aft_feature_disable_private_networking ? {} : { k = "v" }
    content {
      vpc_id = var.vpc_id
      subnets            = var.subnet_ids
      security_group_ids = var.security_group_ids
    }
  }

  lifecycle {
    ignore_changes = [project_visibility]
  }

}

resource "aws_codebuild_project" "account_provisioning_customizations_pipeline" {
  depends_on     = [aws_cloudwatch_log_group.account_request]
  name           = "ct-aft-account-provisioning-customizations"
  description    = "Deploys the Account Provisioning Customizations terraform project"
  build_timeout  = tostring(var.global_codebuild_timeout)
  service_role   = aws_iam_role.account_provisioning_customizations_codebuild_role.arn
  encryption_key = var.aft_key_arn

  artifacts {
    type = "CODEPIPELINE"
  }

  environment {
    compute_type                = "BUILD_GENERAL1_MEDIUM"
    image                       = "aws/codebuild/amazonlinux2-x86_64-standard:3.0"
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
    for_each = var.aft_feature_disable_private_networking ? {} : { k = "v" }
    content {
      vpc_id = var.vpc_id
      subnets            = var.subnet_ids
      security_group_ids = var.security_group_ids
    }
  }

  lifecycle {
    ignore_changes = [project_visibility]
  }

}

#tfsec:ignore:aws-cloudwatch-log-group-customer-key
resource "aws_cloudwatch_log_group" "account_request" {
  name              = "/aws/codebuild/ct-aft-account-request"
  retention_in_days = var.log_group_retention
}

#tfsec:ignore:aws-cloudwatch-log-group-customer-key
resource "aws_cloudwatch_log_group" "account_provisioning_customizations" {
  name              = "/aws/codebuild/ct-aft-account-provisioning-customizations"
  retention_in_days = var.log_group_retention
}
