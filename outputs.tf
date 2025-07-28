# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
#########################################
# Control Tower Core Account Parameters
#########################################

output "ct_management_account_id" {
  value = var.ct_management_account_id
}

output "log_archive_account_id" {
  value = var.log_archive_account_id
}

output "audit_account_id" {
  value = var.audit_account_id
}

#########################################
# General AFT Vars
#########################################

output "aft_management_account_id" {
  value = var.aft_management_account_id
}

output "ct_home_region" {
  value = var.ct_home_region
}

output "cloudwatch_log_group_retention" {
  value = var.cloudwatch_log_group_retention
}

output "backup_recovery_point_retention" {
  value = var.backup_recovery_point_retention
}

output "maximum_concurrent_customizations" {
  value = var.maximum_concurrent_customizations
}

#########################################
# AFT Feature Flags
#########################################

output "aft_feature_cloudtrail_data_events" {
  value = var.aft_feature_cloudtrail_data_events
}

output "aft_feature_enterprise_support" {
  value = var.aft_feature_enterprise_support
}

output "aft_feature_delete_default_vpcs_enabled" {
  value = var.aft_feature_delete_default_vpcs_enabled
}

#########################################
# AFT Customer VCS Variables
#########################################

output "vcs_provider" {
  value = var.vcs_provider
}

output "github_enterprise_url" {
  value = var.github_enterprise_url
}

output "gitlab_selfmanaged_url" {
  value = var.gitlab_selfmanaged_url
}

output "account_request_repo_name" {
  value = var.account_request_repo_name
}

output "account_request_repo_branch" {
  value = var.account_request_repo_branch
}


output "global_customizations_repo_name" {
  value = var.global_customizations_repo_name
}

output "global_customizations_repo_branch" {
  value = var.global_customizations_repo_branch
}

output "account_customizations_repo_name" {
  value = var.account_customizations_repo_name
}

output "account_customizations_repo_branch" {
  value = var.account_customizations_repo_branch
}

output "account_provisioning_customizations_repo_name" {
  value = var.account_provisioning_customizations_repo_name
}

output "account_provisioning_customizations_repo_branch" {
  value = var.account_provisioning_customizations_repo_branch
}

#########################################
# AFT Terraform Distribution Variables
#########################################

output "terraform_version" {
  value = var.terraform_version
}

output "terraform_distribution" {
  value = var.terraform_distribution
}

output "tf_backend_secondary_region" {
  value = var.tf_backend_secondary_region
}

output "terraform_org_name" {
  value = var.terraform_org_name
}

output "terraform_api_endpoint" {
  value = var.terraform_api_endpoint
}

#########################################
# AFT VPC Variables
#########################################

output "aft_vpc_cidr" {
  value = var.aft_vpc_cidr
}

output "aft_vpc_private_subnet_01_cidr" {
  value = var.aft_vpc_private_subnet_01_cidr
}

output "aft_vpc_private_subnet_02_cidr" {
  value = var.aft_vpc_private_subnet_02_cidr
}

output "aft_vpc_public_subnet_01_cidr" {
  value = var.aft_vpc_public_subnet_01_cidr
}

output "aft_vpc_public_subnet_02_cidr" {
  value = var.aft_vpc_public_subnet_02_cidr
}


#########################################
# AFT S3 Buckets
#########################################

output "aft_primary_backend_bucket_id" {
  value = module.aft_backend.bucket_id
}

output "aft_secondary_backend_bucket_id" {
  value = module.aft_backend.secondary_bucket_id
}

output "aft_access_logs_primary_backend_bucket_id" {
  value = module.aft_backend.access_logs_bucket_id
}


#########################################
# AFT IAM Roles
#########################################

output "aft_admin_role_arn" {
  value = module.aft_iam_roles.aft_admin_role_arn
}

output "aft_ct_management_exec_role_arn" {
  value = module.aft_iam_roles.ct_management_exec_role_arn
}

output "aft_log_archive_exec_role_arn" {
  value = module.aft_iam_roles.log_archive_exec_role_arn
}

output "aft_audit_exec_role_arn" {
  value = module.aft_iam_roles.audit_exec_role_arn
}

output "aft_exec_role_arn" {
  value = module.aft_iam_roles.aft_exec_role_arn
}


#########################################
# AFT DynamoDB Tables
#########################################

output "aft_request_table_name" {
  value = module.aft_account_request_framework.request_table_name
}

output "aft_request_audit_table_name" {
  value = module.aft_account_request_framework.request_audit_table_name
}

output "aft_request_metadata_table_name" {
  value = module.aft_account_request_framework.request_metadata_table_name
}

output "aft_controltower_events_table_name" {
  value = module.aft_account_request_framework.controltower_events_table_name
}

output "aft_backend_lock_table_name" {
  value = module.aft_backend.table_id
}


#########################################
# AFT KMS Keys
#########################################

output "aft_kms_key_id" {
  value = module.aft_account_request_framework.aft_kms_key_id
}

output "aft_kms_key_alias_arn" {
  value = module.aft_account_request_framework.aft_kms_key_alias_arn
}

output "aft_backend_primary_kms_key_id" {
  value = module.aft_backend.kms_key_id
}

output "aft_backend_primary_kms_key_alias_arn" {
  value = module.aft_backend.kms_key_alias_arn
}

output "aft_backend_secondary_kms_key_id" {
  value = module.aft_backend.secondary_kms_key_id
}

output "aft_backend_secondary_kms_key_alias_arn" {
  value = module.aft_backend.secondary_kms_key_alias_arn
}


#########################################
# AFT Step Functions State Machines
#########################################

output "aft_account_provisioning_framework_step_function_arn" {
  value = module.aft_account_provisioning_framework.state_machine_arn
}

output "aft_invoke_customizations_step_function_arn" {
  value = module.aft_customizations.state_machine_arn
}

output "aft_features_step_function_arn" {
  value = module.aft_feature_options.state_machine_arn
}


#########################################
# AFT SNS topics
#########################################

output "aft_sns_topic_arn" {
  value = module.aft_account_request_framework.aft_sns_topic_arn
}

output "aft_failure_sns_topic_arn" {
  value = module.aft_account_request_framework.aft_failure_sns_topic_arn
}
