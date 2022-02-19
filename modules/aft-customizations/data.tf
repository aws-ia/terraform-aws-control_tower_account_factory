# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
data "aws_region" "current" {}

data "aws_caller_identity" "current" {}

data "aws_region" "aft_management" {}
data "aws_caller_identity" "aft_management" {}

data "aws_iam_policy" "AWSLambdaBasicExecutionRole" {
  name = "AWSLambdaBasicExecutionRole"
}

data "aws_iam_policy" "AWSLambdaVPCAccessExecutionRole" {
  name = "AWSLambdaVPCAccessExecutionRole"
}

data "local_file" "aft_global_customizations_terraform" {
  filename = "${path.module}/buildspecs/aft-global-customizations-terraform.yml"
}

data "local_file" "aft_global_customizations_api_helpers" {
  filename = "${path.module}/buildspecs/aft-global-customizations-api-helpers.yml"
}

data "local_file" "aft_account_customizations_terraform" {
  filename = "${path.module}/buildspecs/aft-account-customizations-terraform.yml"
}

data "local_file" "aft_account_customizations_api_helpers" {
  filename = "${path.module}/buildspecs/aft-account-customizations-api-helpers.yml"
}

data "local_file" "aft_create_pipeline" {
  filename = "${path.module}/buildspecs/aft-create-pipeline.yml"
}
