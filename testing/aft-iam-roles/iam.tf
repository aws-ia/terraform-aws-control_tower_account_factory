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

data "aws_caller_identity" "current" {}

variable "aft_account_id" {
  description = "AFT Management Account ID"
  type        = string
  default  = "947117813606"
}

## Creation of the NetOps Role ##
resource "aws_iam_role" "netops_role" {
  provider = aws.aft_netops
  name     = "NetOpsAdmin"
  assume_role_policy = templatefile("${path.module}/iam_netops/netops_role_trust_policy.tpl",
    {
      aft_account_id = var.aft_account_id
    }
  )
}

resource "aws_iam_role_policy" "netops_policy" {
  provider = aws.aft_netops
  name     = "NetOps_policy"
  role     = aws_iam_role.netops_role.id

  policy = file("${path.module}/iam_netops/netops_role_policy.tpl")
}
## Creation of the NetOps Role ##

module "netops_exec_role" {
  source = "./netops-role"
  providers = {
    aws = aws.aft_netops
  }
  trusted_entity = aws_iam_role.netops_role.arn
}

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
