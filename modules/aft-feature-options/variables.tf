# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#
variable "aft_vpc_private_subnets" {
  type = list(string)
}

variable "aft_vpc_default_sg" {
  type = list(string)
}

variable "aft_common_layer_arn" {
  type = string
}

variable "cloudwatch_log_group_retention" {
  type = string
}

variable "aft_kms_key_arn" {
  type = string
}

variable "aft_sns_topic_arn" {
  type = string
}

variable "aft_failure_sns_topic_arn" {
  type = string
}

variable "log_archive_bucket_name" {
  type = string
}

variable "log_archive_access_logs_bucket_name" {
  type = string
}

variable "log_archive_bucket_object_expiration_days" {
  type = string
}

variable "log_archive_account_id" {
  type = string
}

variable "aft_features_sfn_name" {
  type = string
}
variable "feature_options_archive_path" {
  type = string
}

variable "feature_options_archive_hash" {
  type = string
}
