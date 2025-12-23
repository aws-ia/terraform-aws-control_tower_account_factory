# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
resource "aws_codepipeline" "aft_codecommit_customizations_codepipeline" {
  count         = local.vcs.is_codecommit ? 1 : 0
  name          = "${var.account_id}-customizations-pipeline"
  role_arn      = data.aws_iam_role.aft_codepipeline_customizations_role.arn
  pipeline_type = "V2"

  artifact_store {
    location = data.aws_s3_bucket.aft_codepipeline_customizations_bucket.id
    type     = "S3"

    encryption_key {
      id   = data.aws_kms_alias.aft_key.arn
      type = "KMS"
    }
  }

  ##############################################################
  # Source
  ##############################################################
  stage {
    name = "Source"

    action {
      name             = "aft-global-customizations"
      category         = "Source"
      owner            = "AWS"
      provider         = "CodeCommit"
      version          = "1"
      output_artifacts = ["source-aft-global-customizations"]

      configuration = {
        RepositoryName       = data.aws_ssm_parameter.aft_global_customizations_repo_name.value
        BranchName           = data.aws_ssm_parameter.aft_global_customizations_repo_branch.value
        PollForSourceChanges = false
      }
    }

    action {
      name             = "aft-account-customizations"
      category         = "Source"
      owner            = "AWS"
      provider         = "CodeCommit"
      version          = "1"
      output_artifacts = ["source-aft-account-customizations"]

      configuration = {
        RepositoryName       = data.aws_ssm_parameter.aft_account_customizations_repo_name.value
        BranchName           = data.aws_ssm_parameter.aft_account_customizations_repo_branch.value
        PollForSourceChanges = false
      }
    }
  }

  ##############################################################
  # Workflow "apply"
  ##############################################################

  ##############################################################
  # Apply-AFT-Global-Customizations
  ##############################################################

  dynamic "stage" {
    for_each = local.workflow_type == "apply" ? [1] : []
    content {
      name = "Global-Customizations"
      action {
        name            = "Apply"
        category        = "Build"
        owner           = "AWS"
        provider        = "CodeBuild"
        input_artifacts = ["source-aft-global-customizations"]
        version         = "1"
        run_order       = "2"
        configuration = {
          ProjectName = var.aft_global_customizations_terraform_codebuild_name
          EnvironmentVariables = jsonencode([
            {
              name  = "VENDED_ACCOUNT_ID",
              value = var.account_id,
              type  = "PLAINTEXT"
            },
            {
              name  = "ACTION",
              value = "apply",
              type  = "PLAINTEXT"
            }
          ])
        }
      }
    }
  }
  ##############################################################
  # Apply-AFT-Account-Customizations
  ##############################################################
  dynamic "stage" {
    for_each = local.workflow_type == "apply" ? [1] : []
    content {
      name = "Account-Customizations"

      action {
        name            = "Apply"
        category        = "Build"
        owner           = "AWS"
        provider        = "CodeBuild"
        input_artifacts = ["source-aft-account-customizations"]
        version         = "1"
        run_order       = "2"
        configuration = {
          ProjectName = var.aft_account_customizations_terraform_codebuild_name
          EnvironmentVariables = jsonencode([
            {
              name  = "VENDED_ACCOUNT_ID",
              value = var.account_id,
              type  = "PLAINTEXT"
            },
            {
              name  = "ACTION",
              value = "apply",
              type  = "PLAINTEXT"
            }
          ])
        }
      }
    }
  }

  ##############################################################
  # Workflow "apply-with-approval"
  ##############################################################

  ##############################################################
  # Apply-AFT-Global-Customizations
  ##############################################################
  dynamic "stage" {
    for_each = local.workflow_type == "apply-with-approval" ? [1] : []
    content {
      name = "Global-Customizations-1"
      action {
        name            = "Plan"
        category        = "Build"
        owner           = "AWS"
        provider        = "CodeBuild"
        input_artifacts = ["source-aft-global-customizations"]
        version         = "1"
        run_order       = "2"
        configuration = {
          ProjectName = var.aft_global_customizations_terraform_codebuild_name
          EnvironmentVariables = jsonencode([
            {
              name  = "VENDED_ACCOUNT_ID",
              value = var.account_id,
              type  = "PLAINTEXT"
            },
            {
              name  = "ACTION",
              value = "plan",
              type  = "PLAINTEXT"
            }
          ])
        }
      }
    }
  }

  dynamic "stage" {
    for_each = local.workflow_type == "apply-with-approval" ? [1] : []
    content {
      name = "Global-Customizations-2"
      action {
        name            = "Approval"
        category        = "Approval"
        owner           = "AWS"
        provider        = "Manual"
        input_artifacts = []
        version         = "1"
        run_order       = "3"
      }
    }
  }

  dynamic "stage" {
    for_each = local.workflow_type == "apply-with-approval" ? [1] : []
    content {
      name = "Global-Customizations-3"
      action {
        name            = "Apply"
        category        = "Build"
        owner           = "AWS"
        provider        = "CodeBuild"
        input_artifacts = ["source-aft-global-customizations"]
        version         = "1"
        run_order       = "4"
        configuration = {
          ProjectName = var.aft_global_customizations_terraform_codebuild_name
          EnvironmentVariables = jsonencode([
            {
              name  = "VENDED_ACCOUNT_ID",
              value = var.account_id,
              type  = "PLAINTEXT"
            },
            {
              name  = "ACTION",
              value = "apply",
              type  = "PLAINTEXT"
            }
          ])
        }
      }
    }
  }

  ##############################################################
  # Apply-AFT-Account-Customizations
  ##############################################################
  dynamic "stage" {
    for_each = local.workflow_type == "apply-with-approval" ? [1] : []
    content {
      name = "Account-Customizations-1"

      action {
        name            = "Plan"
        category        = "Build"
        owner           = "AWS"
        provider        = "CodeBuild"
        input_artifacts = ["source-aft-account-customizations"]
        version         = "1"
        run_order       = "5"
        configuration = {
          ProjectName = var.aft_account_customizations_terraform_codebuild_name
          EnvironmentVariables = jsonencode([
            {
              name  = "VENDED_ACCOUNT_ID",
              value = var.account_id,
              type  = "PLAINTEXT"
            },
            {
              name  = "ACTION",
              value = "plan",
              type  = "PLAINTEXT"
            }
          ])
        }
      }
    }
  }

  dynamic "stage" {
    for_each = local.workflow_type == "apply-with-approval" ? [1] : []
    content {
      name = "Account-Customizations-2"

      action {
        name            = "Approval"
        category        = "Approval"
        owner           = "AWS"
        provider        = "Manual"
        input_artifacts = []
        version         = "1"
        run_order       = "6"
      }
    }

  }

  dynamic "stage" {
    for_each = local.workflow_type == "apply-with-approval" ? [1] : []
    content {
      name = "Account-Customizations-3"

      action {
        name            = "Apply"
        category        = "Build"
        owner           = "AWS"
        provider        = "CodeBuild"
        input_artifacts = ["source-aft-account-customizations"]
        version         = "1"
        run_order       = "7"
        configuration = {
          ProjectName = var.aft_account_customizations_terraform_codebuild_name
          EnvironmentVariables = jsonencode([
            {
              name  = "VENDED_ACCOUNT_ID",
              value = var.account_id,
              type  = "PLAINTEXT"
            },
            {
              name  = "ACTION",
              value = "apply",
              type  = "PLAINTEXT"
            }
          ])
        }
      }
    }
  }
}

moved {
  from = aws_codepipeline.aft_codestar_customizations_codepipeline
  to   = aws_codepipeline.aft_codeconnections_customizations_codepipeline
}
resource "aws_codepipeline" "aft_codeconnections_customizations_codepipeline" {
  count         = local.vcs.is_codecommit ? 0 : 1
  name          = "${var.account_id}-customizations-pipeline"
  role_arn      = data.aws_iam_role.aft_codepipeline_customizations_role.arn
  pipeline_type = "V2"

  artifact_store {
    location = data.aws_s3_bucket.aft_codepipeline_customizations_bucket.id
    type     = "S3"

    encryption_key {
      id   = data.aws_kms_alias.aft_key.arn
      type = "KMS"
    }
  }

  ##############################################################
  # Source
  ##############################################################
  stage {
    name = "Source"

    action {
      name             = "aft-global-customizations"
      category         = "Source"
      owner            = "AWS"
      provider         = "CodeStarSourceConnection"
      version          = "1"
      output_artifacts = ["source-aft-global-customizations"]

      configuration = {
        ConnectionArn        = data.aws_ssm_parameter.codeconnections_connection_arn.value
        FullRepositoryId     = data.aws_ssm_parameter.aft_global_customizations_repo_name.value
        BranchName           = data.aws_ssm_parameter.aft_global_customizations_repo_branch.value
        DetectChanges        = false
        OutputArtifactFormat = "CODE_ZIP"
      }
    }

    action {
      name             = "aft-account-customizations"
      category         = "Source"
      owner            = "AWS"
      provider         = "CodeStarSourceConnection"
      version          = "1"
      output_artifacts = ["source-aft-account-customizations"]

      configuration = {
        ConnectionArn        = data.aws_ssm_parameter.codeconnections_connection_arn.value
        FullRepositoryId     = data.aws_ssm_parameter.aft_account_customizations_repo_name.value
        BranchName           = data.aws_ssm_parameter.aft_account_customizations_repo_branch.value
        DetectChanges        = false
        OutputArtifactFormat = "CODE_ZIP"
      }
    }
  }

  ##############################################################
  # Apply-AFT-Global-Customizations
  ##############################################################

  stage {
    name = "AFT-Global-Customizations"

    action {
      name            = "Apply"
      category        = "Build"
      owner           = "AWS"
      provider        = "CodeBuild"
      input_artifacts = ["source-aft-global-customizations"]
      version         = "1"
      run_order       = "2"
      configuration = {
        ProjectName = var.aft_global_customizations_terraform_codebuild_name
        EnvironmentVariables = jsonencode([
          {
            name  = "VENDED_ACCOUNT_ID",
            value = var.account_id,
            type  = "PLAINTEXT"
          }
        ])
      }
    }

  }
  ##############################################################
  # Apply-AFT-Account-Customizations
  ##############################################################

  stage {
    name = "AFT-Account-Customizations"
    action {
      name            = "Apply"
      category        = "Build"
      owner           = "AWS"
      provider        = "CodeBuild"
      input_artifacts = ["source-aft-account-customizations"]
      version         = "1"
      run_order       = "2"
      configuration = {
        ProjectName = var.aft_account_customizations_terraform_codebuild_name
        EnvironmentVariables = jsonencode([
          {
            name  = "VENDED_ACCOUNT_ID",
            value = var.account_id,
            type  = "PLAINTEXT"
          }
        ])
      }
    }
  }
}
