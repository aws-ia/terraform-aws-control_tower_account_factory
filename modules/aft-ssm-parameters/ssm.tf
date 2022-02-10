# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#
resource "aws_ssm_parameter" "aft_request_queue_name" {
  name  = "/aft/resources/sqs/aft-request-queue-name"
  type  = "String"
  value = var.aft_request_queue_name
}

resource "aws_ssm_parameter" "aft_request_table_name" {
  name  = "/aft/resources/ddb/aft-request-table-name"
  type  = "String"
  value = var.aft_request_table_name
}

resource "aws_ssm_parameter" "aft_request_audit_table_name" {
  name  = "/aft/resources/ddb/aft-request-audit-table-name"
  type  = "String"
  value = var.aft_request_audit_table_name
}

resource "aws_ssm_parameter" "aft_request_metadata_table_name" {
  name  = "/aft/resources/ddb/aft-request-metadata-table-name"
  type  = "String"
  value = var.aft_request_metadata_table_name
}

resource "aws_ssm_parameter" "aft_controltower_events_table_name" {
  name  = "/aft/resources/ddb/aft-controltower-events-table-name"
  type  = "String"
  value = var.aft_controltower_events_table_name
}

resource "aws_ssm_parameter" "aft_account_factory_product_name" {
  name  = "/aft/resources/sc/account-factory-product-name"
  type  = "String"
  value = var.account_factory_product_name
}

resource "aws_ssm_parameter" "aft_invoke_aft_account_provisioning_framework_lambda_function_name" {
  name  = "/aft/resources/lambda/aft-invoke-aft-account-provisioning-framework"
  type  = "String"
  value = var.aft_invoke_aft_account_provisioning_framework_function_name
}

resource "aws_ssm_parameter" "aft_account_provisioning_framework_sfn_name" {
  name  = "/aft/account/aft-management/sfn/aft-account-provisioning-framework-sfn-name"
  type  = "String"
  value = var.aft_account_provisioning_framework_sfn_name
}

resource "aws_ssm_parameter" "aft_sns_topic_arn" {
  name  = "/aft/account/aft-management/sns/topic-arn"
  type  = "String"
  value = var.aft_sns_topic_arn
}

resource "aws_ssm_parameter" "aft_failure_sns_topic_arn" {
  name  = "/aft/account/aft-management/sns/failure-topic-arn"
  type  = "String"
  value = var.aft_failure_sns_topic_arn
}

resource "aws_ssm_parameter" "aft_request_action_trigger_function_arn" {
  name  = "/aft/resources/lambda/aft-account-request-action-trigger-function-arn"
  type  = "String"
  value = var.request_action_trigger_function_arn
}

resource "aws_ssm_parameter" "request_audit_trigger_function_arn" {
  name  = "/aft/resources/lambda/aft-account-request-audit-trigger-function-arn"
  type  = "String"
  value = var.request_audit_trigger_function_arn
}

resource "aws_ssm_parameter" "request_processor_function_arn" {
  name  = "/aft/resources/lambda/aft-account-request-processor-function-arn"
  type  = "String"
  value = var.request_processor_function_arn
}

resource "aws_ssm_parameter" "control_tower_event_logger_function_arn" {
  name  = "/aft/resources/lambda/aft-controltower-event-logger-function-arn"
  type  = "String"
  value = var.control_tower_event_logger_function_arn
}

resource "aws_ssm_parameter" "invoke_aft_account_provisioning_framework_function_arn" {
  name  = "/aft/resources/lambda/aft-invoke-aft-account-provisioning-framework-function-arn"
  type  = "String"
  value = var.invoke_aft_account_provisioning_framework_function_arn
}

resource "aws_ssm_parameter" "validate_request_function_arn" {
  name  = "/aft/resources/lambda/aft-account-provisioning-framework-validate-request-function-arn"
  type  = "String"
  value = var.validate_request_function_arn
}

resource "aws_ssm_parameter" "get_account_info_function_arn" {
  name  = "/aft/resources/lambda/aft-account-provisioning-framework-get-account-info-function-arn"
  type  = "String"
  value = var.get_account_info_function_arn
}

resource "aws_ssm_parameter" "create_role_function_arn" {
  name  = "/aft/resources/lambda/aft-account-provisioning-framework-create-role-function-arn"
  type  = "String"
  value = var.create_role_function_arn
}

resource "aws_ssm_parameter" "tag_account_function_arn" {
  name  = "/aft/resources/lambda/aft-account-provisioning-framework-tag-account-function-arn"
  type  = "String"
  value = var.tag_account_function_arn
}

resource "aws_ssm_parameter" "persist_metadata_function_arn" {
  name  = "/aft/resources/lambda/aft-account-provisioning-framework-persist-metadata-function-arn"
  type  = "String"
  value = var.persist_metadata_function_arn
}

resource "aws_ssm_parameter" "aft_customizations_identify_targets_function_arn" {
  name  = "/aft/resources/lambda/aft-customizations-identify-targets-function-arn"
  type  = "String"
  value = var.aft_customizations_identify_targets_function_arn
}

resource "aws_ssm_parameter" "aft_customizations_execute_pipeline_function_arn" {
  name  = "/aft/resources/lambda/aft-customizations-execute-pipeline-function-arn"
  type  = "String"
  value = var.aft_customizations_execute_pipeline_function_arn
}

resource "aws_ssm_parameter" "aft_customizations_get_pipeline_executions_function_arn" {
  name  = "/aft/resources/lambda/aft-customizations-get-pipeline-executions-function-arn"
  type  = "String"
  value = var.aft_customizations_get_pipeline_executions_function_arn
}

resource "aws_ssm_parameter" "vcs_provider" {
  name  = "/aft/config/vcs/provider"
  type  = "String"
  value = var.vcs_provider
}

resource "aws_ssm_parameter" "ct_management_account_id" {
  name  = "/aft/account/ct-management/account-id"
  type  = "String"
  value = var.ct_management_account_id
}

resource "aws_ssm_parameter" "ct_log_archive_account_id" {
  name  = "/aft/account/log-archive/account-id"
  type  = "String"
  value = var.ct_log_archive_account_id
}

resource "aws_ssm_parameter" "ct_audit_account_id" {
  name  = "/aft/account/audit/account-id"
  type  = "String"
  value = var.ct_audit_account_id
}

resource "aws_ssm_parameter" "aft_management_account_id" {
  name  = "/aft/account/aft-management/account-id"
  type  = "String"
  value = var.aft_management_account_id
}

resource "aws_ssm_parameter" "ct_primary_region" {
  name  = "/aft/config/ct-management-region"
  type  = "String"
  value = var.ct_primary_region
}

resource "aws_ssm_parameter" "aft_version" {
  name  = "/aft/config/aft/version"
  type  = "String"
  value = var.aft_version
}

resource "aws_ssm_parameter" "tf_version" {
  name  = "/aft/config/terraform/version"
  type  = "String"
  value = var.tf_version
}

resource "aws_ssm_parameter" "tf_distribution" {
  name  = "/aft/config/terraform/distribution"
  type  = "String"
  value = var.tf_distribution
}

resource "aws_ssm_parameter" "terraform_api_endpoint" {
  name  = "/aft/config/terraform/api-endpoint"
  type  = "String"
  value = var.terraform_api_endpoint
}

resource "aws_ssm_parameter" "terraform_token" {
  name  = "/aft/config/terraform/token"
  type  = "SecureString"
  value = var.terraform_token
}

resource "aws_ssm_parameter" "terraform_org_name" {
  name  = "/aft/config/terraform/org-name"
  type  = "String"
  value = var.terraform_org_name
}

resource "aws_ssm_parameter" "aft_execution_role_name" {
  name  = "/aft/resources/iam/aft-execution-role-name"
  type  = "String"
  value = var.aft_execution_role_name
}

resource "aws_ssm_parameter" "aft_administrator_role_name" {
  name  = "/aft/resources/iam/aft-administrator-role-name"
  type  = "String"
  value = var.aft_administrator_role_name
}

resource "aws_ssm_parameter" "aft_session_name" {
  name  = "/aft/resources/iam/aft-session-name"
  type  = "String"
  value = var.aft_session_name
}

resource "aws_ssm_parameter" "aft_config_backend_bucket_id" {
  name  = "/aft/config/oss-backend/bucket-id"
  type  = "String"
  value = var.aft_config_backend_bucket_id
}

resource "aws_ssm_parameter" "aft_config_backend_primary_region" {
  name  = "/aft/config/oss-backend/primary-region"
  type  = "String"
  value = var.aft_config_backend_primary_region
}

resource "aws_ssm_parameter" "aft_config_backend_secondary_region" {
  name  = "/aft/config/oss-backend/secondary-region"
  type  = "String"
  value = var.aft_config_backend_secondary_region
}

resource "aws_ssm_parameter" "aft_config_backend_kms_key_id" {
  name  = "/aft/config/oss-backend/kms-key-id"
  type  = "String"
  value = var.aft_config_backend_kms_key_id
}

resource "aws_ssm_parameter" "aft_config_backend_table_id" {
  name  = "/aft/config/oss-backend/table-id"
  type  = "String"
  value = var.aft_config_backend_table_id
}

resource "aws_ssm_parameter" "aft_framework_repo_url" {
  name  = "/aft/config/aft-pipeline-code-source/repo-url"
  type  = "String"
  value = var.aft_framework_repo_url
}

resource "aws_ssm_parameter" "aft_framework_repo_git_ref" {
  name  = "/aft/config/aft-pipeline-code-source/repo-git-ref"
  type  = "String"
  value = var.aft_framework_repo_git_ref
}

resource "aws_ssm_parameter" "aft_feature_cloudtrail_data_events" {
  name  = "/aft/config/feature/cloudtrail-data-events-enabled"
  type  = "String"
  value = var.aft_feature_cloudtrail_data_events
}

resource "aws_ssm_parameter" "aft_feature_enterprise_support" {
  name  = "/aft/config/feature/enterprise-support-enabled"
  type  = "String"
  value = var.aft_feature_enterprise_support
}

resource "aws_ssm_parameter" "aft_feature_delete_default_vpcs_enabled" {
  name  = "/aft/config/feature/delete-default-vpcs-enabled"
  type  = "String"
  value = var.aft_feature_delete_default_vpcs_enabled
}

resource "aws_ssm_parameter" "account_request_repo_name" {
  name  = "/aft/config/account-request/repo-name"
  type  = "String"
  value = var.account_request_repo_name
}

resource "aws_ssm_parameter" "account_request_repo_branch" {
  name  = "/aft/config/account-request/repo-branch"
  type  = "String"
  value = var.account_request_repo_branch
}

resource "aws_ssm_parameter" "global_customizations_repo_name" {
  name  = "/aft/config/global-customizations/repo-name"
  type  = "String"
  value = var.global_customizations_repo_name
}

resource "aws_ssm_parameter" "global_customizations_repo_branch" {
  name  = "/aft/config/global-customizations/repo-branch"
  type  = "String"
  value = var.global_customizations_repo_branch
}

resource "aws_ssm_parameter" "account_customizations_repo_name" {
  name  = "/aft/config/account-customizations/repo-name"
  type  = "String"
  value = var.account_customizations_repo_name
}

resource "aws_ssm_parameter" "account_customizations_repo_branch" {
  name  = "/aft/config/account-customizations/repo-branch"
  type  = "String"
  value = var.account_customizations_repo_branch
}

resource "aws_ssm_parameter" "account_provisioning_customizations_repo_name" {
  name  = "/aft/config/account-provisioning-customizations/repo-name"
  type  = "String"
  value = var.account_provisioning_customizations_repo_name
}

resource "aws_ssm_parameter" "account_provisioning_customizations_repo_branch" {
  name  = "/aft/config/account-provisioning-customizations/repo-branch"
  type  = "String"
  value = var.account_provisioning_customizations_repo_branch
}

resource "aws_ssm_parameter" "codestar_connection_arn" {
  name  = "/aft/config/vcs/codestar-connection-arn"
  type  = "String"
  value = var.codestar_connection_arn
}

resource "aws_ssm_parameter" "github_enterprise_url" {
  name  = "/aft/config/vcs/github-enterprise-url"
  type  = "String"
  value = var.github_enterprise_url
}

resource "aws_ssm_parameter" "aft_logging_bucket_arn" {
  name  = "/aft/account/log-archive/log_bucket_arn"
  type  = "String"
  value = var.aft_logging_bucket_arn
}

resource "aws_ssm_parameter" "aft_log_key_arn" {
  name  = "/aft/account/log-archive/kms_key_arn"
  type  = "String"
  value = var.aft_log_key_arn
}

resource "aws_ssm_parameter" "aft_maximum_concurrent_customizations" {
  name  = "/aft/config/customizations/maximum_concurrent_customizations"
  value = var.maximum_concurrent_customizations
  type  = "String"
}
