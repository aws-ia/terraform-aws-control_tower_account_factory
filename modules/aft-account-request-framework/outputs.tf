# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
output "sns_topic_arn" {
  description = "arn of aft notifications sns topic"
  value       = aws_sns_topic.aft_notifications.arn
}

output "failure_sns_topic_arn" {
  description = "arn of failure_notifications sns topic"
  value       = aws_sns_topic.aft_failure_notifications.arn
}

output "aft_kms_key_arn" {
  description = "Arn for the AFT CMK Key"
  value       = aws_kms_key.aft.arn
}

output "aft_kms_key_id" {
  description = "ID for the AFT CMK Key"
  value       = aws_kms_key.aft.id
}

output "request_action_trigger_function_arn" {
  value = aws_lambda_function.aft_account_request_action_trigger.arn
}

output "request_audit_trigger_function_arn" {
  value = aws_lambda_function.aft_account_request_audit_trigger.arn
}

output "request_processor_function_arn" {
  value = aws_lambda_function.aft_account_request_processor.arn
}

output "control_tower_event_logger_function_arn" {
  value = aws_lambda_function.aft_controltower_event_logger.arn
}

output "invoke_aft_account_provisioning_framework_function_arn" {
  value = aws_lambda_function.aft_invoke_aft_account_provisioning_framework.arn
}

output "request_queue_name" {
  value = aws_sqs_queue.aft_account_request.name
}
output "request_table_name" {
  value = aws_dynamodb_table.aft_request.name
}
output "request_audit_table_name" {
  value = aws_dynamodb_table.aft_request_audit.name
}
output "request_metadata_table_name" {
  value = aws_dynamodb_table.aft_request_metadata.name
}
output "controltower_events_table_name" {
  value = aws_dynamodb_table.aft_controltower_events.name
}
output "account_factory_product_name" {
  value = var.account_factory_product_name
}
output "invoke_aft_account_provisioning_framework_lambda_function_name" {
  value = aws_lambda_function.aft_invoke_aft_account_provisioning_framework.function_name
}
output "aft_cleanup_resources_function_name" {
  value = aws_lambda_function.aft_cleanup_resources.function_name
}
output "aft_account_provisioning_framework_sfn_name" {
  value = var.aft_account_provisioning_framework_sfn_name
}
output "aft_sns_topic_arn" {
  value = aws_sns_topic.aft_notifications.arn
}
output "aft_failure_sns_topic_arn" {
  value = aws_sns_topic.aft_failure_notifications.arn
}

#########################################
# VPC Outputs
#########################################

output "aft_vpc_id" {
  value = aws_vpc.aft_vpc.id
}

output "aft_vpc_public_subnets" {
  value = tolist([aws_subnet.aft_vpc_public_subnet_01.id, aws_subnet.aft_vpc_public_subnet_02.id])
}

output "aft_vpc_private_subnets" {
  value = tolist([aws_subnet.aft_vpc_private_subnet_01.id, aws_subnet.aft_vpc_private_subnet_02.id])
}

output "aft_vpc_default_sg" {
  value = tolist([aws_security_group.aft_vpc_default_sg.id])
}
