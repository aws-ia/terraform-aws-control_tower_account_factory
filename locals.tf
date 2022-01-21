locals {
  aft_version                                      = chomp(trimspace(data.local_file.version.content))
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
  log_archive_bucket_object_expiration_days        = "365"
  lambda_layer_codebuild_delay                     = "420s"
  lambda_layer_python_version                      = "3.8"
  lambda_layer_name                                = "aft-common"
  ssm_paths = {
    aft_tf_aws_customizations_module_url_ssm_path     = "/aft/config/aft-pipeline-code-source/repo-url"
    aft_tf_aws_customizations_module_git_ref_ssm_path = "/aft/config/aft-pipeline-code-source/repo-git-ref"
    aft_tf_s3_bucket_ssm_path                         = "/aft/config/oss-backend/bucket-id"
    aft_tf_backend_region_ssm_path                    = "/aft/config/oss-backend/primary-region"
    aft_tf_kms_key_id_ssm_path                        = "/aft/config/oss-backend/kms-key-id"
    aft_tf_ddb_table_ssm_path                         = "/aft/config/oss-backend/table-id"
    aft_tf_version_ssm_path                           = "/aft/config/terraform/version"
  }
}
