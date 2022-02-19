# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
data "aws_region" "current" {}

data "aws_caller_identity" "current" {}

data "aws_ssm_parameter" "aft_vcs_type" {
  name = "/aft/config/vcs/provider"
}

data "aws_ssm_parameter" "codestar_connection_arn" {
  name = "/aft/config/vcs/codestar-connection-arn"
}

data "aws_ssm_parameter" "aft_global_customizations_repo_name" {
  name = "/aft/config/global-customizations/repo-name"
}

data "aws_ssm_parameter" "aft_global_customizations_repo_branch" {
  name = "/aft/config/global-customizations/repo-branch"
}

data "aws_ssm_parameter" "aft_account_customizations_repo_name" {
  name = "/aft/config/account-customizations/repo-name"
}

data "aws_ssm_parameter" "aft_account_customizations_repo_branch" {
  name = "/aft/config/account-customizations/repo-branch"
}

# Lookups from terraform-aws-aft-pipeline-framework customizations module
data "aws_kms_alias" "aft_key" {
  name = "alias/aft"
}

data "aws_iam_role" "aft_codepipeline_customizations_role" {
  name = "aft-codepipeline-customizations-role"
}

data "aws_s3_bucket" "aft_codepipeline_customizations_bucket" {
  bucket = "aft-customizations-pipeline-${data.aws_caller_identity.current.account_id}"
}

data "aws_ssm_parameter" "vcs_provider" {
  name = "/aft/config/vcs/provider"
}
