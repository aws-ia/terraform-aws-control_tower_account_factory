# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
#####################################################
# AFT Global Customizations Terraform
#####################################################

resource "aws_codebuild_project" "aft_global_customizations_terraform" {
  depends_on     = [aws_cloudwatch_log_group.aft_global_customizations_terraform]
  name           = "aft-global-customizations-terraform"
  description    = "Job to apply Terraform provided by the customer global customizations repo"
  build_timeout  = tostring(var.global_codebuild_timeout)
  service_role   = aws_iam_role.aft_codebuild_customizations_role.arn
  encryption_key = var.aft_kms_key_arn

  artifacts {
    type = "CODEPIPELINE"
  }

  environment {
    compute_type                = "BUILD_GENERAL1_MEDIUM"
    image                       = "aws/codebuild/amazonlinux2-x86_64-standard:5.0"
    type                        = "LINUX_CONTAINER"
    image_pull_credentials_type = "CODEBUILD"

    environment_variable {
      name  = "SPACELIFT_API_CREDENTIALS_JSON"
      value = var.spacelift_api_credentials_ssm_path
      type  = "PARAMETER_STORE"
    }
    
    environment_variable {
      name  = "AWS_PARTITION"
      value = data.aws_partition.current.partition
      type  = "PLAINTEXT"
    }
  }

  logs_config {
    cloudwatch_logs {
      group_name = aws_cloudwatch_log_group.aft_global_customizations_terraform.name
    }

    s3_logs {
      status   = "ENABLED"
      location = "${aws_s3_bucket.aft_codepipeline_customizations_bucket.id}/aft-global-customizations-terraform-logs"
    }
  }

  source {
    type      = "CODEPIPELINE"
    buildspec = data.local_file.aft_global_customizations_terraform.content
  }

  vpc_config {
    vpc_id             = var.aft_vpc_id
    subnets            = var.aft_vpc_private_subnets
    security_group_ids = var.aft_vpc_default_sg
  }

  lifecycle {
    ignore_changes = [project_visibility]
  }

}

# Maintain this log group for log retention reasons. This is no longer used by AFT
#tfsec:ignore:aws-cloudwatch-log-group-customer-key
resource "aws_cloudwatch_log_group" "aft_global_customizations_api_helpers" {
  name              = "/aws/codebuild/aft-global-customizations-api-helpers"
  retention_in_days = var.cloudwatch_log_group_retention
}

#tfsec:ignore:aws-cloudwatch-log-group-customer-key
resource "aws_cloudwatch_log_group" "aft_global_customizations_terraform" {
  name              = "/aws/codebuild/aft-global-customizations-terraform"
  retention_in_days = var.cloudwatch_log_group_retention
}

#####################################################
# AFT Account Customizations Terraform
#####################################################

resource "aws_codebuild_project" "aft_account_customizations_terraform" {
  depends_on     = [aws_cloudwatch_log_group.aft_account_customizations_terraform]
  name           = "aft-account-customizations-terraform"
  description    = "Job to apply Terraform provided by the customer account customizations repo"
  build_timeout  = tostring(var.global_codebuild_timeout)
  service_role   = aws_iam_role.aft_codebuild_customizations_role.arn
  encryption_key = var.aft_kms_key_arn

  artifacts {
    type = "CODEPIPELINE"
  }

  environment {
    compute_type                = "BUILD_GENERAL1_MEDIUM"
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
      group_name = aws_cloudwatch_log_group.aft_account_customizations_terraform.name
    }

    s3_logs {
      status   = "ENABLED"
      location = "${aws_s3_bucket.aft_codepipeline_customizations_bucket.id}/aft-account-customizations-terraform-logs"
    }
  }

  source {
    type      = "CODEPIPELINE"
    buildspec = data.local_file.aft_account_customizations_terraform.content
  }

  vpc_config {
    vpc_id             = var.aft_vpc_id
    subnets            = var.aft_vpc_private_subnets
    security_group_ids = var.aft_vpc_default_sg
  }

  lifecycle {
    ignore_changes = [project_visibility]
  }

}

# Maintain this log group for log retention reasons. This is no longer used by AFT
#tfsec:ignore:aws-cloudwatch-log-group-customer-key
resource "aws_cloudwatch_log_group" "aft_account_customizations_api_helpers" {
  name              = "/aws/codebuild/aft-account-customizations-api-helpers"
  retention_in_days = var.cloudwatch_log_group_retention
}

#tfsec:ignore:aws-cloudwatch-log-group-customer-key
resource "aws_cloudwatch_log_group" "aft_account_customizations_terraform" {
  name              = "/aws/codebuild/aft-account-customizations-terraform"
  retention_in_days = var.cloudwatch_log_group_retention
}

#####################################################
# AFT Account Provisioning Framework SFN - aft-create-pipeline
#####################################################

resource "aws_codebuild_project" "aft_create_pipeline" {
  depends_on     = [aws_cloudwatch_log_group.aft_create_pipeline]
  name           = "aft-create-pipeline"
  description    = "Job to run Terraform required to create account specific customizations pipeline"
  build_timeout  = tostring(var.global_codebuild_timeout)
  service_role   = aws_iam_role.aft_codebuild_customizations_role.arn
  encryption_key = var.aft_kms_key_arn

  artifacts {
    type = "NO_ARTIFACTS"
  }

  environment {
    compute_type                = "BUILD_GENERAL1_MEDIUM"
    image                       = "aws/codebuild/amazonlinux2-x86_64-standard:5.0"
    type                        = "LINUX_CONTAINER"
    image_pull_credentials_type = "CODEBUILD"

    environment_variable {
      name  = "ACCOUNT_ID"
      value = "TBD"
      type  = "PLAINTEXT"
    }

    environment_variable {
      name  = "SSM_TF_S3_BUCKET"
      value = var.aft_tf_s3_bucket_ssm_path
      type  = "PLAINTEXT"
    }

    environment_variable {
      name  = "SSM_TF_BACKEND_REGION"
      value = var.aft_tf_backend_region_ssm_path
      type  = "PLAINTEXT"
    }

    environment_variable {
      name  = "SSM_TF_KMS_KEY_ID"
      value = var.aft_tf_kms_key_id_ssm_path
      type  = "PLAINTEXT"
    }

    environment_variable {
      name  = "SSM_TF_DDB_TABLE"
      value = var.aft_tf_ddb_table_ssm_path
      type  = "PLAINTEXT"
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

    environment_variable {
      name  = "SSM_TF_VERSION"
      value = var.aft_tf_version_ssm_path
      type  = "PLAINTEXT"
    }

    environment_variable {
      name  = "AWS_PARTITION"
      value = data.aws_partition.current.partition
      type  = "PLAINTEXT"
    }
  }

  logs_config {
    cloudwatch_logs {
      group_name = aws_cloudwatch_log_group.aft_create_pipeline.name
    }

    s3_logs {
      status   = "ENABLED"
      location = "${aws_s3_bucket.aft_codepipeline_customizations_bucket.id}/aft-create-pipeline-logs"
    }
  }

  source {
    type      = "NO_SOURCE"
    buildspec = data.local_file.aft_create_pipeline.content
  }

  vpc_config {
    vpc_id             = var.aft_vpc_id
    subnets            = var.aft_vpc_private_subnets
    security_group_ids = var.aft_vpc_default_sg
  }

  lifecycle {
    ignore_changes = [project_visibility]
  }

}

#tfsec:ignore:aws-cloudwatch-log-group-customer-key
resource "aws_cloudwatch_log_group" "aft_create_pipeline" {
  name              = "/aws/codebuild/aft-create-pipeline"
  retention_in_days = var.cloudwatch_log_group_retention
}
