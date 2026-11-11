# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
variable "aft_request_queue_name" {
  type = string
}

variable "aft_request_table_name" {
  type = string
}

variable "aft_request_audit_table_name" {
  type = string
}

variable "aft_request_metadata_table_name" {
  type = string
}

variable "aft_controltower_events_table_name" {
  type = string
}

variable "account_factory_product_name" {
  type = string
}

variable "aft_invoke_aft_account_provisioning_framework_function_name" {
  type = string
}

variable "aft_cleanup_resources_function_name" {
  type = string
}

variable "aft_organizations_account_provisioning_sfn_name" {
  description = "Name of the Step Function that creates and updates accounts for the Organizations vending method."
  type        = string
}

variable "aft_account_provisioning_framework_sfn_name" {
  type = string
}

variable "aft_sns_topic_arn" {
  type = string
}

variable "aft_failure_sns_topic_arn" {
  type = string
}

variable "request_action_trigger_function_arn" {
  type = string
}

variable "request_audit_trigger_function_arn" {
  type = string
}

variable "request_processor_function_arn" {
  type = string
}

variable "control_tower_event_logger_function_arn" {
  type = string
}

variable "invoke_aft_account_provisioning_framework_function_arn" {
  type = string
}

variable "create_role_function_arn" {
  type = string
}

variable "tag_account_function_arn" {
  type = string
}

variable "persist_metadata_function_arn" {
  type = string
}

variable "aft_customizations_identify_targets_function_arn" {
  type = string
}

variable "aft_customizations_execute_pipeline_function_arn" {
  type = string
}

variable "aft_customizations_get_pipeline_executions_function_arn" {
  type = string
}

variable "vcs_provider" {
  type = string
}

variable "ct_management_account_id" {
  type = string
}

variable "ct_log_archive_account_id" {
  type = string
}

variable "ct_audit_account_id" {
  type = string
}

variable "aft_management_account_id" {
  type = string
}

variable "ct_primary_region" {
  type = string
}

variable "tf_version" {
  type = string
}

variable "tf_distribution" {
  type = string
}

variable "terraform_api_endpoint" {
  type = string
}

variable "terraform_token" {
  type      = string
  sensitive = true
}

variable "terraform_oidc_integration" {
  type = string
}

variable "terraform_oidc_aws_audience" {
  type = string
}

variable "account_request_repo_name" {
  type = string
}

variable "account_request_repo_branch" {
  type = string
}

variable "account_provisioning_customizations_repo_name" {
  type = string
}

variable "account_provisioning_customizations_repo_branch" {
  type = string
}

variable "terraform_org_name" {
  type = string
}

variable "terraform_project_name" {
  type = string
}

variable "account_request_workspace_name" {
  type = string
}

variable "account_provisioning_customizations_workspace_name" {
  type = string
}

variable "aft_execution_role_name" {
  type = string
}

variable "aft_administrator_role_name" {
  type = string
}

variable "aft_session_name" {
  type = string
}

variable "aft_config_backend_bucket_id" {
  type = string
}

variable "aft_config_backend_primary_region" {
  type = string
}

variable "aft_config_backend_secondary_region" {
  type = string
}

variable "aft_config_backend_kms_key_id" {
  type = string
}

variable "aft_config_backend_table_id" {
  type = string
}

variable "aft_framework_repo_url" {
  type = string
}

variable "aft_framework_repo_git_ref" {
  type = string
}

variable "terraform_version" {
  type = string
}

variable "aft_feature_cloudtrail_data_events" {
  type = string
}

variable "aft_feature_enterprise_support" {
  type = string
}

variable "aft_feature_delete_default_vpcs_enabled" {
  type = string
}

variable "aft_customization_triggers" {
  type = string
}

variable "global_customizations_repo_name" {
  type = string
}

variable "global_customizations_repo_branch" {
  type = string
}

variable "account_customizations_repo_name" {
  type = string
}

variable "account_customizations_repo_branch" {
  type = string
}

variable "codeconnections_connection_arn" {
  type = string
}

variable "github_enterprise_url" {
  type = string
}
variable "gitlab_selfmanaged_url" {
  type = string
}
variable "aft_logging_bucket_arn" {
  type = string
}

variable "aft_log_key_arn" {
  type = string
}

variable "maximum_concurrent_customizations" {
  type = number
}

variable "aft_version" {
  type = string
}

variable "aft_metrics_reporting" {
  type = string
}

variable "account_vending_method" {
  description = "Method AFT uses to vend accounts (service_catalog or organizations). Written to SSM /aft/config/account-vending-method."
  type        = string
  default     = "service_catalog"
}

variable "aft_feature_governance_validation" {
  description = "Organizations vending method only. Turns governance validation on or off. Written to SSM /aft/config/feature/governance-validation-enabled."
  type        = bool
  default     = true
}

variable "governance_validation_mode" {
  description = "Organizations vending method only. Governance validation outcome (warn or fail). Written to SSM /aft/config/governance-validation-mode."
  type        = string
  default     = "warn"
}

variable "aft_feature_delete_vended_account_default_vpcs_enabled" {
  description = "Organizations vending method only. When true, the default VPCs of each account AFT creates are deleted in the governed Regions. Written to SSM /aft/config/feature/delete-vended-account-default-vpcs-enabled."
  type        = bool
  default     = false
}

variable "aft_codepipeline_customizations_bucket_id" {
  type = string
}


variable "aft_customizations_audit_table_name" {
  type = string
}

variable "aft_plan_output_bucket_name" {
  type = string
}

variable "aft_plan_output_export_enabled" {
  type = bool
}

variable "aft_from_ct_management_event_bus_name" {
  description = "Name of the AFT event bus that receives Control Tower / aft.organizations lifecycle events."
  type        = string
}
