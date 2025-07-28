# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

resource "aws_cloudwatch_log_group" "codebuild_loggroup" {
  name              = "/aws/codebuild/${local.common_name}"
  retention_in_days = var.cloudwatch_log_group_retention
  kms_key_id        = var.cloudwatch_log_group_enable_cmk_encryption ? var.aft_kms_key_arn : null
}

resource "aws_codebuild_project" "codebuild" {
  name           = local.common_name
  description    = "Codebuild project to create lambda layer ${var.lambda_layer_name}"
  build_timeout  = "10"
  service_role   = aws_iam_role.codebuild.arn
  encryption_key = var.aft_kms_key_arn

  artifacts {
    type = "NO_ARTIFACTS"
  }

  environment {
    compute_type                = var.codebuild_compute_type
    image                       = "aws/codebuild/amazonlinux2-x86_64-standard:5.0"
    type                        = "LINUX_CONTAINER"
    image_pull_credentials_type = "CODEBUILD"

    environment_variable {
      name  = "PYTHON_VERSION"
      value = var.lambda_layer_python_version
    }
    environment_variable {
      name  = "BUCKET_NAME"
      value = var.s3_bucket_name
    }
    environment_variable {
      name  = "SSM_AWS_MODULE_SOURCE"
      value = var.aft_tf_aws_customizations_module_url_ssm_path
      type  = "PLAINTEXT"
    }
    environment_variable {
      name  = "SSM_AWS_MODULE_GIT_REF"
      value = var.aft_tf_aws_customizations_module_git_ref_ssm_path
      type  = "PLAINTEXT"
    }

  }

  logs_config {
    cloudwatch_logs {
      group_name  = aws_cloudwatch_log_group.codebuild_loggroup.name
      stream_name = "build-logs"
    }

    s3_logs {
      status   = "ENABLED"
      location = "${var.s3_bucket_name}/aft-lambda-layer-builder-logs"
    }
  }

  source {
    type      = "NO_SOURCE"
    buildspec = data.local_file.aft_lambda_layer.content
  }

  dynamic "vpc_config" {
    for_each = var.aft_enable_vpc ? [1] : []
    content {
      vpc_id             = var.aft_vpc_id
      subnets            = var.aft_vpc_private_subnets
      security_group_ids = var.aft_vpc_default_sg
    }
  }

  lifecycle {
    ignore_changes = [project_visibility]
  }

}
