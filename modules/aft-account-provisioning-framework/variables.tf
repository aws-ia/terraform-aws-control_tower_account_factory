# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
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
  type = list(string)
}

variable "aft_vpc_default_sg" {
  type = list(string)
}

variable "provisioning_framework_archive_path" {
  type = string
}

variable "provisioning_framework_archive_hash" {
  type = string
}
