# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#
locals {
  state_machine_source = "${path.module}/states/aft_features.asl.json"
  replacements_map = {
    aft_delete_default_vpc_function_arn = aws_lambda_function.aft_delete_default_vpc.arn
    aft_enroll_support_function_arn     = aws_lambda_function.aft_enroll_support.arn
    aft_enable_cloudtrail_function_arn  = aws_lambda_function.aft_enable_cloudtrail.arn
    aft_notification_arn                = var.aft_sns_topic_arn
    aft_failure_notification_arn        = var.aft_failure_sns_topic_arn
  }
}

resource "aws_sfn_state_machine" "aft_features" {
  provider   = aws.aft_management
  name       = var.aft_features_sfn_name
  role_arn   = aws_iam_role.aft_features_sfn.arn
  definition = templatefile(local.state_machine_source, local.replacements_map)
}
