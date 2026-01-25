# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
#########################################
# Control Tower Core Account Parameters
#########################################
variable "ct_management_account_id" {
  description = "Control Tower Management Account Id"
  type        = string
  validation {
    condition     = can(regex("^\\d{12}$", var.ct_management_account_id))
    error_message = "Variable var: ct_management_account_id is not valid."
  }
}
variable "log_archive_account_id" {
  description = "Log Archive Account Id"
  type        = string
  validation {
    condition     = can(regex("^\\d{12}$", var.log_archive_account_id))
    error_message = "Variable var: log_archive_account_id is not valid."
  }
}
variable "audit_account_id" {
  description = "Audit Account Id"
  type        = string
  validation {
    condition     = can(regex("^\\d{12}$", var.audit_account_id))
    error_message = "Variable var: audit_account_id is not valid."
  }
}

#########################################
# General AFT Vars
#########################################

variable "aft_framework_repo_url" {
  description = "Git repo URL where the AFT framework should be sourced from"
  default     = "https://github.com/aws-ia/terraform-aws-control_tower_account_factory.git"
  type        = string
  validation {
    condition     = length(var.aft_framework_repo_url) > 0
    error_message = "Variable var: aft_framework_repo_url cannot be empty."
  }
}

variable "aft_framework_repo_git_ref" {
  description = "Git branch from which the AFT framework should be sourced from"
  default     = null
  type        = string
}

variable "aft_management_account_id" {
  description = "AFT Management Account ID"
  type        = string
  validation {
    condition     = can(regex("^\\d{12}$", var.aft_management_account_id))
    error_message = "Variable var: aft_management_account_id is not valid."
  }
}

variable "ct_home_region" {
  description = "The region from which this module will be executed. This MUST be the same region as Control Tower is deployed."
  type        = string
  validation {
    condition     = can(regex("(us(-gov)?|ap|ca|cn|eu|sa|me|af|il)-(central|(north|south)?(east|west)?)-\\d", var.ct_home_region))
    error_message = "Variable var: region is not valid."
  }
}

variable "cloudwatch_log_group_retention" {
  description = "Amount of days to keep CloudWatch Log Groups for Lambda functions. 0 = Never Expire"
  type        = string
  default     = "0"
  validation {
    condition     = contains(["1", "3", "5", "7", "14", "30", "60", "90", "120", "150", "180", "365", "400", "545", "731", "1827", "3653", "0"], var.cloudwatch_log_group_retention)
    error_message = "Valid values for var: cloudwatch_log_group_retention are (1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, 3653, and 0)."
  }
}

variable "cloudwatch_log_group_enable_cmk_encryption" {
  type        = bool
  description = "Flag toggling CloudWatch Log Groups encryption by using the AFT customer managed key stored in KMS. Additional charges apply. Otherwise, logs will use CloudWatch managed server-side encryption."
  default     = false
}

variable "backup_recovery_point_retention" {
  description = "Number of days to keep backup recovery points in AFT DynamoDB tables. Default = Never Expire"
  type        = number
  default     = null
  validation {
    condition     = var.backup_recovery_point_retention == null ? true : (var.backup_recovery_point_retention >= 1 && var.backup_recovery_point_retention <= 36500)
    error_message = "Value must be between 1 and 36500."
  }
}
variable "log_archive_bucket_object_expiration_days" {
  description = "Amount of days to keep the objects stored in the AFT logging bucket"
  type        = number
  default     = 365
  validation {
    condition     = var.log_archive_bucket_object_expiration_days > 0
    error_message = "Log_archive_bucket_object_expiration_days must be an integer greater than 0."
  }
}

variable "aft_backend_bucket_access_logs_object_expiration_days" {
  description = "Amount of days to keep the objects stored in the access logs bucket for AFT backend buckets"
  type        = number
  default     = 365
  validation {
    condition     = var.aft_backend_bucket_access_logs_object_expiration_days > 0
    error_message = "Aft_backend_bucket_access_logs_object_expiration_days must be an integer greater than 0."
  }
}

variable "sfn_s3_bucket_object_expiration_days" {
  description = "Amount of days to keep the objects stored in the CodePipeline bucket for AFT Step Functions"
  type        = number
  default     = 90
}

variable "maximum_concurrent_customizations" {
  description = "Maximum number of customizations/pipelines to run at once"
  type        = number
  default     = 5
  validation {
    condition     = var.maximum_concurrent_customizations > 0
    error_message = "Maximum_concurrent_customizations must be greater than 0."
  }
}

variable "aft_vpc_endpoints" {
  type        = bool
  description = "Flag turning VPC endpoints on/off for AFT VPC"
  default     = true
  validation {
    condition     = contains([true, false], var.aft_vpc_endpoints)
    error_message = "Valid values for var: aft_vpc_endpoints are (true, false)."
  }
}

variable "concurrent_account_factory_actions" {
  description = "Maximum number of accounts that can be provisioned in parallel."
  type        = number
  default     = 5
  validation {
    condition     = var.concurrent_account_factory_actions > 0
    error_message = "Maximum_concurrent_accounts_being_provisioned must be greater than 0."
  }
}

variable "global_codebuild_timeout" {
  type        = number
  description = "Codebuild build timeout"
  default     = 60
  validation {
    condition = (
      var.global_codebuild_timeout >= 5 &&
      var.global_codebuild_timeout <= 480
    )
    error_message = "Codebuild build timeout must be between 5 and 480 minutes."
  }
}

variable "tags" {
  description = "Map of tags to apply to resources deployed by AFT."
  type        = map(any)
  default     = null
}

#########################################
# AFT Feature Flags
#########################################

variable "aft_feature_cloudtrail_data_events" {
  description = "Feature flag toggling CloudTrail data events on/off"
  type        = bool
  default     = false
  validation {
    condition     = contains([true, false], var.aft_feature_cloudtrail_data_events)
    error_message = "Valid values for var: aft_feature_cloudtrail_data_events are (true, false)."
  }
}
variable "aft_feature_enterprise_support" {
  description = "Feature flag toggling Enterprise Support enrollment on/off"
  type        = bool
  default     = false
  validation {
    condition     = contains([true, false], var.aft_feature_enterprise_support)
    error_message = "Valid values for var: aft_feature_enterprise_support are (true, false)."
  }
}

variable "aft_feature_delete_default_vpcs_enabled" {
  description = "Feature flag toggling deletion of default VPCs on/off"
  type        = bool
  default     = false
  validation {
    condition     = contains([true, false], var.aft_feature_delete_default_vpcs_enabled)
    error_message = "Valid values for var: aft_feature_delete_default_vpcs_enabled are (true, false)."
  }
}

#########################################
# AFT Customer VCS Variables
#########################################


variable "vcs_provider" {
  description = "Customer VCS Provider - valid inputs are codecommit, bitbucket, github, githubenterprise, gitlab, or gitLab self-managed"
  type        = string
  default     = "codecommit"
  validation {
    condition     = contains(["codecommit", "bitbucket", "github", "githubenterprise", "gitlab", "gitlabselfmanaged", "azuredevops"], var.vcs_provider)
    error_message = "Valid values for var: vcs_provider are (codecommit, bitbucket, github, githubenterprise, gitlab, gitlabselfmanaged, azuredevops)."
  }
}

variable "github_enterprise_url" {
  description = "GitHub enterprise URL, if GitHub Enterprise is being used"
  type        = string
  default     = "null"
}
variable "gitlab_selfmanaged_url" {
  description = "GitLab SelfManaged URL, if GitLab SelfManaged is being used"
  type        = string
  default     = "null"
}
variable "account_request_repo_name" {
  description = "Repository name for the account request files. For non-CodeCommit repos, name should be in the format of Org/Repo"
  type        = string
  default     = "aft-account-request"
  validation {
    condition     = length(var.account_request_repo_name) > 0
    error_message = "Variable var: account_request_repo_name cannot be empty."
  }
}

variable "account_request_repo_branch" {
  description = "Branch to source account request repo from"
  type        = string
  default     = "main"
  validation {
    condition     = length(var.account_request_repo_branch) > 0
    error_message = "Variable var: account_request_repo_branch cannot be empty."
  }
}

variable "global_customizations_repo_name" {
  description = "Repository name for the global customization files. For non-CodeCommit repos, name should be in the format of Org/Repo"
  type        = string
  default     = "aft-global-customizations"
  validation {
    condition     = length(var.global_customizations_repo_name) > 0
    error_message = "Variable var: global_customizations_repo_name cannot be empty."
  }
}

variable "global_customizations_repo_branch" {
  description = "Branch to source global customizations repo from"
  type        = string
  default     = "main"
  validation {
    condition     = length(var.global_customizations_repo_branch) > 0
    error_message = "Variable var: global_customizations_repo_branch cannot be empty."
  }
}

variable "account_customizations_repo_name" {
  description = "Repository name for the account customizations files. For non-CodeCommit repos, name should be in the format of Org/Repo"
  type        = string
  default     = "aft-account-customizations"
  validation {
    condition     = length(var.account_customizations_repo_name) > 0
    error_message = "Variable var: account_customizations_repo_name cannot be empty."
  }
}

variable "account_customizations_repo_branch" {
  description = "Branch to source account customizations repo from"
  type        = string
  default     = "main"
  validation {
    condition     = length(var.account_customizations_repo_branch) > 0
    error_message = "Variable var: account_customizations_repo_branch cannot be empty."
  }
}

variable "account_provisioning_customizations_repo_name" {
  description = "Repository name for the account provisioning customizations files. For non-CodeCommit repos, name should be in the format of Org/Repo"
  type        = string
  default     = "aft-account-provisioning-customizations"
  validation {
    condition     = length(var.account_provisioning_customizations_repo_name) > 0
    error_message = "Variable var: account_provisioning_customizations_repo_name cannot be empty."
  }
}

variable "account_provisioning_customizations_repo_branch" {
  description = "Branch to source account provisioning customization files"
  type        = string
  default     = "main"
  validation {
    condition     = length(var.account_provisioning_customizations_repo_branch) > 0
    error_message = "Variable var: account_provisioning_customizations_repo_branch cannot be empty."
  }
}

#########################################
# AFT Terraform Distribution Variables
#########################################

variable "terraform_version" {
  description = "Terraform version being used for AFT"
  type        = string
  default     = "1.6.0"
  validation {
    condition     = can(regex("\\bv?\\d+(\\.\\d+)+[\\-\\w]*\\b", var.terraform_version))
    error_message = "Invalid value for var: terraform_version."
  }
}

variable "terraform_distribution" {
  description = "Terraform distribution being used for AFT - valid values are oss, tfc, or tfe"
  type        = string
  default     = "oss"
  validation {
    condition     = contains(["oss", "tfc", "tfe"], var.terraform_distribution)
    error_message = "Valid values for var: terraform_distribution are (oss, tfc, tfe)."
  }
}

variable "tf_backend_secondary_region" {
  default     = ""
  type        = string
  description = "AFT creates a backend for state tracking for its own state as well as OSS cases. The backend's primary region is the same as the AFT region, but this defines the secondary region to replicate to."
  validation {
    condition     = var.tf_backend_secondary_region == "" || can(regex("(us(-gov)?|ap|ca|cn|eu|sa|me|af)-(central|(north|south)?(east|west)?)-\\d", var.tf_backend_secondary_region))
    error_message = "Variable var: tf_backend_secondary_region is not valid."
  }
}

# Non-OSS Variables
variable "terraform_token" {
  type        = string
  description = "Terraform token for Cloud or Enterprise"
  default     = "null" # Non-sensitive default value #tfsec:ignore:general-secrets-no-plaintext-exposure
  sensitive   = true
  validation {
    condition     = length(var.terraform_token) > 0
    error_message = "Variable var: terraform_token cannot be empty."
  }
}

variable "terraform_org_name" {
  type        = string
  description = "Organization name for Terraform Cloud or Enterprise"
  default     = "null"
  validation {
    condition     = length(var.terraform_org_name) > 0
    error_message = "Variable var: terraform_org_name cannot be empty."
  }
}

variable "terraform_project_name" {
  type        = string
  description = "Project name for Terraform Cloud or Enterprise - project must exist before deployment"
  default     = "Default Project"
  validation {
    condition     = length(var.terraform_project_name) > 0
    error_message = "Variable var: terraform_project_name cannot be empty."
  }
}

variable "terraform_api_endpoint" {
  description = "API Endpoint for Terraform. Must be in the format of https://xxx.xxx."
  type        = string
  default     = "https://app.terraform.io/api/v2/"
  validation {
    condition     = length(var.terraform_api_endpoint) > 0
    error_message = "Variable var: terraform_api_endpoint cannot be empty."
  }
}

#########################################
# AFT VPC Variables
#########################################
variable "aft_enable_vpc" {
  description = "Flag turning use of VPC on/off for AFT"
  type        = bool
  default     = true
  validation {
    condition     = contains([true, false], var.aft_enable_vpc)
    error_message = "Valid values for var: aft_enable_vpc are (true, false)."
  }
}

variable "aft_vpc_cidr" {
  type        = string
  description = "CIDR Block to allocate to the AFT VPC"
  default     = "192.168.0.0/22"
  validation {
    condition     = can(regex("^([0-9]{1,3}\\.){3}[0-9]{1,3}(\\/([0-9]|[1-2][0-9]|3[0-2]))?$", var.aft_vpc_cidr))
    error_message = "Variable var: aft_vpc_cidr value must be a valid network CIDR, x.x.x.x/y."
  }
}

variable "aft_vpc_private_subnet_01_cidr" {
  type        = string
  description = "CIDR Block to allocate to the Private Subnet 01"
  default     = "192.168.0.0/24"
  validation {
    condition     = can(regex("^([0-9]{1,3}\\.){3}[0-9]{1,3}(\\/([0-9]|[1-2][0-9]|3[0-2]))?$", var.aft_vpc_private_subnet_01_cidr))
    error_message = "Variable var: aft_vpc_private_subnet_01_cidr value must be a valid network CIDR, x.x.x.x/y."
  }
}

variable "aft_vpc_private_subnet_02_cidr" {
  type        = string
  description = "CIDR Block to allocate to the Private Subnet 02"
  default     = "192.168.1.0/24"
  validation {
    condition     = can(regex("^([0-9]{1,3}\\.){3}[0-9]{1,3}(\\/([0-9]|[1-2][0-9]|3[0-2]))?$", var.aft_vpc_private_subnet_02_cidr))
    error_message = "Variable var: aft_vpc_private_subnet_02_cidr value must be a valid network CIDR, x.x.x.x/y."
  }
}

variable "aft_vpc_public_subnet_01_cidr" {
  type        = string
  description = "CIDR Block to allocate to the Public Subnet 01"
  default     = "192.168.2.0/25"
  validation {
    condition     = can(regex("^([0-9]{1,3}\\.){3}[0-9]{1,3}(\\/([0-9]|[1-2][0-9]|3[0-2]))?$", var.aft_vpc_public_subnet_01_cidr))
    error_message = "Variable var: aft_vpc_public_subnet_01_cidr value must be a valid network CIDR, x.x.x.x/y."
  }
}

variable "aft_vpc_public_subnet_02_cidr" {
  type        = string
  description = "CIDR Block to allocate to the Public Subnet 02"
  default     = "192.168.2.128/25"
  validation {
    condition     = can(regex("^([0-9]{1,3}\\.){3}[0-9]{1,3}(\\/([0-9]|[1-2][0-9]|3[0-2]))?$", var.aft_vpc_public_subnet_02_cidr))
    error_message = "Variable var: aft_vpc_public_subnet_02_cidr value must be a valid network CIDR, x.x.x.x/y."
  }
}

variable "aft_customer_vpc_id" {
  type        = string
  description = "The VPC ID to deploy AFT resources in, if customer is providing an existing VPC. Only supported for new deployments."
  default     = null
}

variable "aft_customer_private_subnets" {
  type        = list(string)
  description = "A list of private subnets to deploy AFT resources in, if customer is providing an existing VPC. Only supported for new deployments."
  default     = []
}

variable "aft_codebuild_compute_type" {
  type        = string
  description = "The CodeBuild compute type that build projects will use."
  default     = "BUILD_GENERAL1_MEDIUM"
  validation {
    condition     = can(regex("^BUILD_", var.aft_codebuild_compute_type))
    error_message = "aft_codebuild_compute_type value should start with `BUILD_`"
  }
}

variable "sns_topic_enable_cmk_encryption" {
  type        = bool
  description = "Flag toggling SNS topics encryption by using the AFT Customer managed key stored in KMS. Additional charges apply. Otherwise the SNS topics are encrypted using the AWS-managed KMS key."
  default     = false
}

#########################################
# AFT Metrics Reporting Variables
#########################################

variable "aft_metrics_reporting" {
  description = "Flag toggling reporting of operational metrics"
  type        = bool
  default     = true
  validation {
    condition     = contains([true, false], var.aft_metrics_reporting)
    error_message = "Valid values for var: aft_metrics_reporting are (true, false)."
  }
}
