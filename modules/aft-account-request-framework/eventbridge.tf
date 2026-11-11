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

# A timed-out execution of aft-organizations-account-provisioning runs none of
# its states, so its NotifyFailure step cannot report it. This rule sends the
# status-change event to the same Lambda. FAILED is not matched: every failed
# execution has already been reported by its NotifyFailure step.
resource "aws_cloudwatch_event_rule" "aft_organizations_account_provisioning_timed_out" {
  count       = local.service_catalog_backend ? 0 : 1
  name        = "aft-organizations-account-provisioning-timed-out"
  description = "Report timed-out executions of the organizations account-provisioning Step Function"
  event_pattern = jsonencode({
    source        = ["aws.states"]
    "detail-type" = ["Step Functions Execution Status Change"]
    detail = {
      status          = ["TIMED_OUT"]
      stateMachineArn = [aws_sfn_state_machine.aft_organizations_account_provisioning[0].arn]
    }
  })
}

resource "aws_cloudwatch_event_target" "aft_organizations_account_provisioning_timed_out" {
  count = local.service_catalog_backend ? 0 : 1
  rule  = aws_cloudwatch_event_rule.aft_organizations_account_provisioning_timed_out[0].name
  arn   = aws_lambda_function.aft_organizations_account_provisioning["notify_failure"].arn
}

resource "aws_lambda_permission" "aft_organizations_account_provisioning_timed_out" {
  count         = local.service_catalog_backend ? 0 : 1
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.aft_organizations_account_provisioning["notify_failure"].function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.aft_organizations_account_provisioning_timed_out[0].arn
}

######### Organizations vending method lifecycle events #########
# The organizations provisioning Step Function publishes aft.organizations
# events onto the AFT bus from the AFT management account. Match only those:
# the source, the account the state machine publishes from, and the detail
# type it sets. The bus also accepts events from the CT management account, so
# the source alone does not identify the publisher. Fan out to the same two
# consumers as native Control Tower events. Only created for the Organizations
# vending method.
resource "aws_cloudwatch_event_rule" "aft_organizations_lifecycle_events" {
  count          = local.service_catalog_backend ? 0 : 1
  name           = "aft-organizations-lifecycle-events"
  description    = "Route aft.organizations lifecycle events to the AFT consumers"
  event_bus_name = aws_cloudwatch_event_bus.aft_from_ct_management.name
  event_pattern = jsonencode({
    source        = ["aft.organizations"]
    account       = [data.aws_caller_identity.aft-management.account_id]
    "detail-type" = ["AFT Account Provisioning"]
  })
}

resource "aws_cloudwatch_event_target" "aft_organizations_event_logger" {
  count          = local.service_catalog_backend ? 0 : 1
  rule           = aws_cloudwatch_event_rule.aft_organizations_lifecycle_events[0].name
  arn            = aws_lambda_function.aft_controltower_event_logger.arn
  event_bus_name = aws_cloudwatch_event_bus.aft_from_ct_management.name
}

resource "aws_cloudwatch_event_target" "aft_organizations_invoke_provisioning_framework" {
  count          = local.service_catalog_backend ? 0 : 1
  rule           = aws_cloudwatch_event_rule.aft_organizations_lifecycle_events[0].name
  arn            = aws_lambda_function.aft_invoke_aft_account_provisioning_framework.arn
  event_bus_name = aws_cloudwatch_event_bus.aft_from_ct_management.name
}
