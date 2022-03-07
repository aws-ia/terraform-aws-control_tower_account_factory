# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#
provider "aws" {
  alias  = "aft_netops"
  region = "us-east-1"
  # assume_role {
  #   role_arn     = "arn:aws:iam::${var.aft_account_id}:role/AWSControlTowerExecution"
  #   session_name = "NetOps-Session"
  # }
  default_tags {
    tags = {
      managed_by = "AFT"
    }
  }
}


data "aws_organizations_organization" "example" {}

# data "aws_caller_identity" "current" {}

# variable "aft_account_id" {
#   description = "AFT Management Account ID"
#   type        = string
#   default     = "947117813606"
# }

## Creation of the NetOps Role ##

resource "aws_iam_role" "netops_role" {
  depends_on = [data.aws_organizations_organization.example]
  for_each = toset(data.aws_organizations_organization.example.non_master_accounts[*].id)
  provider = aws.aft_netops
  name     = "NetOpsAdmin"
  assume_role_policy = templatefile("${path.module}/iam_netops/netops_role_trust_policy.tpl",
    {
      aft_account_id = each.value
    }
  )
}

resource "aws_iam_role_policy" "netops_policy" {
  depends_on = [aws_iam_role.netops_role]
  for_each = aws_iam_role.netops_role
  provider = aws.aft_netops
  name     = "NetOpsAdmin_policy"
  role     = each.value.id

  policy = file("${path.module}/iam_netops/netops_role_policy.tpl")
}

module "netops_exec_role" {
  depends_on = [aws_iam_role.netops_role]
  for_each = aws_iam_role.netops_role
  source = "./netops-role"
  providers = {
    aws = aws.aft_netops
  }
  trusted_entity = each.value.arn
}

## Creation of the NetOps Role ##


# module "log_archive_exec_role" {
#   source = "./admin-role"
#   providers = {
#     aws = aws.log_archive
#   }
#   trusted_entity = aws_iam_role.aft_admin_role.arn
# }

# module "audit_exec_role" {
#   source = "./admin-role"
#   providers = {
#     aws = aws.audit
#   }
#   trusted_entity = aws_iam_role.aft_admin_role.arn
# }

# module "aft_exec_role" {
#   source = "./admin-role"
#   providers = {
#     aws = aws.aft_management
#   }
#   trusted_entity = aws_iam_role.aft_admin_role.arn
# }
