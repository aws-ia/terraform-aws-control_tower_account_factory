# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
resource "aws_iam_role" "codebuild" {
  name               = local.common_name
  assume_role_policy = file("${path.module}/iam/trust-policies/codebuild.tpl")
}

resource "aws_iam_role" "codebuild_trigger_lambda_role" {
  name               = "codebuild_trigger_role"
  assume_role_policy = file("${path.module}/iam/trust-policies/lambda.tpl")
}

resource "aws_iam_role_policy" "codebuild" {
  role = aws_iam_role.codebuild.name
  policy = templatefile("${path.module}/iam/role-policies/codebuild.tpl", {
    "data_aws_partition_current_partition"      = data.aws_partition.current.partition
    "aws_region"                                = var.aws_region
    "account_id"                                = local.account_id
    "layer_name"                                = var.lambda_layer_name
    "s3_bucket_name"                            = var.s3_bucket_name
    "data_aws_kms_alias_aft_key_target_key_arn" = var.aft_kms_key_arn
  })
}

resource "aws_iam_role_policy" "codebuild_trigger_policy" {
  role = aws_iam_role.codebuild_trigger_lambda_role.name
  policy = templatefile("${path.module}/iam/role-policies/codebuild-trigger.tpl", {
    "data_aws_partition_current_partition" = data.aws_partition.current.partition
    "aws_region"                           = var.aws_region
    "account_id"                           = local.account_id
    "codebuild_project_name"               = aws_codebuild_project.codebuild.name
    "codebuild_trigger_function_name"      = local.codebuild_trigger_function_name
  })
}

resource "aws_iam_role_policy_attachment" "codebuild_trigger_VPC_access" {
  role       = aws_iam_role.codebuild_trigger_lambda_role.name
  policy_arn = "arn:${data.aws_partition.current.partition}:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}
