resource "aws_codecommit_repository" "global_customizations" {
  count           = local.vcs.is_codecommit ? 1 : 0
  repository_name = var.global_customizations_repo_name
  description     = "This repo holds the Global Customizations for the CT-AFT solution"
  default_branch  = var.global_customizations_repo_branch
}

resource "aws_codecommit_repository" "account_customizations" {
  count           = local.vcs.is_codecommit ? 1 : 0
  repository_name = var.account_customizations_repo_name
  description     = "This repo holds the Account Customizations for the CT-AFT solution"
  default_branch  = var.account_customizations_repo_branch
}

resource "aws_codecommit_repository" "account_request" {
  count           = local.vcs.is_codecommit ? 1 : 0
  repository_name = var.account_request_repo_name
  description     = "This repo holds the Account Request Terraform for the CT-AFT solution"
  default_branch  = var.account_request_repo_branch
}

resource "aws_codecommit_repository" "account_provisioning_customizations" {
  count           = local.vcs.is_codecommit ? 1 : 0
  repository_name = var.account_provisioning_customizations_repo_name
  description     = "This repo holds the Account Provisioning Customizations Step Function Terraform Project"
  default_branch  = var.account_provisioning_customizations_repo_branch
}