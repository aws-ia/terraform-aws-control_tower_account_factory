# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
variable "vpc_id" {
  type = string
}

variable "subnet_ids" {
  type    = list(string)
  default = null
}

variable "security_group_ids" {
  type = list(string)
}

variable "log_group_retention" {
  type = string
}

variable "vcs_provider" {
  type = string
}

variable "github_enterprise_url" {
  type = string
}

variable "gitlab_selfmanaged_url" {
  type = string
}

variable "account_request_table_name" {
  type = string
}

variable "aft_config_backend_table_id" {
  type = string
}

variable "aft_config_backend_bucket_id" {
  type = string
}

variable "aft_config_backend_kms_key_id" {
  type = string
}

variable "codepipeline_s3_bucket_name" {
  type = string
}

variable "codepipeline_s3_bucket_arn" {
  type = string
}

variable "aft_key_arn" {
  type = string
}

variable "account_request_repo_name" {
  type = string
}

variable "account_request_repo_branch" {
  type = string
}

variable "global_customizations_repo_name" {
  type = string
}

variable "global_customizations_repo_branch" {
  type = string
}

variable "account_customizations_repo_name" {
  type = string
}

variable "account_customizations_repo_branch" {
  type = string
}

variable "account_provisioning_customizations_repo_name" {
  type = string
}

variable "account_provisioning_customizations_repo_branch" {
  type = string
}

variable "global_codebuild_timeout" {
  type = number
}

variable "aft_enable_vpc" {
  type = bool
}
