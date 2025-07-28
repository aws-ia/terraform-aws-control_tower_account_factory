# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
variable "lambda_layer_name" {
  type = string
  validation {
    condition     = can(regex("^[a-zA-Z0-9\\-]+$", var.lambda_layer_name))
    error_message = "Layer name must contain only alphanumeric characters and hyphens."
  }
}

variable "aft_tf_aws_customizations_module_url_ssm_path" {
  type = string
}

variable "aft_tf_aws_customizations_module_git_ref_ssm_path" {
  type = string
}

variable "aws_region" {
  type = string
}

variable "lambda_layer_codebuild_delay" {
  type = string
}

variable "lambda_layer_python_version" {
  type = string
}

variable "lambda_runtime_python_version" {
  type = string
}

variable "s3_bucket_name" {
  type = string
}

variable "aft_kms_key_arn" {
  type = string
}

variable "aft_vpc_id" {
  type    = string
  default = null
}

variable "aft_vpc_private_subnets" {
  type    = list(string)
  default = null
}

variable "aft_vpc_default_sg" {
  type    = list(string)
  default = null
}
variable "aft_version" {
  type = string
}

variable "builder_archive_path" {
  type = string
}

variable "builder_archive_hash" {
  type = string
}

variable "cloudwatch_log_group_retention" {
  type = string
}

variable "cloudwatch_log_group_enable_cmk_encryption" {
  type = bool
}

variable "aft_enable_vpc" {
  type = bool
}

variable "codebuild_compute_type" {
  type = string
}
