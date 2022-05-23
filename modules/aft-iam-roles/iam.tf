# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
data "aws_caller_identity" "aft_management" {
  provider = aws.aft_management
}

resource "aws_iam_role" "aft_admin_role" {
  provider = aws.aft_management
  name     = "AWSAFTAdmin"
  assume_role_policy = templatefile("${path.module}/iam/aft_admin_role_trust_policy.tpl",
    {
      aft_account_id = data.aws_caller_identity.aft_management.account_id
    }
  )
}

resource "aws_iam_role_policy" "aft_admin_role" {
  provider = aws.aft_management
  name     = "aft_admin_role_policy"
  role     = aws_iam_role.aft_admin_role.id

  policy = file("${path.module}/iam/aft_admin_role_policy.tpl")
}

module "ct_management_exec_role" {
  source = "./admin-role"
  providers = {
    aws = aws.ct_management
  }
  trusted_entity = aws_iam_role.aft_admin_role.arn
}

module "log_archive_exec_role" {
  source = "./admin-role"
  providers = {
    aws = aws.log_archive
  }
  trusted_entity = aws_iam_role.aft_admin_role.arn
}

module "audit_exec_role" {
  source = "./admin-role"
  providers = {
    aws = aws.audit
  }
  trusted_entity = aws_iam_role.aft_admin_role.arn
}

module "aft_exec_role" {
  source = "./admin-role"
  providers = {
    aws = aws.aft_management
  }
  trusted_entity = aws_iam_role.aft_admin_role.arn
}


module "ct_management_service_role" {
  source = "./service-role"
  providers = {
    aws = aws.ct_management
  }
  trusted_entity = aws_iam_role.aft_admin_role.arn
}

module "log_archive_service_role" {
  source = "./service-role"
  providers = {
    aws = aws.log_archive
  }
  trusted_entity = aws_iam_role.aft_admin_role.arn
}

module "audit_service_role" {
  source = "./service-role"
  providers = {
    aws = aws.audit
  }
  trusted_entity = aws_iam_role.aft_admin_role.arn
}

module "aft_service_role" {
  source = "./service-role"
  providers = {
    aws = aws.aft_management
  }
  trusted_entity = aws_iam_role.aft_admin_role.arn
}
