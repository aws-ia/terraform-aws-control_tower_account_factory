# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
###################################################################
# Step Functions - AFT Features
###################################################################

resource "aws_iam_role" "aft_features_sfn" {
  provider           = aws.aft_management
  name               = "aft-features-execution-role"
  assume_role_policy = templatefile("${path.module}/iam/trust-policies/states.tpl", { none = "none" })
}

resource "aws_iam_role_policy" "aft_features_sfn" {
  provider = aws.aft_management
  name     = "aft-features-policy"
  role     = aws_iam_role.aft_features_sfn.id

  policy = templatefile("${path.module}/iam/role-policies/aft_features_states.tpl", {
    data_aws_region_aft-management_name                = data.aws_region.current.name
    data_aws_caller_identity_aft-management_account_id = data.aws_caller_identity.current.id
  })

}

###################################################################
# Lambda - Delete Default VPC
###################################################################

resource "aws_iam_role" "aft_delete_default_vpc_lambda" {
  provider           = aws.aft_management
  name               = "aft-delete-default-vpc-execution-role"
  assume_role_policy = templatefile("${path.module}/iam/trust-policies/lambda.tpl", { none = "none" })
}

resource "aws_iam_role_policy" "aft_delete_default_vpc_lambda" {
  provider = aws.aft_management
  name     = "aft-delete-default-vpc-policy"
  role     = aws_iam_role.aft_delete_default_vpc_lambda.id

  policy = templatefile("${path.module}/iam/role-policies/aft_delete_default_vpc_lambda.tpl", {
    data_aws_caller_identity_current_account_id = data.aws_caller_identity.current.account_id
    data_aws_region_current_name                = data.aws_region.current.name
    aws_kms_key_aft_arn                         = var.aft_kms_key_arn
  })

}

resource "aws_iam_role_policy_attachment" "aft_delete_default_vpc_lambda" {
  provider   = aws.aft_management
  count      = length(local.lambda_managed_policies)
  role       = aws_iam_role.aft_delete_default_vpc_lambda.name
  policy_arn = local.lambda_managed_policies[count.index]
}

###################################################################
# Lambda - Enroll Support
###################################################################

resource "aws_iam_role" "aft_enroll_support" {
  provider           = aws.aft_management
  name               = "aft-enroll-support-execution-role"
  assume_role_policy = templatefile("${path.module}/iam/trust-policies/lambda.tpl", { none = "none" })
}

resource "aws_iam_role_policy" "aft_enroll_support" {
  provider = aws.aft_management
  name     = "aft-enroll-support-policy"
  role     = aws_iam_role.aft_enroll_support.id

  policy = templatefile("${path.module}/iam/role-policies/aft_enroll_support.tpl", {
    data_aws_caller_identity_current_account_id = data.aws_caller_identity.current.account_id
    data_aws_region_current_name                = data.aws_region.current.name
    aws_kms_key_aft_arn                         = var.aft_kms_key_arn
  })

}

resource "aws_iam_role_policy_attachment" "aft_enroll_support" {
  provider   = aws.aft_management
  count      = length(local.lambda_managed_policies)
  role       = aws_iam_role.aft_enroll_support.name
  policy_arn = local.lambda_managed_policies[count.index]
}

###################################################################
# Lambda - Enable Cloudtrail
###################################################################

resource "aws_iam_role" "aft_enable_cloudtrail" {
  provider           = aws.aft_management
  name               = "aft-enable-cloudtrail-execution-role"
  assume_role_policy = templatefile("${path.module}/iam/trust-policies/lambda.tpl", { none = "none" })
}

resource "aws_iam_role_policy" "aft_enable_cloudtrail" {
  provider = aws.aft_management
  name     = "aft-enable-cloudtrail-policy"
  role     = aws_iam_role.aft_enable_cloudtrail.id

  policy = templatefile("${path.module}/iam/role-policies/aft_enable_cloudtrail.tpl", {
    data_aws_caller_identity_current_account_id = data.aws_caller_identity.current.account_id
    data_aws_region_current_name                = data.aws_region.current.name
    aws_kms_key_aft_arn                         = var.aft_kms_key_arn
  })

}

resource "aws_iam_role_policy_attachment" "aft_enable_cloudtrail" {
  provider   = aws.aft_management
  count      = length(local.lambda_managed_policies)
  role       = aws_iam_role.aft_enable_cloudtrail.name
  policy_arn = local.lambda_managed_policies[count.index]
}
