# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#
resource "aws_cloudwatch_query_definition" "customization_request_query" {
  name = "Account Factory for Terraform/Customization Logs by Customization Request ID"

  log_group_names = [
    "/aws/lambda/${var.create_role_lambda_function_name}",
    "/aws/lambda/${var.persist_metadata_lambda_function_name}",
    "/aws/lambda/${var.tag_account_lambda_function_name}",
    "/aws/lambda/${var.account_metadata_ssm_lambda_function_name}",
    "/aws/lambda/${var.delete_default_vpc_lambda_function_name}",
    "/aws/lambda/${var.enroll_support_lambda_function_name}",
    "/aws/lambda/${var.enable_cloudtrail_lambda_function_name}",
  ]

  query_string = <<EOF
fields @timestamp, log_message.account_id as target_account_id, log_message.customization_request_id as customization_request_id, log_message.detail as detail, @logStream
| sort @timestamp desc
| filter log_message.customization_request_id == "INSERT-CUSTOMIZATION-REQUEST-ID-HERE"
EOF
}

resource "aws_cloudwatch_query_definition" "account_id_query" {
  name = "Account Factory for Terraform/Customization Logs by Account ID"

  log_group_names = [
    "/aws/lambda/${var.create_role_lambda_function_name}",
    "/aws/lambda/${var.persist_metadata_lambda_function_name}",
    "/aws/lambda/${var.tag_account_lambda_function_name}",
    "/aws/lambda/${var.account_metadata_ssm_lambda_function_name}",
    "/aws/lambda/${var.delete_default_vpc_lambda_function_name}",
    "/aws/lambda/${var.enroll_support_lambda_function_name}",
    "/aws/lambda/${var.enable_cloudtrail_lambda_function_name}",
  ]

  query_string = <<EOF
fields @timestamp, log_message.account_id as target_account_id, log_message.customization_request_id as customization_request_id, log_message.detail as detail, @logStream
| sort @timestamp desc
| filter log_message.account_id == "INSERT-ACCOUNT-ID-HERE" and @message like /customization_request_id/
EOF
}
