# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 4.27.0, < 5.0.0"
    }
  }
}
variable "trusted_entity_type" {
  default = "AWS"
}

variable "role_name" {
  default = "AWSAFTService"
}

variable "trusted_entity" {

}
variable "aft_admin_session_arn" {

}

resource "aws_iam_role" "role" {
  name = var.role_name

  assume_role_policy = templatefile("${path.module}/trust_policy.tpl",
    {
      trusted_entity_type        = var.trusted_entity_type
      trusted_entity             = var.trusted_entity
      aft_admin_assumed_role_arn = var.aft_admin_session_arn

    }
  )
}

resource "aws_iam_role_policy_attachment" "administrator-access-attachment" {
  role       = aws_iam_role.role.name
  policy_arn = "arn:${data.aws_partition.current.partition}:iam::aws:policy/AdministratorAccess"
}

output "arn" {
  value = aws_iam_role.role.arn
}
