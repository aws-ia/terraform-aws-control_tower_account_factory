# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
variable "account_factory_product_name" {
  type = string
}

variable "account_vending_method" {
  description = "Method AFT uses to vend accounts (service_catalog or organizations). Service Catalog resources are only created for service_catalog."
  type        = string
  default     = "service_catalog"
}

variable "cloudwatch_log_group_retention" {
  type = string
}

variable "cloudwatch_log_group_enable_cmk_encryption" {
  type = bool
}

variable "aft_organizations_account_provisioning_sfn_name" {
  description = "Name of the Step Function that creates and updates accounts for the Organizations vending method."
  type        = string
}

variable "aft_organizations_provisioning_timeout_seconds" {
  description = "TimeoutSeconds of the organizations account-provisioning Step Function; the baseline poll ends its control wait before it."
  type        = number
  default     = 7200
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

variable "backup_schedule" {
  type = string
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
