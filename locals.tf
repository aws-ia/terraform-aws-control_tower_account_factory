# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
locals {
  aft_version                                      = chomp(trimspace(data.local_file.version.content))
  aft_framework_repo_git_ref                       = var.aft_framework_repo_git_ref == null || var.aft_framework_repo_git_ref == "" ? local.aft_version : var.aft_framework_repo_git_ref
  aft_account_provisioning_customizations_sfn_name = "aft-account-provisioning-customizations"
  aft_account_provisioning_framework_sfn_name      = "aft-account-provisioning-framework"
  trigger_customizations_sfn_name                  = "aft-invoke-customizations"
  aft_features_sfn_name                            = "aft-feature-options"
  aft_execution_role_name                          = "AWSAFTExecution"
  aft_administrator_role_name                      = "AWSAFTAdmin"
  aft_session_name                                 = "AWSAFT-Session"
  account_factory_product_name                     = "AWS Control Tower Account Factory"
  log_archive_bucket_name                          = "aws-aft-logs"
  log_archive_access_logs_bucket_name              = "aws-aft-s3-access-logs"
  lambda_layer_codebuild_delay                     = "420s"
  lambda_layer_python_version                      = chomp(trimspace(data.local_file.python_version.content))
  lambda_runtime_python_version                    = format("%s%s", "python", chomp(trimspace(data.local_file.python_version.content)))
  lambda_layer_name                                = "aft-common"
  create_role_lambda_function_name                 = "aft-account-provisioning-framework-create-aft-execution-role"
  tag_account_lambda_function_name                 = "aft-account-provisioning-framework-tag-account"
  persist_metadata_lambda_function_name            = "aft-account-provisioning-framework-persist-metadata"
  account_metadata_ssm_lambda_function_name        = "aft-account-provisioning-framework-account-metadata-ssm"
  delete_default_vpc_lambda_function_name          = "aft-delete-default-vpc"
  enroll_support_lambda_function_name              = "aft-enroll-support"
  enable_cloudtrail_lambda_function_name           = "aft-enable-cloudtrail"
  ssm_paths = {
    aft_tf_aws_customizations_module_url_ssm_path     = "/aft/config/aft-pipeline-code-source/repo-url"
    aft_tf_aws_customizations_module_git_ref_ssm_path = "/aft/config/aft-pipeline-code-source/repo-git-ref"
    aft_tf_s3_bucket_ssm_path                         = "/aft/config/oss-backend/bucket-id"
    aft_tf_backend_region_ssm_path                    = "/aft/config/oss-backend/primary-region"
    aft_tf_kms_key_id_ssm_path                        = "/aft/config/oss-backend/kms-key-id"
    aft_tf_ddb_table_ssm_path                         = "/aft/config/oss-backend/table-id"
    aft_tf_version_ssm_path                           = "/aft/config/terraform/version"
  }
  service_catalog_regional_availability = [
    "ca-central-1",
    "cn-north-1",
    "cn-northwest-1",
    "eu-north-1",
    "eu-west-2",
    "eu-west-3",
    "us-east-1",
    "us-east-2",
    "us-gov-west-1",
    "us-west-2",
    "af-south-1",
    "ap-east-1",
    "ap-south-2",
    "ap-southeast-2",
    "ap-southeast-3",
    "ap-southeast-4",
    "me-central-1",
    "me-south-1",
    "sa-east-1",
    "us-gov-east-1",
    "ap-northeast-2",
    "ap-northeast-3",
    "ap-south-1",
    "ap-southeast-1",
    "eu-central-1",
    "eu-south-1",
    "eu-south-2",
    "eu-west-1",
    "il-central-1",
    "us-west-1",
    "ap-northeast-1",
    "eu-central-2"
  ]
}
