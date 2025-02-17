# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

#tfsec:ignore:aws-lambda-enable-tracing
resource "aws_lambda_function" "codebuild_trigger" {
  filename         = var.builder_archive_path
  function_name    = local.codebuild_trigger_function_name
  description      = "AFT Lambda Layer - CodeBuild Trigger"
  role             = aws_iam_role.codebuild_trigger_lambda_role.arn
  handler          = "codebuild_trigger.lambda_handler"
  source_code_hash = var.builder_archive_hash
  memory_size      = 1024
  runtime          = var.lambda_runtime_python_version
  timeout          = 900
  dynamic "vpc_config" {
    for_each = var.aft_enable_vpc ? [1] : []
    content {
      subnet_ids         = var.aft_vpc_private_subnets
      security_group_ids = var.aft_vpc_default_sg
    }
  }
}

#tfsec:ignore:aws-cloudwatch-log-group-customer-key
resource "aws_cloudwatch_log_group" "codebuild_trigger_loggroup" {
  name              = "/aws/lambda/${aws_lambda_function.codebuild_trigger.function_name}"
  retention_in_days = var.cloudwatch_log_group_retention
}

data "aws_lambda_invocation" "trigger_codebuild_job" {
  function_name = aws_lambda_function.codebuild_trigger.function_name

  input = <<JSON
{
  "codebuild_project_name": "${aws_codebuild_project.codebuild.name}"
}
JSON
}

output "lambda_layer_build_status" {
  value = jsondecode(data.aws_lambda_invocation.trigger_codebuild_job.result)["Status"]
}
