# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
variable "aft_account_provisioning_framework_sfn_name" {
  type = string
}

variable "aft_sns_topic_arn" {
  type = string
}

variable "aft_failure_sns_topic_arn" {
  type = string
}

variable "aft_common_layer_arn" {
  type = string
}

variable "aft_kms_key_arn" {
  type = string
}

variable "cloudwatch_log_group_retention" {
  type = string
}

variable "aft_account_provisioning_customizations_sfn_name" {
  type = string
}

variable "trigger_customizations_sfn_name" {
  type = string
}

variable "aft_features_sfn_name" {
  type = string
}

variable "aft_vpc_private_subnets" {
  type    = list(string)
  default = null
}

variable "aft_vpc_default_sg" {
  type    = list(string)
  default = null
}

variable "provisioning_framework_archive_path" {
  type = string
}

variable "provisioning_framework_archive_hash" {
  type = string
}

variable "create_role_lambda_function_name" {
  type = string
}

variable "tag_account_lambda_function_name" {
  type = string
}

variable "persist_metadata_lambda_function_name" {
  type = string
}

variable "account_metadata_ssm_lambda_function_name" {
  type = string
}

variable "delete_default_vpc_lambda_function_name" {
  type = string
}

variable "enroll_support_lambda_function_name" {
  type = string
}

variable "enable_cloudtrail_lambda_function_name" {
  type = string
}

variable "lambda_runtime_python_version" {
  type = string
}

variable "aft_enable_vpc" {
  type = bool
}
