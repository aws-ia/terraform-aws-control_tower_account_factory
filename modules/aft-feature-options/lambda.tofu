# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
######## aft_delete_default_vpc ########
#tfsec:ignore:aws-lambda-enable-tracing
resource "aws_lambda_function" "aft_delete_default_vpc" {
  provider      = aws.aft_management
  filename      = var.feature_options_archive_path
  function_name = var.delete_default_vpc_lambda_function_name
  description   = "Deletes default VPCs in all regions. Called from aft-features SFN."
  role          = aws_iam_role.aft_delete_default_vpc_lambda.arn
  handler       = "aft_delete_default_vpc.lambda_handler"

  source_code_hash = var.feature_options_archive_hash
  memory_size      = 1024
  runtime          = var.lambda_runtime_python_version
  timeout          = "300"
  layers           = [var.aft_common_layer_arn]

  dynamic "vpc_config" {
    for_each = var.aft_enable_vpc ? [1] : []

    content {
      subnet_ids         = var.aft_vpc_private_subnets
      security_group_ids = var.aft_vpc_default_sg
    }
  }
}

#tfsec:ignore:aws-cloudwatch-log-group-customer-key
resource "aws_cloudwatch_log_group" "aft_delete_default_vpc" {
  provider          = aws.aft_management
  name              = "/aws/lambda/${aws_lambda_function.aft_delete_default_vpc.function_name}"
  retention_in_days = var.cloudwatch_log_group_retention
}


######## aft_enroll_support ########
#tfsec:ignore:aws-lambda-enable-tracing
resource "aws_lambda_function" "aft_enroll_support" {
  provider      = aws.aft_management
  filename      = var.feature_options_archive_path
  function_name = var.enroll_support_lambda_function_name
  description   = "Creates request to enroll an account in Enterprise support. Called from aft-features SFN."
  role          = aws_iam_role.aft_enroll_support.arn
  handler       = "aft_enroll_support.lambda_handler"

  source_code_hash = var.feature_options_archive_hash
  memory_size      = 1024
  runtime          = var.lambda_runtime_python_version
  timeout          = "300"
  layers           = [var.aft_common_layer_arn]

  dynamic "vpc_config" {
    for_each = var.aft_enable_vpc ? [1] : []

    content {
      subnet_ids         = var.aft_vpc_private_subnets
      security_group_ids = var.aft_vpc_default_sg
    }
  }
}

#tfsec:ignore:aws-cloudwatch-log-group-customer-key
resource "aws_cloudwatch_log_group" "aft_enroll_support" {
  provider          = aws.aft_management
  name              = "/aws/lambda/${aws_lambda_function.aft_enroll_support.function_name}"
  retention_in_days = var.cloudwatch_log_group_retention
}

######## aft_enable_cloudtrail ########
#tfsec:ignore:aws-lambda-enable-tracing
resource "aws_lambda_function" "aft_enable_cloudtrail" {
  provider      = aws.aft_management
  filename      = var.feature_options_archive_path
  function_name = var.enable_cloudtrail_lambda_function_name
  description   = "Creates an Org Trail to capture data events. Called from aft-features SFN."
  role          = aws_iam_role.aft_enable_cloudtrail.arn
  handler       = "aft_enable_cloudtrail.lambda_handler"

  source_code_hash = var.feature_options_archive_hash
  memory_size      = 1024
  runtime          = var.lambda_runtime_python_version
  timeout          = "300"
  layers           = [var.aft_common_layer_arn]

  dynamic "vpc_config" {
    for_each = var.aft_enable_vpc ? [1] : []

    content {
      subnet_ids         = var.aft_vpc_private_subnets
      security_group_ids = var.aft_vpc_default_sg
    }
  }
}

#tfsec:ignore:aws-cloudwatch-log-group-customer-key
resource "aws_cloudwatch_log_group" "aft_enable_cloudtrail" {
  provider          = aws.aft_management
  name              = "/aws/lambda/${aws_lambda_function.aft_enable_cloudtrail.function_name}"
  retention_in_days = var.cloudwatch_log_group_retention
}
