# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
###################################################################
# CodePipeline IAM Resources
###################################################################

resource "aws_iam_role" "aft_codepipeline_customizations_role" {
  name               = "aft-codepipeline-customizations-role"
  assume_role_policy = templatefile("${path.module}/iam/trust-policies/codepipeline.tpl", { none = "none" })
}

resource "aws_iam_role_policy" "aft_codepipeline_customizations_policy" {
  name = "aft-codepipeline-customizations-policy"
  role = aws_iam_role.aft_codepipeline_customizations_role.id

  policy = templatefile("${path.module}/iam/role-policies/aft_codepipeline_customizations_policy.tpl", {
    aws_s3_bucket_aft_codepipeline_customizations_bucket_arn = aws_s3_bucket.aft_codepipeline_customizations_bucket.arn
    data_aws_region_current_name                             = data.aws_region.current.name
    data_aws_caller_identity_current_account_id              = data.aws_caller_identity.current.account_id
    data_aws_kms_alias_aft_key_target_key_arn                = var.aft_kms_key_arn
  })
}
###################################################################
# CodeBuild IAM Resources
###################################################################

resource "aws_iam_role" "aft_codebuild_customizations_role" {
  name               = "aft-codebuild-customizations-role"
  assume_role_policy = templatefile("${path.module}/iam/trust-policies/codebuild.tpl", { none = "none" })
}

resource "aws_iam_role_policy" "aft_codebuild_customizations_policy" {
  role = aws_iam_role.aft_codebuild_customizations_role.name

  policy = templatefile("${path.module}/iam/role-policies/aft_codebuild_customizations_policy.tpl", {
    aws_s3_bucket_aft_codepipeline_customizations_bucket_arn = aws_s3_bucket.aft_codepipeline_customizations_bucket.arn
    data_aws_region_current_name                             = data.aws_region.current.name
    data_aws_caller_identity_current_account_id              = data.aws_caller_identity.current.account_id
    data_aws_kms_alias_aft_key_target_key_arn                = var.aft_kms_key_arn
    data_aws_dynamo_account_metadata_table                   = var.request_metadata_table_name
  })
}

###################################################################
# Step Functions - Invoke Customizations
###################################################################

resource "aws_iam_role" "aft_invoke_customizations_sfn" {
  name               = "aft-invoke-customizations-execution-role"
  assume_role_policy = templatefile("${path.module}/iam/trust-policies/states.tpl", { none = "none" })
}

resource "aws_iam_role_policy" "aft_invoke_customizations_sfn" {
  name = "aft-invoke-customizations-policy"
  role = aws_iam_role.aft_invoke_customizations_sfn.id

  policy = templatefile("${path.module}/iam/role-policies/aft_states_invoke_customizations_policy.tpl", {
    data_aws_region_aft-management_name                = data.aws_region.aft_management.name
    data_aws_caller_identity_aft-management_account_id = data.aws_caller_identity.aft_management.account_id
  })

}

###################################################################
# Lambda - Identify Targets
###################################################################

resource "aws_iam_role" "aft_customizations_identify_targets_lambda" {
  name               = "aft-identify-targets-execution-role"
  assume_role_policy = templatefile("${path.module}/iam/trust-policies/lambda.tpl", { none = "none" })
}

resource "aws_iam_role_policy" "aft_identify_targets_lambda" {
  name = "aft-identify-targets-policy"
  role = aws_iam_role.aft_customizations_identify_targets_lambda.id

  policy = templatefile("${path.module}/iam/role-policies/aft_identify_targets_lambda.tpl", {
    data_aws_caller_identity_current_account_id = data.aws_caller_identity.current.account_id
    data_aws_region_current_name                = data.aws_region.current.name
    request_metadata_table_name                 = var.request_metadata_table_name
    aws_kms_key_aft_arn                         = var.aft_kms_key_arn
    aft_sns_topic_arn                           = var.aft_sns_topic_arn
    aft_failure_sns_topic_arn                   = var.aft_failure_sns_topic_arn
  })

}

resource "aws_iam_role_policy_attachment" "aft_identify_targets_lambda" {
  count      = length(local.lambda_managed_policies)
  role       = aws_iam_role.aft_customizations_identify_targets_lambda.name
  policy_arn = local.lambda_managed_policies[count.index]
}

###################################################################
# Lambda - Execute Pipeline
###################################################################

resource "aws_iam_role" "aft_customizations_execute_pipeline_lambda" {
  name               = "aft-execute-pipeline-execution-role"
  assume_role_policy = templatefile("${path.module}/iam/trust-policies/lambda.tpl", { none = "none" })
}

resource "aws_iam_role_policy" "aft_execute_pipeline_lambda" {
  name = "aft-execute-pipeline-policy"
  role = aws_iam_role.aft_customizations_execute_pipeline_lambda.id

  policy = templatefile("${path.module}/iam/role-policies/aft_execute_pipeline_lambda.tpl", {
    data_aws_region_current_name                = data.aws_region.current.name
    data_aws_caller_identity_current_account_id = data.aws_caller_identity.current.account_id
    aws_kms_key_aft_arn                         = var.aft_kms_key_arn
    aft_sns_topic_arn                           = var.aft_sns_topic_arn
    aft_failure_sns_topic_arn                   = var.aft_failure_sns_topic_arn
  })

}

resource "aws_iam_role_policy_attachment" "aft_execute_pipeline_lambda" {
  count      = length(local.lambda_managed_policies)
  role       = aws_iam_role.aft_customizations_execute_pipeline_lambda.name
  policy_arn = local.lambda_managed_policies[count.index]
}

###################################################################
# Lambda - Get Pipeline Executions
###################################################################

resource "aws_iam_role" "aft_customizations_get_pipeline_executions_lambda" {
  name               = "aft-get-pipeline-status-execution-role"
  assume_role_policy = templatefile("${path.module}/iam/trust-policies/lambda.tpl", { none = "none" })
}

resource "aws_iam_role_policy" "aft_get_pipeline_executions_lambda" {
  name = "aft-get-pipeline-status-policy"
  role = aws_iam_role.aft_customizations_get_pipeline_executions_lambda.id

  policy = templatefile("${path.module}/iam/role-policies/aft_get_pipeline_status_lambda.tpl", {
    data_aws_region_current_name                = data.aws_region.current.name
    data_aws_caller_identity_current_account_id = data.aws_caller_identity.current.account_id
    aws_kms_key_aft_arn                         = var.aft_kms_key_arn
    aft_sns_topic_arn                           = var.aft_sns_topic_arn
    aft_failure_sns_topic_arn                   = var.aft_failure_sns_topic_arn
  })

}

resource "aws_iam_role_policy_attachment" "aft_get_pipeline_executions_lambda" {
  count      = length(local.lambda_managed_policies)
  role       = aws_iam_role.aft_customizations_get_pipeline_executions_lambda.name
  policy_arn = local.lambda_managed_policies[count.index]
}

resource "aws_iam_role_policy" "terraform_oss_backend_codebuild_customizations_policy" {
  count = var.terraform_distribution == "oss" ? 1 : 0
  name  = "ct-aft-codebuild-customizations-terraform-oss-backend-policy"
  role  = aws_iam_role.aft_codebuild_customizations_role.id

  policy = templatefile("${path.module}/iam/role-policies/ct_aft_codebuild_oss_backend_policy.tpl", {
    data_aws_region_current_name                      = data.aws_region.current.name
    data_aws_caller_identity_current_account_id       = data.aws_caller_identity.current.account_id
    data_aws_dynamo_terraform_oss_backend_table       = var.aft_config_backend_table_id
    aws_s3_bucket_aft_terraform_oss_backend_bucket_id = var.aft_config_backend_bucket_id
    aws_s3_bucket_aft_terraform_oss_kms_key_id        = var.aft_config_backend_kms_key_id
  })
}

###################################################################
# Lambda - Invoke Account Provisioning
###################################################################

resource "aws_iam_role" "aft_customizations_invoke_account_provisioning_lambda" {
  name               = "aft-customizations-invoke-account-provisioning-role"
  assume_role_policy = templatefile("${path.module}/iam/trust-policies/lambda.tpl", { none = "none" })
}

resource "aws_iam_role_policy" "aft_customizations_invoke_account_provisioning_lambda" {
  name = "aft-customizations-invoke-account-provisioning-policy"
  role = aws_iam_role.aft_customizations_invoke_account_provisioning_lambda.id

  policy = templatefile("${path.module}/iam/role-policies/aft_customizations_invoke_account_provisioning.tpl", {
    data_aws_region_current_name                = data.aws_region.current.name
    data_aws_caller_identity_current_account_id = data.aws_caller_identity.current.account_id
    data_aws_kms_alias_aft_key_target_key_arn   = var.aft_kms_key_arn
    data_aws_dynamo_account_metadata_table      = var.request_metadata_table_name
    data_aws_dynamo_account_request_table       = var.account_request_table_name
    invoke_account_provisioning_arn             = var.invoke_account_provisioning_sfn_arn
    aft_sns_topic_arn                           = var.aft_sns_topic_arn
    aft_failure_sns_topic_arn                   = var.aft_failure_sns_topic_arn
  })

}

resource "aws_iam_role_policy_attachment" "aft_customizations_invoke_account_provisioning_lambda" {
  count      = length(local.lambda_managed_policies)
  role       = aws_iam_role.aft_customizations_invoke_account_provisioning_lambda.name
  policy_arn = local.lambda_managed_policies[count.index]
}
