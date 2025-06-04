# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

locals {
  # Parse comma-separated email string from SSM parameter
  notification_emails = data.aws_ssm_parameter.aft_approval_notification_emails.value != "" ? split(",", data.aws_ssm_parameter.aft_approval_notification_emails.value) : []
}

# SNS Topic for approval notifications
resource "aws_sns_topic" "aft_approval_notifications" {
  count = length(local.notification_emails) > 0 ? 1 : 0
  name  = "${var.account_id}-aft-approval-notifications"
  
  kms_master_key_id = data.aws_kms_alias.aft_key.arn
}

# SNS Topic Subscriptions for approval notifications  
resource "aws_sns_topic_subscription" "aft_approval_email_notifications" {
  count     = length(local.notification_emails)
  topic_arn = aws_sns_topic.aft_approval_notifications[0].arn
  protocol  = "email"
  endpoint  = local.notification_emails[count.index]
}

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
  # Global-Plan
  ##############################################################
  stage {
    name = "Global-Plan"
    
    action {
      name            = "Plan"
      category        = "Build"
      owner           = "AWS"
      provider        = "CodeBuild"
      input_artifacts = ["source-aft-global-customizations"]
      version         = "1"
      run_order       = "1"
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

  ##############################################################
  # Global-Approval-Step
  ##############################################################
  stage {
    name = "Global-Approval-Step"
    
    action {
      name            = "Approval"
      category        = "Approval"
      owner           = "AWS"
      provider        = "Manual"
      input_artifacts = []
      version         = "1"
      run_order       = "1"
      
      configuration = length(local.notification_emails) > 0 ? {
        NotificationArn = aws_sns_topic.aft_approval_notifications[0].arn
        CustomData      = "Global customizations for account ${var.account_id} require approval before applying."
      } : {}
    }
  }

  ##############################################################
  # Global-Apply
  ##############################################################
  stage {
    name = "Global-Apply"
    
    action {
      name            = "Apply"
      category        = "Build"
      owner           = "AWS"
      provider        = "CodeBuild"
      input_artifacts = ["source-aft-global-customizations"]
      version         = "1"
      run_order       = "1"
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

  ##############################################################
  # Specific-Plan
  ##############################################################
  stage {
    name = "Specific-Plan"

    action {
      name            = "Plan"
      category        = "Build"
      owner           = "AWS"
      provider        = "CodeBuild"
      input_artifacts = ["source-aft-account-customizations"]
      version         = "1"
      run_order       = "1"
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

  ##############################################################
  # Specific-Plan-Approval-Step
  ##############################################################
  stage {
    name = "Specific-Plan-Approval-Step"

    action {
      name            = "Approval"
      category        = "Approval"
      owner           = "AWS"
      provider        = "Manual"
      input_artifacts = []
      version         = "1"
      run_order       = "1"
    }
  }

  ##############################################################
  # Specific-Apply
  ##############################################################
  stage {
    name = "Specific-Apply"

    action {
      name            = "Apply"
      category        = "Build"
      owner           = "AWS"
      provider        = "CodeBuild"
      input_artifacts = ["source-aft-account-customizations"]
      version         = "1"
      run_order       = "1"
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
  # Global-Plan
  ##############################################################
  stage {
    name = "Global-Plan"
    
    action {
      name            = "Plan"
      category        = "Build"
      owner           = "AWS"
      provider        = "CodeBuild"
      input_artifacts = ["source-aft-global-customizations"]
      version         = "1"
      run_order       = "1"
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

  ##############################################################
  # Global-Approval-Step
  ##############################################################
  stage {
    name = "Global-Approval-Step"
    
    action {
      name            = "Approval"
      category        = "Approval"
      owner           = "AWS"
      provider        = "Manual"
      input_artifacts = []
      version         = "1"
      run_order       = "1"
      
      configuration = length(local.notification_emails) > 0 ? {
        NotificationArn = aws_sns_topic.aft_approval_notifications[0].arn
        CustomData      = "Global customizations for account ${var.account_id} require approval before applying."
      } : {}
    }
  }

  ##############################################################
  # Global-Apply
  ##############################################################
  stage {
    name = "Global-Apply"
    
    action {
      name            = "Apply"
      category        = "Build"
      owner           = "AWS"
      provider        = "CodeBuild"
      input_artifacts = ["source-aft-global-customizations"]
      version         = "1"
      run_order       = "1"
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

  ##############################################################
  # Specific-Plan
  ##############################################################
  stage {
    name = "Specific-Plan"

    action {
      name            = "Plan"
      category        = "Build"
      owner           = "AWS"
      provider        = "CodeBuild"
      input_artifacts = ["source-aft-account-customizations"]
      version         = "1"
      run_order       = "1"
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

  ##############################################################
  # Specific-Plan-Approval-Step
  ##############################################################
  stage {
    name = "Specific-Plan-Approval-Step"

    action {
      name            = "Approval"
      category        = "Approval"
      owner           = "AWS"
      provider        = "Manual"
      input_artifacts = []
      version         = "1"
      run_order       = "1"
    }
  }

  ##############################################################
  # Specific-Apply
  ##############################################################
  stage {
    name = "Specific-Apply"

    action {
      name            = "Apply"
      category        = "Build"
      owner           = "AWS"
      provider        = "CodeBuild"
      input_artifacts = ["source-aft-account-customizations"]
      version         = "1"
      run_order       = "1"
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
