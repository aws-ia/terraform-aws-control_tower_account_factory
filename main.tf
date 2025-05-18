# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
module "packaging" {
  source = "./modules/aft-archives"
}

module "aft_account_provisioning_framework" {
  providers = {
    aws = aws.aft_management
  }
  source                                           = "./modules/aft-account-provisioning-framework"
  aft_account_provisioning_framework_sfn_name      = local.aft_account_provisioning_framework_sfn_name
  aft_account_provisioning_customizations_sfn_name = local.aft_account_provisioning_customizations_sfn_name
  trigger_customizations_sfn_name                  = local.trigger_customizations_sfn_name
  aft_features_sfn_name                            = local.aft_features_sfn_name
  aft_sns_topic_arn                                = module.aft_account_request_framework.aft_sns_topic_arn
  aft_failure_sns_topic_arn                        = module.aft_account_request_framework.aft_failure_sns_topic_arn
  aft_common_layer_arn                             = module.aft_lambda_layer.layer_version_arn
  aft_kms_key_arn                                  = module.aft_account_request_framework.aft_kms_key_arn
  aft_enable_vpc                                   = module.aft_account_request_framework.vpc_deployment
  aft_vpc_private_subnets                          = module.aft_account_request_framework.aft_vpc_private_subnets
  aft_vpc_default_sg                               = module.aft_account_request_framework.aft_vpc_default_sg
  cloudwatch_log_group_retention                   = var.cloudwatch_log_group_retention
  provisioning_framework_archive_path              = module.packaging.provisioning_framework_archive_path
  provisioning_framework_archive_hash              = module.packaging.provisioning_framework_archive_hash
  create_role_lambda_function_name                 = local.create_role_lambda_function_name
  tag_account_lambda_function_name                 = local.tag_account_lambda_function_name
  persist_metadata_lambda_function_name            = local.persist_metadata_lambda_function_name
  account_metadata_ssm_lambda_function_name        = local.account_metadata_ssm_lambda_function_name
  delete_default_vpc_lambda_function_name          = local.delete_default_vpc_lambda_function_name
  enroll_support_lambda_function_name              = local.enroll_support_lambda_function_name
  enable_cloudtrail_lambda_function_name           = local.enable_cloudtrail_lambda_function_name
  lambda_runtime_python_version                    = local.lambda_runtime_python_version
}

module "aft_account_request_framework" {
  providers = {
    aws               = aws.aft_management
    aws.ct_management = aws.ct_management
  }
  source                                      = "./modules/aft-account-request-framework"
  account_factory_product_name                = local.account_factory_product_name
  aft_account_provisioning_framework_sfn_name = local.aft_account_provisioning_framework_sfn_name
  aft_common_layer_arn                        = module.aft_lambda_layer.layer_version_arn
  cloudwatch_log_group_retention              = var.cloudwatch_log_group_retention
  aft_enable_vpc                              = var.aft_enable_vpc
  aft_vpc_cidr                                = var.aft_vpc_cidr
  aft_vpc_private_subnet_01_cidr              = var.aft_vpc_private_subnet_01_cidr
  aft_vpc_private_subnet_02_cidr              = var.aft_vpc_private_subnet_02_cidr
  aft_vpc_public_subnet_01_cidr               = var.aft_vpc_public_subnet_01_cidr
  aft_vpc_public_subnet_02_cidr               = var.aft_vpc_public_subnet_02_cidr
  aft_vpc_endpoints                           = var.aft_vpc_endpoints
  concurrent_account_factory_actions          = var.concurrent_account_factory_actions
  request_framework_archive_path              = module.packaging.request_framework_archive_path
  request_framework_archive_hash              = module.packaging.request_framework_archive_hash
  lambda_runtime_python_version               = local.lambda_runtime_python_version
  backup_recovery_point_retention             = var.backup_recovery_point_retention
  aft_customer_vpc_id                         = var.aft_customer_vpc_id
  aft_customer_private_subnets                = var.aft_customer_private_subnets
}

module "aft_backend" {
  providers = {
    aws.primary_region   = aws.aft_management
    aws.secondary_region = aws.tf_backend_secondary_region
  }
  source                                                = "./modules/aft-backend"
  primary_region                                        = var.ct_home_region
  secondary_region                                      = var.tf_backend_secondary_region
  aft_management_account_id                             = var.aft_management_account_id
  aft_backend_bucket_access_logs_object_expiration_days = var.aft_backend_bucket_access_logs_object_expiration_days
}

module "aft_code_repositories" {
  providers = {
    aws = aws.aft_management
  }
  source                                          = "./modules/aft-code-repositories"
  vpc_id                                          = module.aft_account_request_framework.aft_vpc_id
  aft_config_backend_bucket_id                    = module.aft_backend.bucket_id
  aft_config_backend_table_id                     = module.aft_backend.table_id
  aft_config_backend_kms_key_id                   = module.aft_backend.kms_key_id
  account_request_table_name                      = module.aft_account_request_framework.request_table_name
  codepipeline_s3_bucket_arn                      = module.aft_customizations.aft_codepipeline_customizations_bucket_arn
  codepipeline_s3_bucket_name                     = module.aft_customizations.aft_codepipeline_customizations_bucket_name
  security_group_ids                              = module.aft_account_request_framework.aft_vpc_default_sg
  subnet_ids                                      = module.aft_account_request_framework.aft_vpc_private_subnets
  aft_key_arn                                     = module.aft_account_request_framework.aft_kms_key_arn
  account_request_repo_branch                     = var.account_request_repo_branch
  account_request_repo_name                       = var.account_request_repo_name
  account_customizations_repo_name                = var.account_customizations_repo_name
  global_customizations_repo_name                 = var.global_customizations_repo_name
  github_enterprise_url                           = var.github_enterprise_url
  gitlab_selfmanaged_url                          = var.gitlab_selfmanaged_url
  vcs_provider                                    = var.vcs_provider
  terraform_distribution                          = var.terraform_distribution
  account_provisioning_customizations_repo_name   = var.account_provisioning_customizations_repo_name
  account_provisioning_customizations_repo_branch = var.account_provisioning_customizations_repo_branch
  account_customizations_repo_branch              = var.account_customizations_repo_branch
  global_customizations_repo_branch               = var.global_customizations_repo_branch
  log_group_retention                             = var.cloudwatch_log_group_retention
  global_codebuild_timeout                        = var.global_codebuild_timeout
  aft_enable_vpc                                  = module.aft_account_request_framework.vpc_deployment
}

module "aft_customizations" {
  providers = {
    aws = aws.aft_management
  }
  source                                            = "./modules/aft-customizations"
  aft_tf_aws_customizations_module_git_ref_ssm_path = local.ssm_paths.aft_tf_aws_customizations_module_git_ref_ssm_path
  aft_tf_aws_customizations_module_url_ssm_path     = local.ssm_paths.aft_tf_aws_customizations_module_url_ssm_path
  aft_tf_backend_region_ssm_path                    = local.ssm_paths.aft_tf_backend_region_ssm_path
  aft_tf_ddb_table_ssm_path                         = local.ssm_paths.aft_tf_ddb_table_ssm_path
  aft_tf_kms_key_id_ssm_path                        = local.ssm_paths.aft_tf_kms_key_id_ssm_path
  aft_tf_s3_bucket_ssm_path                         = local.ssm_paths.aft_tf_s3_bucket_ssm_path
  aft_tf_version_ssm_path                           = local.ssm_paths.aft_tf_version_ssm_path
  aft_kms_key_id                                    = module.aft_account_request_framework.aft_kms_key_id
  aft_kms_key_arn                                   = module.aft_account_request_framework.aft_kms_key_arn
  aft_common_layer_arn                              = module.aft_lambda_layer.layer_version_arn
  aft_sns_topic_arn                                 = module.aft_account_request_framework.sns_topic_arn
  aft_failure_sns_topic_arn                         = module.aft_account_request_framework.failure_sns_topic_arn
  request_metadata_table_name                       = module.aft_account_request_framework.request_metadata_table_name
  aft_vpc_id                                        = module.aft_account_request_framework.aft_vpc_id
  aft_vpc_private_subnets                           = module.aft_account_request_framework.aft_vpc_private_subnets
  aft_vpc_default_sg                                = module.aft_account_request_framework.aft_vpc_default_sg
  aft_config_backend_bucket_id                      = module.aft_backend.bucket_id
  aft_config_backend_table_id                       = module.aft_backend.table_id
  aft_config_backend_kms_key_id                     = module.aft_backend.kms_key_id
  invoke_account_provisioning_sfn_arn               = module.aft_account_provisioning_framework.state_machine_arn
  account_request_table_name                        = module.aft_account_request_framework.request_table_name
  terraform_distribution                            = var.terraform_distribution
  cloudwatch_log_group_retention                    = var.cloudwatch_log_group_retention
  maximum_concurrent_customizations                 = var.maximum_concurrent_customizations
  customizations_archive_path                       = module.packaging.customizations_archive_path
  customizations_archive_hash                       = module.packaging.customizations_archive_hash
  global_codebuild_timeout                          = var.global_codebuild_timeout
  lambda_runtime_python_version                     = local.lambda_runtime_python_version
  aft_enable_vpc                                    = module.aft_account_request_framework.vpc_deployment
}

module "aft_feature_options" {
  providers = {
    aws.ct_management  = aws.ct_management
    aws.audit          = aws.audit
    aws.log_archive    = aws.log_archive
    aws.aft_management = aws.aft_management
  }
  source                                    = "./modules/aft-feature-options"
  log_archive_access_logs_bucket_name       = local.log_archive_access_logs_bucket_name
  log_archive_bucket_name                   = local.log_archive_bucket_name
  log_archive_bucket_object_expiration_days = var.log_archive_bucket_object_expiration_days
  aft_features_sfn_name                     = local.aft_features_sfn_name
  aft_kms_key_arn                           = module.aft_account_request_framework.aft_kms_key_arn
  aft_kms_key_id                            = module.aft_account_request_framework.aft_kms_key_id
  aft_common_layer_arn                      = module.aft_lambda_layer.layer_version_arn
  aft_sns_topic_arn                         = module.aft_account_request_framework.sns_topic_arn
  aft_failure_sns_topic_arn                 = module.aft_account_request_framework.failure_sns_topic_arn
  aft_vpc_private_subnets                   = module.aft_account_request_framework.aft_vpc_private_subnets
  aft_vpc_default_sg                        = module.aft_account_request_framework.aft_vpc_default_sg
  log_archive_account_id                    = var.log_archive_account_id
  cloudwatch_log_group_retention            = var.cloudwatch_log_group_retention
  feature_options_archive_path              = module.packaging.feature_options_archive_path
  feature_options_archive_hash              = module.packaging.feature_options_archive_hash
  delete_default_vpc_lambda_function_name   = local.delete_default_vpc_lambda_function_name
  enroll_support_lambda_function_name       = local.enroll_support_lambda_function_name
  enable_cloudtrail_lambda_function_name    = local.enable_cloudtrail_lambda_function_name
  lambda_runtime_python_version             = local.lambda_runtime_python_version
  aft_enable_vpc                            = module.aft_account_request_framework.vpc_deployment
}

module "aft_iam_roles" {
  source = "./modules/aft-iam-roles"
  providers = {
    aws.ct_management  = aws.ct_management
    aws.audit          = aws.audit
    aws.log_archive    = aws.log_archive
    aws.aft_management = aws.aft_management
  }
}

module "aft_lambda_layer" {
  providers = {
    aws = aws.aft_management
  }
  source                                            = "./modules/aft-lambda-layer"
  aft_version                                       = local.aft_version
  lambda_layer_name                                 = local.lambda_layer_name
  lambda_layer_codebuild_delay                      = local.lambda_layer_codebuild_delay
  lambda_layer_python_version                       = local.lambda_layer_python_version
  lambda_runtime_python_version                     = local.lambda_runtime_python_version
  aft_tf_aws_customizations_module_git_ref_ssm_path = local.ssm_paths.aft_tf_aws_customizations_module_git_ref_ssm_path
  aft_tf_aws_customizations_module_url_ssm_path     = local.ssm_paths.aft_tf_aws_customizations_module_url_ssm_path
  aws_region                                        = var.ct_home_region
  aft_kms_key_arn                                   = module.aft_account_request_framework.aft_kms_key_arn
  aft_vpc_id                                        = module.aft_account_request_framework.aft_vpc_id
  aft_vpc_private_subnets                           = module.aft_account_request_framework.aft_vpc_private_subnets
  aft_vpc_default_sg                                = module.aft_account_request_framework.aft_vpc_default_sg
  s3_bucket_name                                    = module.aft_customizations.aft_codepipeline_customizations_bucket_name
  builder_archive_path                              = module.packaging.builder_archive_path
  builder_archive_hash                              = module.packaging.builder_archive_hash
  cloudwatch_log_group_retention                    = var.cloudwatch_log_group_retention
  aft_enable_vpc                                    = module.aft_account_request_framework.vpc_deployment
}

module "aft_ssm_parameters" {
  providers = {
    aws = aws.aft_management
  }
  source                                                      = "./modules/aft-ssm-parameters"
  aft_request_queue_name                                      = module.aft_account_request_framework.request_queue_name
  aft_request_table_name                                      = module.aft_account_request_framework.request_table_name
  aft_request_audit_table_name                                = module.aft_account_request_framework.request_audit_table_name
  aft_request_metadata_table_name                             = module.aft_account_request_framework.request_metadata_table_name
  aft_controltower_events_table_name                          = module.aft_account_request_framework.controltower_events_table_name
  account_factory_product_name                                = module.aft_account_request_framework.account_factory_product_name
  aft_invoke_aft_account_provisioning_framework_function_name = module.aft_account_request_framework.invoke_aft_account_provisioning_framework_lambda_function_name
  aft_cleanup_resources_function_name                         = module.aft_account_request_framework.aft_cleanup_resources_function_name
  aft_account_provisioning_framework_sfn_name                 = module.aft_account_request_framework.aft_account_provisioning_framework_sfn_name
  aft_sns_topic_arn                                           = module.aft_account_request_framework.sns_topic_arn
  aft_failure_sns_topic_arn                                   = module.aft_account_request_framework.failure_sns_topic_arn
  request_action_trigger_function_arn                         = module.aft_account_request_framework.request_action_trigger_function_arn
  request_audit_trigger_function_arn                          = module.aft_account_request_framework.request_audit_trigger_function_arn
  request_processor_function_arn                              = module.aft_account_request_framework.request_processor_function_arn
  control_tower_event_logger_function_arn                     = module.aft_account_request_framework.control_tower_event_logger_function_arn
  invoke_aft_account_provisioning_framework_function_arn      = module.aft_account_request_framework.invoke_aft_account_provisioning_framework_function_arn
  create_role_function_arn                                    = module.aft_account_provisioning_framework.create_role_function_arn
  tag_account_function_arn                                    = module.aft_account_provisioning_framework.tag_account_function_arn
  persist_metadata_function_arn                               = module.aft_account_provisioning_framework.persist_metadata_function_arn
  aft_customizations_identify_targets_function_arn            = module.aft_customizations.aft_customizations_identify_targets_function_arn
  aft_customizations_execute_pipeline_function_arn            = module.aft_customizations.aft_customizations_execute_pipeline_function_arn
  aft_customizations_get_pipeline_executions_function_arn     = module.aft_customizations.aft_customizations_get_pipeline_executions_function_arn
  codeconnections_connection_arn                              = module.aft_code_repositories.codeconnections_connection_arn
  aft_log_key_arn                                             = module.aft_feature_options.aws_aft_log_key_arn
  aft_logging_bucket_arn                                      = module.aft_feature_options.aws_aft_logs_s3_bucket_arn
  aft_config_backend_bucket_id                                = module.aft_backend.bucket_id
  aft_config_backend_table_id                                 = module.aft_backend.table_id
  aft_config_backend_kms_key_id                               = module.aft_backend.kms_key_id
  aft_administrator_role_name                                 = local.aft_administrator_role_name
  aft_execution_role_name                                     = local.aft_execution_role_name
  aft_session_name                                            = local.aft_session_name
  aft_version                                                 = local.aft_version
  ct_management_account_id                                    = var.ct_management_account_id
  ct_audit_account_id                                         = var.audit_account_id
  ct_log_archive_account_id                                   = var.log_archive_account_id
  aft_management_account_id                                   = var.aft_management_account_id
  ct_primary_region                                           = var.ct_home_region
  tf_version                                                  = var.terraform_version
  tf_distribution                                             = var.terraform_distribution
  terraform_api_endpoint                                      = var.terraform_api_endpoint
  account_request_repo_branch                                 = var.account_request_repo_branch
  account_request_repo_name                                   = var.account_request_repo_name
  vcs_provider                                                = var.vcs_provider
  aft_config_backend_primary_region                           = var.ct_home_region
  aft_config_backend_secondary_region                         = var.tf_backend_secondary_region
  aft_framework_repo_url                                      = var.aft_framework_repo_url
  aft_framework_repo_git_ref                                  = local.aft_framework_repo_git_ref
  terraform_token                                             = var.terraform_token # Null default value #tfsec:ignore:general-secrets-no-plaintext-exposure
  terraform_version                                           = var.terraform_version
  terraform_org_name                                          = var.terraform_org_name
  terraform_project_name                                      = var.terraform_project_name
  aft_feature_cloudtrail_data_events                          = var.aft_feature_cloudtrail_data_events
  aft_feature_enterprise_support                              = var.aft_feature_enterprise_support
  aft_feature_delete_default_vpcs_enabled                     = var.aft_feature_delete_default_vpcs_enabled
  account_customizations_repo_name                            = var.account_customizations_repo_name
  account_customizations_repo_branch                          = var.account_customizations_repo_branch
  global_customizations_repo_name                             = var.global_customizations_repo_name
  global_customizations_repo_branch                           = var.global_customizations_repo_branch
  account_provisioning_customizations_repo_name               = var.account_provisioning_customizations_repo_name
  account_provisioning_customizations_repo_branch             = var.account_provisioning_customizations_repo_branch
  maximum_concurrent_customizations                           = var.maximum_concurrent_customizations
  github_enterprise_url                                       = var.github_enterprise_url
  gitlab_selfmanaged_url                                      = var.gitlab_selfmanaged_url
  aft_metrics_reporting                                       = var.aft_metrics_reporting
}
