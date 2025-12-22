# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
######### invoke_aft_account_provisioning_framework #########

# Create Role Lambda Permissions
resource "aws_iam_role" "aft_lambda_aft_account_provisioning_framework_create_role" {
  name               = "aft-account-provisioning-framework-lambda-create-role-role"
  assume_role_policy = templatefile("${path.module}/iam/trust-policies/lambda.tpl", { none = "none" })
}

resource "aws_iam_role_policy_attachment" "aft_account_provisioning_framework_create_role" {
  count      = length(local.lambda_managed_policies)
  role       = aws_iam_role.aft_lambda_aft_account_provisioning_framework_create_role.name
  policy_arn = local.lambda_managed_policies[count.index]
}

resource "aws_iam_role_policy" "aft_invoke_aft_account_provisioning_framework_create_role" {
  name = "aft-lambda-invoke-aft_account_provisioning_framework-create-role-policy"
  role = aws_iam_role.aft_lambda_aft_account_provisioning_framework_create_role.id
  policy = templatefile("${path.module}/iam/role-policies/lambda-aft-account-provisioning-framework.tpl", {
    data_aws_partition_current_partition               = data.aws_partition.current.partition
    data_aws_region_aft-management_name                = data.aws_region.aft_management.region
    data_aws_caller_identity_aft-management_account_id = data.aws_caller_identity.aft_management.account_id
    aft_sns_topic_arn                                  = var.aft_sns_topic_arn
    aft_failure_sns_topic_arn                          = var.aft_failure_sns_topic_arn
    aws_kms_key_aft_arn                                = var.aft_kms_key_arn
  })
}

# Tag Account Lambda Permissions
resource "aws_iam_role" "aft_lambda_aft_account_provisioning_framework_tag_account" {
  name               = "aft-account-provisioning-framework-lambda-tag-account-role"
  assume_role_policy = templatefile("${path.module}/iam/trust-policies/lambda.tpl", { none = "none" })
}

resource "aws_iam_role_policy_attachment" "aft_account_provisioning_framework_tag_account" {
  count      = length(local.lambda_managed_policies)
  role       = aws_iam_role.aft_lambda_aft_account_provisioning_framework_tag_account.name
  policy_arn = local.lambda_managed_policies[count.index]
}

resource "aws_iam_role_policy" "aft_invoke_aft_account_provisioning_framework_tag_account" {
  name = "aft-lambda-invoke-aft-account-provisioning-framework-tag-account-policy"
  role = aws_iam_role.aft_lambda_aft_account_provisioning_framework_tag_account.id
  policy = templatefile("${path.module}/iam/role-policies/lambda-aft-account-provisioning-framework.tpl", {
    data_aws_partition_current_partition               = data.aws_partition.current.partition
    data_aws_region_aft-management_name                = data.aws_region.aft_management.region
    data_aws_caller_identity_aft-management_account_id = data.aws_caller_identity.aft_management.account_id
    aft_sns_topic_arn                                  = var.aft_sns_topic_arn
    aft_failure_sns_topic_arn                          = var.aft_failure_sns_topic_arn
    aws_kms_key_aft_arn                                = var.aft_kms_key_arn
  })
}

# Persist Metadata Lambda Permissions
resource "aws_iam_role" "aft_lambda_aft_account_provisioning_framework_persist_metadata" {
  name               = "aft-account-provisioning-framework-lambda-persist-metadata-role"
  assume_role_policy = templatefile("${path.module}/iam/trust-policies/lambda.tpl", { none = "none" })
}

resource "aws_iam_role_policy_attachment" "aft_account_provisioning_framework_persist_metadata" {
  count      = length(local.lambda_managed_policies)
  role       = aws_iam_role.aft_lambda_aft_account_provisioning_framework_persist_metadata.name
  policy_arn = local.lambda_managed_policies[count.index]
}

resource "aws_iam_role_policy" "aft_invoke_aft_account_provisioning_framework_persist_metadata" {
  name = "aft-lambda-invoke-aft-account-provisioning-framework-persist-metadata-policy"
  role = aws_iam_role.aft_lambda_aft_account_provisioning_framework_persist_metadata.id
  policy = templatefile("${path.module}/iam/role-policies/lambda-aft-account-provisioning-framework.tpl", {
    data_aws_partition_current_partition               = data.aws_partition.current.partition
    data_aws_region_aft-management_name                = data.aws_region.aft_management.region
    data_aws_caller_identity_aft-management_account_id = data.aws_caller_identity.aft_management.account_id
    aft_sns_topic_arn                                  = var.aft_sns_topic_arn
    aft_failure_sns_topic_arn                          = var.aft_failure_sns_topic_arn
    aws_kms_key_aft_arn                                = var.aft_kms_key_arn
  })
}

######### states_execution_role #########

resource "aws_iam_role" "aft_states" {
  name               = "aft-states-execution-role"
  assume_role_policy = templatefile("${path.module}/iam/trust-policies/states.tpl", { none = "none" })
}

resource "aws_iam_role_policy" "aft_states" {
  name = "aft-account-provisioning-framework-states-policy"
  role = aws_iam_role.aft_states.id

  policy = templatefile("${path.module}/iam/role-policies/iam-aft-states.tpl", {
    data_aws_partition_current_partition               = data.aws_partition.current.partition
    data_aws_region_aft-management_name                = data.aws_region.aft_management.region
    data_aws_caller_identity_aft-management_account_id = data.aws_caller_identity.aft_management.account_id
    aws_kms_key_aft_arn                                = var.aft_kms_key_arn
    sns_topic_enable_cmk_encryption                    = var.sns_topic_enable_cmk_encryption
  })
}
