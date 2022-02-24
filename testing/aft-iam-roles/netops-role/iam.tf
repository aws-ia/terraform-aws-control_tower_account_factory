# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#
variable "trusted_entity_type" {
  default = "AWS"
}

variable "role_name" {
  default = "NetOpsExecution"
}

variable "trusted_entity" {
  
}

resource "aws_iam_role" "role" {
  name = var.role_name

  # Terraform's "jsonencode" function converts a
  # Terraform expression result to valid JSON syntax.
  assume_role_policy = templatefile("${path.module}/trust_policy.tpl",
    {
      trusted_entity_type = var.trusted_entity_type
      trusted_entity      = var.trusted_entity
    }
  )

  managed_policy_arns = ["arn:aws:iam::aws:policy/job-function/NetworkAdministrator"]
}

output "arn" {
  value = aws_iam_role.role.arn
}
