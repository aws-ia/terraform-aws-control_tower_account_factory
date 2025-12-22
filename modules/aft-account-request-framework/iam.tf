# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
######### Control Tower Events - CT Management #########
resource "aws_iam_role" "aft_control_tower_events" {
  provider           = aws.ct_management
  name               = "aft-control-tower-events-rule"
  assume_role_policy = templatefile("${path.module}/iam/trust-policies/events.tpl", { none = "none" })
}

resource "aws_iam_role_policy" "control_tower_events" {
  provider = aws.ct_management
  name     = "control-tower-events"
  role     = aws_iam_role.aft_control_tower_events.id

  policy = templatefile("${path.module}/iam/role-policies/events-control-tower-events.tpl", {
    aws_cloudwatch_event_bus_from-ct-management_arn = aws_cloudwatch_event_bus.aft_from_ct_management.arn
  })
}

######### aft_account_request_audit_trigger #########

resource "aws_iam_role" "aft_account_request_audit_trigger" {
  name               = "aft-lambda-account-request-audit-trigger"
  assume_role_policy = templatefile("${path.module}/iam/trust-policies/lambda.tpl", { none = "none" })
}

resource "aws_iam_role_policy_attachment" "aft_account_request_audit_trigger" {
  count      = length(local.lambda_managed_policies)
  role       = aws_iam_role.aft_account_request_audit_trigger.name
  policy_arn = local.lambda_managed_policies[count.index]
}

resource "aws_iam_role_policy" "aft_account_request_audit_trigger" {
  name = "aft-account-request-audit-trigger"
  role = aws_iam_role.aft_account_request_audit_trigger.id

  policy = templatefile("${path.module}/iam/role-policies/lambda-account-request-audit-trigger.tpl", {
    data_aws_partition_current_partition               = data.aws_partition.current.partition
    data_aws_region_aft-management_name                = data.aws_region.aft-management.region
    data_aws_caller_identity_aft-management_account_id = data.aws_caller_identity.aft-management.account_id
    aws_sns_topic_aft_notifications_arn                = aws_sns_topic.aft_notifications.arn
    aws_sns_topic_aft_failure_notifications_arn        = aws_sns_topic.aft_failure_notifications.arn
    aws_dynamodb_table_aft-request_name                = aws_dynamodb_table.aft_request.name
    aws_dynamodb_table_aft-request-audit_name          = aws_dynamodb_table.aft_request_audit.name
    aws_sqs_queue_aft_account_request_arn              = aws_sqs_queue.aft_account_request.arn
    aws_kms_key_aft_arn                                = aws_kms_key.aft.arn
  })
}

######### aft_account_request_action_trigger #########

resource "aws_iam_role" "aft_account_request_action_trigger" {
  name               = "aft-lambda-account-request-action-trigger"
  assume_role_policy = templatefile("${path.module}/iam/trust-policies/lambda.tpl", { none = "none" })
}

resource "aws_iam_role_policy_attachment" "aft_account_request_action_trigger" {
  count      = length(local.lambda_managed_policies)
  role       = aws_iam_role.aft_account_request_action_trigger.name
  policy_arn = local.lambda_managed_policies[count.index]
}

resource "aws_iam_role_policy" "aft_account_request_action_trigger" {
  name = "aft-account-request-action-trigger"
  role = aws_iam_role.aft_account_request_action_trigger.id

  policy = templatefile("${path.module}/iam/role-policies/lambda-account-request-action-trigger.tpl", {
    data_aws_partition_current_partition                              = data.aws_partition.current.partition
    data_aws_region_aft-management_name                               = data.aws_region.aft-management.region
    data_aws_caller_identity_aft-management_account_id                = data.aws_caller_identity.aft-management.account_id
    aws_sns_topic_aft_notifications_arn                               = aws_sns_topic.aft_notifications.arn
    aws_sns_topic_aft_failure_notifications_arn                       = aws_sns_topic.aft_failure_notifications.arn
    aws_lambda_function_invoke_aft_account_provisioning_framework_arn = aws_lambda_function.aft_invoke_aft_account_provisioning_framework.arn
    aws_lambda_function_cleanup_resources_arn                         = aws_lambda_function.aft_cleanup_resources.arn
    aws_sqs_queue_aft_account_request_arn                             = aws_sqs_queue.aft_account_request.arn
    aws_kms_key_aft_arn                                               = aws_kms_key.aft.arn
    aws_dynamodb_table_aft-request_name                               = aws_dynamodb_table.aft_request.name
    aws_dynamodb_table_aft-request-audit_name                         = aws_dynamodb_table.aft_request_audit.name
  })
}

######### controltower_event_logger #########
resource "aws_iam_role" "aft_controltower_event_logger" {
  name               = "aft-lambda-controltower-event-logger"
  assume_role_policy = templatefile("${path.module}/iam/trust-policies/lambda.tpl", { none = "none" })
}

resource "aws_iam_role_policy_attachment" "aft_controltower_event_logger" {
  count      = length(local.lambda_managed_policies)
  role       = aws_iam_role.aft_controltower_event_logger.name
  policy_arn = local.lambda_managed_policies[count.index]
}

resource "aws_iam_role_policy" "aft_controltower_event_logger" {
  name = "aft-controltower-event-logger"
  role = aws_iam_role.aft_controltower_event_logger.id

  policy = templatefile("${path.module}/iam/role-policies/lambda-controltower-event-logger.tpl", {
    data_aws_partition_current_partition               = data.aws_partition.current.partition
    data_aws_region_aft-management_name                = data.aws_region.aft-management.region
    data_aws_caller_identity_aft-management_account_id = data.aws_caller_identity.aft-management.account_id
    aws_dynamodb_table_controltower-events_name        = aws_dynamodb_table.aft_controltower_events.name
    aws_sns_topic_aft_notifications_arn                = aws_sns_topic.aft_notifications.arn
    aws_sns_topic_aft_failure_notifications_arn        = aws_sns_topic.aft_failure_notifications.arn
    aws_kms_key_aft_arn                                = aws_kms_key.aft.arn
  })
}

######### account_request_processor #########
resource "aws_iam_role" "aft_account_request_processor" {
  name               = "aft-lambda-account-request-processor"
  assume_role_policy = templatefile("${path.module}/iam/trust-policies/lambda.tpl", { none = "none" })
}

resource "aws_iam_role_policy_attachment" "account_request_processor" {
  count      = length(local.lambda_managed_policies)
  role       = aws_iam_role.aft_account_request_processor.name
  policy_arn = local.lambda_managed_policies[count.index]
}

resource "aws_iam_role_policy" "aft_account_request_processor" {
  name = "aft-account-request-processor"
  role = aws_iam_role.aft_account_request_processor.id

  policy = templatefile("${path.module}/iam/role-policies/lambda-account-request-processor.tpl", {
    data_aws_partition_current_partition               = data.aws_partition.current.partition
    data_aws_region_aft-management_name                = data.aws_region.aft-management.region
    data_aws_caller_identity_aft-management_account_id = data.aws_caller_identity.aft-management.account_id
    aws_kms_key_aft_arn                                = aws_kms_key.aft.arn
    aws_sns_topic_aft_notifications_arn                = aws_sns_topic.aft_notifications.arn
    aws_sns_topic_aft_failure_notifications_arn        = aws_sns_topic.aft_failure_notifications.arn
    aws_sqs_queue_aft_account_request_arn              = aws_sqs_queue.aft_account_request.arn
  })
}


######### invoke_aft_account_provisioning_framework #########

resource "aws_iam_role" "aft_invoke_aft_account_provisioning_framework" {
  name               = "aft-lambda-invoke-aft-account-provisioning-framework"
  assume_role_policy = templatefile("${path.module}/iam/trust-policies/lambda.tpl", { none = "none" })
}

resource "aws_iam_role_policy_attachment" "aft_invoke_aft_account_provisioning_framework" {
  count      = length(local.lambda_managed_policies)
  role       = aws_iam_role.aft_invoke_aft_account_provisioning_framework.name
  policy_arn = local.lambda_managed_policies[count.index]
}

resource "aws_iam_role_policy" "aft_invoke_aft_account_provisioning_framework" {
  name = "aft-invoke-account-provisioning-framework"
  role = aws_iam_role.aft_invoke_aft_account_provisioning_framework.id

  policy = templatefile("${path.module}/iam/role-policies/lambda-invoke-aft-account-provisioning-framework.tpl", {
    data_aws_partition_current_partition               = data.aws_partition.current.partition
    data_aws_region_aft-management_name                = data.aws_region.aft-management.region
    data_aws_caller_identity_aft-management_account_id = data.aws_caller_identity.aft-management.account_id
    aws_sns_topic_aft_notifications_arn                = aws_sns_topic.aft_notifications.arn
    aws_sns_topic_aft_failure_notifications_arn        = aws_sns_topic.aft_failure_notifications.arn
    aws_dynamodb_table_aft-request_name                = aws_dynamodb_table.aft_request.name
    var_aft_account_provisioning_framework_sfn_name    = var.aft_account_provisioning_framework_sfn_name
    aws_kms_key_aft_arn                                = aws_kms_key.aft.arn
  })
}

######### cleanup-aft-resourcess #########
resource "aws_iam_role" "aft_cleanup_resources" {
  name               = "aft-lambda-cleanup-resources"
  assume_role_policy = templatefile("${path.module}/iam/trust-policies/lambda.tpl", { none = "none" })
}

resource "aws_iam_role_policy_attachment" "aft_cleanup_resources" {
  count      = length(local.lambda_managed_policies)
  role       = aws_iam_role.aft_cleanup_resources.name
  policy_arn = local.lambda_managed_policies[count.index]
}

resource "aws_iam_role_policy" "aft_cleanup_resources" {
  name = "aft-cleanup-resources"
  role = aws_iam_role.aft_cleanup_resources.id

  policy = templatefile("${path.module}/iam/role-policies/lambda-aft-cleanup-resources.tpl", {
    data_aws_partition_current_partition               = data.aws_partition.current.partition
    data_aws_region_aft-management_name                = data.aws_region.aft-management.region
    data_aws_caller_identity_aft-management_account_id = data.aws_caller_identity.aft-management.account_id
    aws_sns_topic_aft_notifications_arn                = aws_sns_topic.aft_notifications.arn
    aws_sns_topic_aft_failure_notifications_arn        = aws_sns_topic.aft_failure_notifications.arn
    aws_dynamodb_table_aft-request-metadata_name       = aws_dynamodb_table.aft_request_metadata.name
    aws_kms_key_aft_arn                                = aws_kms_key.aft.arn
  })
}

######### aft_aws_backup #########

resource "aws_iam_role" "aft_aws_backup" {
  name               = "aft-aws-backup"
  assume_role_policy = templatefile("${path.module}/iam/trust-policies/backup.tpl", { none = "none" })
}
resource "aws_iam_role_policy_attachment" "aft_aws_backup_service_role" {
  role       = aws_iam_role.aft_aws_backup.name
  policy_arn = "arn:${data.aws_partition.current.partition}:iam::aws:policy/service-role/AWSBackupServiceRolePolicyForBackup"
}
