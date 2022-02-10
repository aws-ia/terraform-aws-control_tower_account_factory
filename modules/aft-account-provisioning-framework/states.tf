# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#
locals {
  state_machine_source = "${path.module}/states/aft_account_provisioning_framework.asl.json"
  replacements_map = {
    validate_request_function_name                                    = aws_lambda_function.validate_request.function_name
    get_account_info_function_name                                    = aws_lambda_function.get_account_info.function_name
    create_role_function_name                                         = aws_lambda_function.create_role.function_name
    tag_account_function_name                                         = aws_lambda_function.tag_account.function_name
    persist_metadata_function_name                                    = aws_lambda_function.persist_metadata.function_name
    account_metadata_ssm_function_name                                = aws_lambda_function.account_metadata_ssm.function_name
    aft_notification_arn                                              = var.aft_sns_topic_arn
    aft_failure_notification_arn                                      = var.aft_failure_sns_topic_arn
    aft_account_provisioning_customizations_state_machine_arn         = "arn:aws:states:${data.aws_region.aft_management.name}:${data.aws_caller_identity.aft_management.account_id}:stateMachine:${var.aft_account_provisioning_customizations_sfn_name}"
    customizations_trigger_state_machine_arn                          = "arn:aws:states:${data.aws_region.aft_management.name}:${data.aws_caller_identity.aft_management.account_id}:stateMachine:${var.trigger_customizations_sfn_name}"
    aft_account_provisioning_framework_aft_features_state_machine_arn = "arn:aws:states:${data.aws_region.aft_management.name}:${data.aws_caller_identity.aft_management.account_id}:stateMachine:${var.aft_features_sfn_name}"
  }
}

resource "aws_sfn_state_machine" "aft_account_provisioning_framework_sfn" {
  name       = var.aft_account_provisioning_framework_sfn_name
  role_arn   = aws_iam_role.aft_states.arn
  definition = templatefile(local.state_machine_source, local.replacements_map)
}
