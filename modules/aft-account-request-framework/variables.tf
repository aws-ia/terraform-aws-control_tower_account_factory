# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
variable "account_factory_product_name" {
  type = string
}

variable "cloudwatch_log_group_retention" {
  type = string
}

variable "cloudwatch_log_group_enable_cmk_encryption" {
  type = bool
}

variable "aft_account_provisioning_framework_sfn_name" {
  type = string
}

variable "aft_common_layer_arn" {
  type = string
}

variable "aft_vpc_cidr" {
  type    = string
  default = null
}

variable "aft_vpc_private_subnet_01_cidr" {
  type    = string
  default = null
}

variable "aft_vpc_private_subnet_02_cidr" {
  type    = string
  default = null
}

variable "aft_vpc_public_subnet_01_cidr" {
  type    = string
  default = null
}

variable "aft_vpc_public_subnet_02_cidr" {
  type    = string
  default = null
}

variable "aft_vpc_endpoints" {
  type    = bool
  default = null
}

variable "request_framework_archive_path" {
  type = string
}

variable "request_framework_archive_hash" {
  type = string
}
variable "concurrent_account_factory_actions" {
  type = number
}

variable "lambda_runtime_python_version" {
  type = string
}

variable "backup_recovery_point_retention" {
  type = number
}

variable "aft_enable_vpc" {
  type = bool
}

variable "aft_customer_vpc_id" {
  type = string
}

variable "aft_customer_private_subnets" {
  type = list(string)
}

variable "sns_topic_enable_cmk_encryption" {
  type = bool
}
