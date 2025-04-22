# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
locals {
  vcs = {
    is_codecommit = lower(data.aws_ssm_parameter.vcs_provider.value) == "codecommit" ? true : false
  }
}
variable "account_id" {
  type        = string
  description = "Account ID for which the pipeline is being created"
}

variable "aft_tf_s3_bucket_ssm_path" {
  type        = string
  description = "SSM Parameter path for the AFT Terraform S3 Bucket"
  default     = "/aft/config/oss-backend/bucket-id"
}

variable "aft_tf_backend_region_ssm_path" {
  type        = string
  description = "SSM Parameter path for the AFT Terraform Backend Region"
  default     = "/aft/config/oss-backend/primary-region"
}

variable "aft_tf_kms_key_id_ssm_path" {
  type        = string
  description = "SSM Parameter path for the AFT KMS Key ID"
  default     = "/aft/config/oss-backend/kms-key-id"
}

variable "aft_tf_ddb_table_ssm_path" {
  type        = string
  description = "SSM Parameter path for the DynamoDB table"
  default     = "/aft/config/oss-backend/table-id"
}

variable "aft_tf_version_ssm_path" {
  type        = string
  description = "SSM Parameter path for the Terraform version"
  default     = "/aft/config/terraform/version"
}

variable "aft_tf_aws_customizations_module_url_ssm_path" {
  type        = string
  description = "SSM Parameter path for the Public AWS Customizations module"
  default     = "/aft/config/aft-pipeline-code-source/repo-url"
}

variable "aft_tf_aws_customizations_module_git_ref_ssm_path" {
  type        = string
  description = "SSM Parameter path for the Public AWS Customizations module"
  default     = "/aft/config/aft-pipeline-code-source/repo-git-ref"
}

variable "aft_tf_sns_codepipeline_notifications_topic_arn_ssm_path" {
  type        = string
  description = "CodePipeline Notifications SNS Topic ARN"
  default     = "/aft/account/aft-management/sns/codepipeline-topic-arn"
}

variable "aft_account_customizations_api_helpers_codebuild_name" {
  type        = string
  description = "CodeBuild Project Name"
  default     = "aft-account-customizations-api-helpers"
}

variable "aft_account_customizations_terraform_codebuild_name" {
  type        = string
  description = "CodeBuild Project Name"
  default     = "aft-account-customizations-terraform"
}

variable "aft_aws_customizations_api_helpers_codebuild_name" {
  type        = string
  description = "CodeBuild Project Name"
  default     = "aft-aws-customizations-api-helpers"
}

variable "aft_aws_customizations_terraform_codebuild_name" {
  type        = string
  description = "CodeBuild Project Name"
  default     = "aft-aws-customizations-terraform"
}

variable "aft_global_customizations_api_helpers_codebuild_name" {
  type        = string
  description = "CodeBuild Project Name"
  default     = "aft-global-customizations-api-helpers"
}

variable "aft_global_customizations_terraform_codebuild_name" {
  type        = string
  description = "CodeBuild Project Name"
  default     = "aft-global-customizations-terraform"
}
