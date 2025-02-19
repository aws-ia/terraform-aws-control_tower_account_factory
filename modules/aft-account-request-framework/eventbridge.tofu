# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
######### Control Tower Event Bus #########
resource "aws_cloudwatch_event_bus" "aft_from_ct_management" {
  name = "aft-events-from-ct-management"
}

resource "aws_cloudwatch_event_permission" "control_tower_management_account" {
  principal      = data.aws_caller_identity.ct-management.account_id
  statement_id   = "control_tower_management_account"
  event_bus_name = aws_cloudwatch_event_bus.aft_from_ct_management.name
}

######### Control Tower Events - CT Management #########
resource "aws_cloudwatch_event_rule" "aft_control_tower_events" {
  provider      = aws.ct_management
  name          = "aft-capture-ct-events"
  description   = "Capture ControlTower events"
  event_pattern = <<EOF
{
  "source": ["aws.controltower"],
  "detail-type": ["AWS Service Event via CloudTrail"],
  "detail": {
    "eventName": ["CreateManagedAccount", "UpdateManagedAccount"]
  }
}
EOF
}

resource "aws_cloudwatch_event_target" "aft_management_event_bus" {
  provider = aws.ct_management
  arn      = aws_cloudwatch_event_bus.aft_from_ct_management.arn
  rule     = aws_cloudwatch_event_rule.aft_control_tower_events.id
  role_arn = aws_iam_role.aft_control_tower_events.arn
}

######### Control Tower Event Logger #########
resource "aws_cloudwatch_event_rule" "aft_controltower_event_trigger" {
  name           = "aft-controltower-event-logger"
  description    = "Send CT Events to Lambda"
  event_bus_name = aws_cloudwatch_event_bus.aft_from_ct_management.name
  event_pattern  = <<EOF
{
  "account": ["${data.aws_caller_identity.ct-management.account_id}"]
}
EOF
}

resource "aws_cloudwatch_event_target" "aft_controltower_event_logger" {
  rule           = aws_cloudwatch_event_rule.aft_controltower_event_trigger.name
  arn            = aws_lambda_function.aft_controltower_event_logger.arn
  event_bus_name = aws_cloudwatch_event_bus.aft_from_ct_management.name
}

######### AFT invoke AFT Account Provisioning Framework #########

resource "aws_cloudwatch_event_target" "aft_invoke_aft_account_provisioning_framework" {
  rule           = aws_cloudwatch_event_rule.aft_controltower_event_trigger.name
  arn            = aws_lambda_function.aft_invoke_aft_account_provisioning_framework.arn
  event_bus_name = aws_cloudwatch_event_bus.aft_from_ct_management.name
}

######### Account Processor Lambda #########
resource "aws_cloudwatch_event_rule" "aft_account_request_processor" {
  name                = "aft-lambda-account-request-processor"
  description         = "Trigger Lambda"
  schedule_expression = "rate(5 minutes)"
}

resource "aws_cloudwatch_event_target" "aft_account_request_processor" {
  arn  = aws_lambda_function.aft_account_request_processor.arn
  rule = aws_cloudwatch_event_rule.aft_account_request_processor.id
}
