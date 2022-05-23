# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
variable "trusted_entity_type" {
  default = "AWS"
}

variable "role_name" {
  default = "AWSAFTService"
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
}

resource "aws_iam_role_policy_attachment" "administrator-access-attachment" {
  role       = aws_iam_role.role.name
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
}

output "arn" {
  value = aws_iam_role.role.arn
}
