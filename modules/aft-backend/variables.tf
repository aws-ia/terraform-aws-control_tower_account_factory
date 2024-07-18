# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
variable "primary_region" {
  type = string
}

variable "secondary_region" {
  type = string
}

variable "aft_management_account_id" {
  type = string
}

variable "aft_backend_bucket_access_logs_object_expiration_days" {
  type = number
}
