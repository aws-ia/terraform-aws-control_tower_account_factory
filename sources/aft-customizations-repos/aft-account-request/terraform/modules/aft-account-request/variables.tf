# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
variable "account-request-table" {
  type        = string
  description = "name of account-request-table"
  default     = "aft-request"
}

variable "account-request-table-hash" {
  type        = string
  description = "name of account-request-table hash key"
  default     = "id"
}

variable "control_tower_parameters" {
  type = object({
    AccountEmail              = string
    AccountName               = string
    ManagedOrganizationalUnit = string
    SSOUserEmail              = string
    SSOUserFirstName          = string
    SSOUserLastName           = string
  })
}

variable "change_management_parameters" {
  type = object({
    change_requested_by = string
    change_reason       = string
  })
}

variable "account_tags" {
  type        = map(any)
  description = "map of account-level tags"
  default     = {}
}

variable "custom_fields" {
  type        = map(any)
  description = "map of custom fields defined by the customer"
  default     = {}
}

variable "account_customizations_name" {
  type        = string
  default     = ""
  description = "The name of the account customizations to apply"
}

variable "workflow_type" {
  type        = string
  default     = "apply"
  description = "Type of pipeline workflow, it can be apply, apply-with-approval"
  validation {
    condition     = var.workflow_type == "apply" || var.workflow_type == "apply-with-approval"
    error_message = "The workflow_type must be apply or apply-with-approval."
  }
}
