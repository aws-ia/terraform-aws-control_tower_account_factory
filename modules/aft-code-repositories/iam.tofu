# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# CodePipeline Roles

resource "aws_iam_role" "account_request_codepipeline_role" {
  name               = "ct-aft-codepipeline-account-request-role"
  assume_role_policy = templatefile("${path.module}/iam/trust-policies/codepipeline.tpl", { none = "none" })
}

resource "aws_iam_role_policy" "account_request_codepipeline_policy" {
  name = "ct-aft-codepipeline-account-request-policy"
  role = aws_iam_role.account_request_codepipeline_role.id

  policy = templatefile("${path.module}/iam/role-policies/ct_aft_account_request_codepipeline_policy.tpl", {
    aws_s3_bucket_aft_codepipeline_customizations_bucket_arn = var.codepipeline_s3_bucket_arn
    data_aws_partition_current_partition                     = data.aws_partition.current.partition
    data_aws_region_current_name                             = data.aws_region.current.name
    data_aws_caller_identity_current_account_id              = data.aws_caller_identity.current.account_id
    data_aws_kms_alias_aft_key_target_key_arn                = var.aft_key_arn
  })
}

resource "aws_iam_role" "account_provisioning_customizations_codepipeline_role" {
  name               = "ct-aft-codepipeline-account-provisioning-customizations-role"
  assume_role_policy = templatefile("${path.module}/iam/trust-policies/codepipeline.tpl", { none = "none" })
}

resource "aws_iam_role_policy" "account_provisioning_customizations_codepipeline_policy" {
  name = "ct-aft-codepipeline-account-provisioning-customizations-policy"
  role = aws_iam_role.account_provisioning_customizations_codepipeline_role.id

  policy = templatefile("${path.module}/iam/role-policies/ct_aft_account_provisioning_customizations_codepipeline_policy.tpl", {
    aws_s3_bucket_aft_codepipeline_customizations_bucket_arn = var.codepipeline_s3_bucket_arn
    data_aws_partition_current_partition                     = data.aws_partition.current.partition
    data_aws_region_current_name                             = data.aws_region.current.name
    data_aws_caller_identity_current_account_id              = data.aws_caller_identity.current.account_id
    data_aws_kms_alias_aft_key_target_key_arn                = var.aft_key_arn
  })
}

# Codebuild Role

resource "aws_iam_role" "account_provisioning_customizations_codebuild_role" {
  name               = "ct-aft-codebuild-account-provisioning-customizations-role"
  assume_role_policy = templatefile("${path.module}/iam/trust-policies/codebuild.tpl", { none = "none" })
}

resource "aws_iam_role_policy" "account_provisioning_customizations_codebuild_policy" {
  name = "ct-aft-codebuild-account-provisioning-customizations-policy"
  role = aws_iam_role.account_provisioning_customizations_codebuild_role.id

  policy = templatefile("${path.module}/iam/role-policies/ct_aft_codebuild_policy.tpl", {
    aws_s3_bucket_aft_codepipeline_customizations_bucket_arn = var.codepipeline_s3_bucket_arn
    data_aws_partition_current_partition                     = data.aws_partition.current.partition
    data_aws_region_current_name                             = data.aws_region.current.name
    data_aws_caller_identity_current_account_id              = data.aws_caller_identity.current.account_id
    data_aws_kms_alias_aft_key_target_key_arn                = var.aft_key_arn
    data_aws_dynamo_account_request_table                    = var.account_request_table_name
  })
}

resource "aws_iam_role_policy" "terraform_oss_backend_account_provisioning_customizations_codebuild_policy" {
  name = "ct-aft-codebuild-terraform-oss-backend-policy"
  role = aws_iam_role.account_provisioning_customizations_codebuild_role.id

  policy = templatefile("${path.module}/iam/role-policies/ct_aft_codebuild_oss_backend_policy.tpl", {
    data_aws_partition_current_partition              = data.aws_partition.current.partition
    data_aws_region_current_name                      = data.aws_region.current.name
    data_aws_caller_identity_current_account_id       = data.aws_caller_identity.current.account_id
    data_aws_dynamo_terraform_oss_backend_table       = var.aft_config_backend_table_id
    aws_s3_bucket_aft_terraform_oss_backend_bucket_id = var.aft_config_backend_bucket_id
    aws_s3_bucket_aft_terraform_oss_kms_key_id        = var.aft_config_backend_kms_key_id
  })
}

resource "aws_iam_role" "account_request_codebuild_role" {
  name               = "ct-aft-codebuild-account-request-role"
  assume_role_policy = templatefile("${path.module}/iam/trust-policies/codebuild.tpl", { none = "none" })
}

resource "aws_iam_role_policy" "account_request_codebuild_policy" {
  name = "ct-aft-codebuild-account-request-policy"
  role = aws_iam_role.account_request_codebuild_role.id

  policy = templatefile("${path.module}/iam/role-policies/ct_aft_codebuild_policy.tpl", {
    aws_s3_bucket_aft_codepipeline_customizations_bucket_arn = var.codepipeline_s3_bucket_arn
    data_aws_partition_current_partition                     = data.aws_partition.current.partition
    data_aws_region_current_name                             = data.aws_region.current.name
    data_aws_caller_identity_current_account_id              = data.aws_caller_identity.current.account_id
    data_aws_kms_alias_aft_key_target_key_arn                = var.aft_key_arn
    data_aws_dynamo_account_request_table                    = var.account_request_table_name
  })
}

resource "aws_iam_role_policy" "terraform_oss_backend_account_request_codebuild_policy" {
  name = "ct-aft-codebuild-terraform-oss-backend-policy"
  role = aws_iam_role.account_request_codebuild_role.id

  policy = templatefile("${path.module}/iam/role-policies/ct_aft_codebuild_oss_backend_policy.tpl", {
    data_aws_partition_current_partition              = data.aws_partition.current.partition
    data_aws_region_current_name                      = data.aws_region.current.name
    data_aws_caller_identity_current_account_id       = data.aws_caller_identity.current.account_id
    data_aws_dynamo_terraform_oss_backend_table       = var.aft_config_backend_table_id
    aws_s3_bucket_aft_terraform_oss_backend_bucket_id = var.aft_config_backend_bucket_id
    aws_s3_bucket_aft_terraform_oss_kms_key_id        = var.aft_config_backend_kms_key_id
  })
}

resource "time_sleep" "iam_eventual_consistency" {
  depends_on      = [aws_iam_role.account_request_codebuild_role]
  create_duration = "60s"
}

# CloudWatch Events Role

resource "aws_iam_role" "cloudwatch_events_codepipeline_role" {
  count              = local.vcs.is_codecommit ? 1 : 0
  name               = "ct-aft-cwe-codepipeline-role"
  assume_role_policy = templatefile("${path.module}/iam/trust-policies/events.tpl", { none = "none" })
}

resource "aws_iam_role_policy" "cloudwatch_events_codepipeline_role" {
  count = local.vcs.is_codecommit ? 1 : 0
  name  = "ct-aft-cwe-codepipeline-role-policy"
  role  = aws_iam_role.cloudwatch_events_codepipeline_role[0].id

  policy = templatefile("${path.module}/iam/role-policies/ct_aft_cwe_policy.tpl", {
    data_aws_partition_current_partition      = data.aws_partition.current.partition
    region                                    = data.aws_region.current.name
    account_id                                = data.aws_caller_identity.current.account_id
    account_request_pipeline_name             = aws_codepipeline.codecommit_account_request[0].name
    provisioning_customizations_pipeline_name = aws_codepipeline.codecommit_account_provisioning_customizations[0].name
  })
}
