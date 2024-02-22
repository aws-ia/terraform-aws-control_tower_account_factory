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
    condition     = can(regex("(us(-gov)?|ap|ca|cn|eu|sa|me|af)-(central|(north|south)?(east|west)?)-\\d", var.ct_home_region))
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
  description = "Customer VCS Provider - valid inputs are codecommit, bitbucket, github, or githubenterprise"
  type        = string
  default     = "codecommit"
  validation {
    condition     = contains(["codecommit", "bitbucket", "github", "githubenterprise"], var.vcs_provider)
    error_message = "Valid values for var: vcs_provider are (codecommit, bitbucket, github, githubenterprise)."
  }
}

variable "github_enterprise_url" {
  description = "GitHub enterprise URL, if GitHub Enterprise is being used"
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
  default     = "1.5.7"
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

#########################################
# local_file replacement variables
#########################################

variable "aft_version" {
  type    = string
  default = "1.11.1"
}

variable "python_version" {
  type    = string
  default = "3.11"
}

variable "ct_aft_account_provisioning_customizations" {
  description = "build spec config from modules/aft-code-repositories/buildspecs/ct-aft-account-provisioning-customizations.yml"
  type        = string
  default     = <<EOT
# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
version: 0.2

phases:
  pre_build:
    commands:
      - DEFAULT_PATH=$(pwd)
      - TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
      - AWS_MODULE_SOURCE=$(aws ssm get-parameter --name "/aft/config/aft-pipeline-code-source/repo-url" --query "Parameter.Value" --output text)
      - AWS_MODULE_GIT_REF=$(aws ssm get-parameter --name "/aft/config/aft-pipeline-code-source/repo-git-ref" --query "Parameter.Value" --output text)
      - TF_VERSION=$(aws ssm get-parameter --name "/aft/config/terraform/version" --query "Parameter.Value" --output text)
      - TF_DISTRIBUTION=$(aws ssm get-parameter --name "/aft/config/terraform/distribution" --query "Parameter.Value" --output text)
      - CT_MGMT_REGION=$(aws ssm get-parameter --name "/aft/config/ct-management-region" --query "Parameter.Value" --output text)
      - AFT_MGMT_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
      - AFT_EXEC_ROLE_ARN=arn:$AWS_PARTITION:iam::$AFT_MGMT_ACCOUNT:role/AWSAFTExecution
      - AFT_ADMIN_ROLE_NAME=$(aws ssm get-parameter --name /aft/resources/iam/aft-administrator-role-name | jq --raw-output ".Parameter.Value")
      - AFT_ADMIN_ROLE_ARN=arn:$AWS_PARTITION:iam::$AFT_MGMT_ACCOUNT:role/$AFT_ADMIN_ROLE_NAME
      - ROLE_SESSION_NAME=$(aws ssm get-parameter --name /aft/resources/iam/aft-session-name | jq --raw-output ".Parameter.Value")
      - |
        ssh_key_parameter=$(aws ssm get-parameter --name /aft/config/aft-ssh-key --with-decryption 2> /dev/null || echo "None")
        if [[ $ssh_key_parameter != "None" ]]; then
          ssh_key=$(jq --raw-output ".Parameter.Value" <<< $ssh_key_parameter)
          mkdir -p ~/.ssh
          echo "Host *" >> ~/.ssh/config
          echo "StrictHostKeyChecking no" >> ~/.ssh/config
          echo "UserKnownHostsFile=/dev/null" >> ~/.ssh/config
          echo "$ssh_key" > ~/.ssh/ssh_key
          echo -e "\n\n" >>  ~/.ssh/ssh_key
          chmod 600 ~/.ssh/ssh_key
          eval "$(ssh-agent -s)"
          ssh-add ~/.ssh/ssh_key
        fi
      - git config --global credential.helper '!aws codecommit credential-helper $@'
      - git config --global credential.UseHttpPath true
      - git clone -b $AWS_MODULE_GIT_REF $AWS_MODULE_SOURCE aws-aft-core-framework
      - python3 -m venv ./venv
      - source ./venv/bin/activate
      - pip install jinja2-cli==0.7.0 Jinja2==3.0.1 MarkupSafe==2.0.1 boto3==1.18.56 requests==2.26.0
      - |
        if [ $TF_DISTRIBUTION = "oss" ]; then
          TF_BACKEND_REGION=$(aws ssm get-parameter --name "/aft/config/oss-backend/primary-region" --query "Parameter.Value" --output text)
          TF_KMS_KEY_ID=$(aws ssm get-parameter --name "/aft/config/oss-backend/kms-key-id" --query "Parameter.Value" --output text)
          TF_DDB_TABLE=$(aws ssm get-parameter --name "/aft/config/oss-backend/table-id" --query "Parameter.Value" --output text)
          TF_S3_BUCKET=$(aws ssm get-parameter --name "/aft/config/oss-backend/bucket-id" --query "Parameter.Value" --output text)
          TF_S3_KEY=account-provisioning-customizations/terraform.tfstate
          cd /tmp
          echo "Installing Terraform"
          curl -o terraform_$TF_VERSION_linux_amd64.zip https://releases.hashicorp.com/terraform/$TF_VERSION/terraform_$TF_VERSION_linux_amd64.zip
          unzip -o terraform_$TF_VERSION_linux_amd64.zip && mv terraform /usr/bin
          terraform -no-color --version
          cd $DEFAULT_PATH/terraform
          for f in *.jinja; do jinja2 $f -D timestamp="$TIMESTAMP" -D tf_distribution_type=$TF_DISTRIBUTION -D region=$TF_BACKEND_REGION -D provider_region=$CT_MGMT_REGION -D bucket=$TF_S3_BUCKET -D key=$TF_S3_KEY -D dynamodb_table=$TF_DDB_TABLE -D kms_key_id=$TF_KMS_KEY_ID -D aft_admin_role_arn=$AFT_EXEC_ROLE_ARN -D tf_version=$TF_VERSION >> ./$(basename $f .jinja).tf; done
          for f in *.tf; do echo "\n \n"; echo $f; cat $f; done
          JSON=$(aws sts assume-role --role-arn $AFT_ADMIN_ROLE_ARN --role-session-name $ROLE_SESSION_NAME)
          #Make newly assumed role default session
          export AWS_ACCESS_KEY_ID=$(echo $JSON | jq --raw-output ".Credentials[\"AccessKeyId\"]")
          export AWS_SECRET_ACCESS_KEY=$(echo $JSON | jq --raw-output ".Credentials[\"SecretAccessKey\"]")
          export AWS_SESSION_TOKEN=$(echo $JSON | jq --raw-output ".Credentials[\"SessionToken\"]")
          terraform init -no-color
        else
          TF_BACKEND_REGION=$(aws ssm get-parameter --name "/aft/config/oss-backend/primary-region" --query "Parameter.Value" --output text)
          TF_ORG_NAME=$(aws ssm get-parameter --name "/aft/config/terraform/org-name" --query "Parameter.Value" --output text)
          TF_TOKEN=$(aws ssm get-parameter --name "/aft/config/terraform/token" --with-decryption --query "Parameter.Value" --output text)
          TF_ENDPOINT=$(aws ssm get-parameter --name "/aft/config/terraform/api-endpoint" --query "Parameter.Value" --output text)
          TF_WORKSPACE_NAME="ct-aft-account-provisioning-customizations"
          TF_CONFIG_PATH="./temp_configuration_file.tar.gz"
          cd $DEFAULT_PATH/terraform
          for f in *.jinja; do jinja2 $f -D timestamp="$TIMESTAMP" -D provider_region=$CT_MGMT_REGION -D tf_distribution_type=$TF_DISTRIBUTION -D terraform_org_name=$TF_ORG_NAME -D terraform_workspace_name=$TF_WORKSPACE_NAME -D aft_admin_role_arn=$AFT_EXEC_ROLE_ARN >> ./$(basename $f .jinja).tf; done
          for f in *.tf; do echo "\n \n"; echo $f; cat $f; done
          cd $DEFAULT_PATH
          tar -czf temp_configuration_file.tar.gz -C terraform --exclude .git --exclude venv .
          python3 $DEFAULT_PATH/aws-aft-core-framework/sources/scripts/workspace_manager.py --operation "deploy" --organization_name $TF_ORG_NAME --workspace_name $TF_WORKSPACE_NAME --assume_role_arn $AFT_ADMIN_ROLE_ARN --assume_role_session_name $ROLE_SESSION_NAME --api_endpoint $TF_ENDPOINT --api_token $TF_TOKEN --terraform_version $TF_VERSION --config_file $TF_CONFIG_PATH
        fi

  build:
    commands:
      - |
        if [ $TF_DISTRIBUTION = "oss" ]; then
          terraform apply -no-color --auto-approve
        fi
  post_build:
    commands:
      - echo "Post-Build"

  EOT

}

variable "ct_aft_account_request" {
  description = "build spec config for to replace modules/aft-code-repositories/buildspecs/ct-aft-account-request.yml"
  type        = string
  default     = <<EOT
# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
version: 0.2

phases:
  pre_build:
    commands:
      - DEFAULT_PATH=$(pwd)
      - TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
      - AWS_MODULE_SOURCE=$(aws ssm get-parameter --name "/aft/config/aft-pipeline-code-source/repo-url" --query "Parameter.Value" --output text)
      - AWS_MODULE_GIT_REF=$(aws ssm get-parameter --name "/aft/config/aft-pipeline-code-source/repo-git-ref" --query "Parameter.Value" --output text)
      - TF_VERSION=$(aws ssm get-parameter --name "/aft/config/terraform/version" --query "Parameter.Value" --output text)
      - TF_DISTRIBUTION=$(aws ssm get-parameter --name "/aft/config/terraform/distribution" --query "Parameter.Value" --output text)
      - CT_MGMT_REGION=$(aws ssm get-parameter --name "/aft/config/ct-management-region" --query "Parameter.Value" --output text)
      - AFT_MGMT_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
      - AFT_EXEC_ROLE_ARN=arn:$AWS_PARTITION:iam::$AFT_MGMT_ACCOUNT:role/AWSAFTExecution
      - AFT_ADMIN_ROLE_NAME=$(aws ssm get-parameter --name /aft/resources/iam/aft-administrator-role-name | jq --raw-output ".Parameter.Value")
      - AFT_ADMIN_ROLE_ARN=arn:$AWS_PARTITION:iam::$AFT_MGMT_ACCOUNT:role/$AFT_ADMIN_ROLE_NAME
      - ROLE_SESSION_NAME=$(aws ssm get-parameter --name /aft/resources/iam/aft-session-name | jq --raw-output ".Parameter.Value")
      - |
        ssh_key_parameter=$(aws ssm get-parameter --name /aft/config/aft-ssh-key --with-decryption 2> /dev/null || echo "None")
        if [[ $ssh_key_parameter != "None" ]]; then
          ssh_key=$(jq --raw-output ".Parameter.Value" <<< $ssh_key_parameter)
          mkdir -p ~/.ssh
          echo "Host *" >> ~/.ssh/config
          echo "StrictHostKeyChecking no" >> ~/.ssh/config
          echo "UserKnownHostsFile=/dev/null" >> ~/.ssh/config
          echo "$ssh_key" > ~/.ssh/ssh_key
          echo -e "\n\n" >>  ~/.ssh/ssh_key
          chmod 600 ~/.ssh/ssh_key
          eval "$(ssh-agent -s)"
          ssh-add ~/.ssh/ssh_key
        fi
      - git config --global credential.helper '!aws codecommit credential-helper $@'
      - git config --global credential.UseHttpPath true
      - git clone -b $AWS_MODULE_GIT_REF $AWS_MODULE_SOURCE aws-aft-core-framework
      - python3 -m venv ./venv
      - source ./venv/bin/activate
      - pip install jinja2-cli==0.7.0 Jinja2==3.0.1 MarkupSafe==2.0.1 boto3==1.18.56 requests==2.26.0
      - |
        if [ $TF_DISTRIBUTION = "oss" ]; then
          TF_BACKEND_REGION=$(aws ssm get-parameter --name "/aft/config/oss-backend/primary-region" --query "Parameter.Value" --output text)
          TF_KMS_KEY_ID=$(aws ssm get-parameter --name "/aft/config/oss-backend/kms-key-id" --query "Parameter.Value" --output text)
          TF_DDB_TABLE=$(aws ssm get-parameter --name "/aft/config/oss-backend/table-id" --query "Parameter.Value" --output text)
          TF_S3_BUCKET=$(aws ssm get-parameter --name "/aft/config/oss-backend/bucket-id" --query "Parameter.Value" --output text)
          TF_S3_KEY=account-request/terraform.tfstate
          cd /tmp
          echo "Installing Terraform"
          curl -o terraform_$TF_VERSION_linux_amd64.zip https://releases.hashicorp.com/terraform/$TF_VERSION/terraform_$TF_VERSION_linux_amd64.zip
          unzip -o terraform_$TF_VERSION_linux_amd64.zip && mv terraform /usr/bin
          terraform --version
          cd $DEFAULT_PATH/terraform
          for f in *.jinja; do jinja2 $f -D timestamp="$TIMESTAMP" -D tf_distribution_type=$TF_DISTRIBUTION -D provider_region=$CT_MGMT_REGION -D region=$TF_BACKEND_REGION -D bucket=$TF_S3_BUCKET -D key=$TF_S3_KEY -D dynamodb_table=$TF_DDB_TABLE -D kms_key_id=$TF_KMS_KEY_ID -D aft_admin_role_arn=$AFT_EXEC_ROLE_ARN -D tf_version=$TF_VERSION >> ./$(basename $f .jinja).tf; done
          for f in *.tf; do echo "\n \n"; echo $f; cat $f; done
          JSON=$(aws sts assume-role --role-arn $AFT_ADMIN_ROLE_ARN --role-session-name $ROLE_SESSION_NAME)
          #Make newly assumed role default session
          export AWS_ACCESS_KEY_ID=$(echo $JSON | jq --raw-output ".Credentials[\"AccessKeyId\"]")
          export AWS_SECRET_ACCESS_KEY=$(echo $JSON | jq --raw-output ".Credentials[\"SecretAccessKey\"]")
          export AWS_SESSION_TOKEN=$(echo $JSON | jq --raw-output ".Credentials[\"SessionToken\"]")
          terraform init -no-color
        else
          TF_ORG_NAME=$(aws ssm get-parameter --name "/aft/config/terraform/org-name" --query "Parameter.Value" --output text)
          TF_TOKEN=$(aws ssm get-parameter --name "/aft/config/terraform/token" --with-decryption --query "Parameter.Value" --output text)
          TF_ENDPOINT=$(aws ssm get-parameter --name "/aft/config/terraform/api-endpoint" --query "Parameter.Value" --output text)
          TF_WORKSPACE_NAME="ct-aft-account-request"
          TF_CONFIG_PATH="./temp_configuration_file.tar.gz"
          cd $DEFAULT_PATH/terraform
          for f in *.jinja; do jinja2 $f -D timestamp="$TIMESTAMP" -D provider_region=$CT_MGMT_REGION -D tf_distribution_type=$TF_DISTRIBUTION -D terraform_org_name=$TF_ORG_NAME -D terraform_workspace_name=$TF_WORKSPACE_NAME -D aft_admin_role_arn=$AFT_EXEC_ROLE_ARN >> ./$(basename $f .jinja).tf; done
          for f in *.tf; do echo "\n \n"; echo $f; cat $f; done
          cd $DEFAULT_PATH
          tar -czf temp_configuration_file.tar.gz -C terraform --exclude .git --exclude venv .
          python3 $DEFAULT_PATH/aws-aft-core-framework/sources/scripts/workspace_manager.py --operation "deploy" --organization_name $TF_ORG_NAME --workspace_name $TF_WORKSPACE_NAME --assume_role_arn $AFT_ADMIN_ROLE_ARN --assume_role_session_name $ROLE_SESSION_NAME --api_endpoint $TF_ENDPOINT --api_token $TF_TOKEN --terraform_version $TF_VERSION --config_file $TF_CONFIG_PATH
        fi

  build:
    commands:
      - |
        if [ $TF_DISTRIBUTION = "oss" ]; then
          terraform apply -no-color --auto-approve
        fi
  post_build:
    commands:
      - echo "Post-Build"

  EOT

}

variable "aft_global_customizations_terraform" {
  description = "build spec config for to replace modules/aft-customizations/buildspecs/aft-global-customizations-terraform.yml"
  type        = string
  default     = <<EOT
# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
version: 0.2

phases:
  install:
    commands:
      - set -e
      # Populate Required Variables
      - DEFAULT_PATH=$(pwd)
      - TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
      - TF_VERSION=$(aws ssm get-parameter --name "/aft/config/terraform/version" --query "Parameter.Value" --output text)
      - TF_DISTRIBUTION=$(aws ssm get-parameter --name "/aft/config/terraform/distribution" --query "Parameter.Value" --output text)
      - CT_MGMT_REGION=$(aws ssm get-parameter --name "/aft/config/ct-management-region" --query "Parameter.Value" --output text)
      - AFT_MGMT_ACCOUNT=$(aws ssm get-parameter --name "/aft/account/aft-management/account-id" --query "Parameter.Value" --output text)
      - AFT_EXEC_ROLE_ARN=arn:$AWS_PARTITION:iam::$AFT_MGMT_ACCOUNT:role/AWSAFTExecution
      - VENDED_EXEC_ROLE_ARN=arn:$AWS_PARTITION:iam::$VENDED_ACCOUNT_ID:role/AWSAFTExecution
      - AFT_ADMIN_ROLE_NAME=$(aws ssm get-parameter --name /aft/resources/iam/aft-administrator-role-name | jq --raw-output ".Parameter.Value")
      - AFT_ADMIN_ROLE_ARN=arn:$AWS_PARTITION:iam::$AFT_MGMT_ACCOUNT:role/$AFT_ADMIN_ROLE_NAME
      - ROLE_SESSION_NAME=$(aws ssm get-parameter --name /aft/resources/iam/aft-session-name | jq --raw-output ".Parameter.Value")

      # Configure Development SSH Key
      - |
        ssh_key_parameter=$(aws ssm get-parameter --name /aft/config/aft-ssh-key --with-decryption 2> /dev/null || echo "None")
        if [[ $ssh_key_parameter != "None" ]]; then
          ssh_key=$(jq --raw-output ".Parameter.Value" <<< $ssh_key_parameter)
          mkdir -p ~/.ssh
          echo "Host *" >> ~/.ssh/config
          echo "StrictHostKeyChecking no" >> ~/.ssh/config
          echo "UserKnownHostsFile=/dev/null" >> ~/.ssh/config
          echo "$ssh_key" > ~/.ssh/ssh_key
          echo -e "\n\n" >>  ~/.ssh/ssh_key
          chmod 600 ~/.ssh/ssh_key
          eval "$(ssh-agent -s)"
          ssh-add ~/.ssh/ssh_key
        fi

      # Clone AFT
      - AWS_MODULE_SOURCE=$(aws ssm get-parameter --name "/aft/config/aft-pipeline-code-source/repo-url" --query "Parameter.Value" --output text)
      - AWS_MODULE_GIT_REF=$(aws ssm get-parameter --name "/aft/config/aft-pipeline-code-source/repo-git-ref" --query "Parameter.Value" --output text)
      - git config --global credential.helper '!aws codecommit credential-helper $@'
      - git config --global credential.UseHttpPath true
      - git clone --quiet -b $AWS_MODULE_GIT_REF $AWS_MODULE_SOURCE aws-aft-core-framework

      # Generate session profiles
      - chmod +x $DEFAULT_PATH/aws-aft-core-framework/sources/scripts/creds.sh
      - $DEFAULT_PATH/aws-aft-core-framework/sources/scripts/creds.sh

      # Install AFT Python Dependencies
      - python3 -m venv $DEFAULT_PATH/aft-venv
      - $DEFAULT_PATH/aft-venv/bin/pip install pip==22.1.2
      - $DEFAULT_PATH/aft-venv/bin/pip install jinja2-cli==0.7.0 Jinja2==3.0.1 MarkupSafe==2.0.1 boto3==1.18.56 requests==2.26.0

      # Install API Helper Python Dependencies
      - python3 -m venv $DEFAULT_PATH/api-helpers-venv
      - $DEFAULT_PATH/api-helpers-venv/bin/pip install -r $DEFAULT_PATH/api_helpers/python/requirements.txt

      # Mark helper scripts as executable
      - chmod +x $DEFAULT_PATH/api_helpers/pre-api-helpers.sh
      - chmod +x $DEFAULT_PATH/api_helpers/post-api-helpers.sh
      
  pre_build:
    on-failure: ABORT
    commands:
      - source $DEFAULT_PATH/api-helpers-venv/bin/activate
      - export AWS_PROFILE=aft-target
      - $DEFAULT_PATH/api_helpers/pre-api-helpers.sh
      - unset AWS_PROFILE

  build:
    on-failure: CONTINUE
    commands:
      # Apply customizations
      - source $DEFAULT_PATH/aft-venv/bin/activate
      - |
        if [ $TF_DISTRIBUTION = "oss" ]; then
          TF_BACKEND_REGION=$(aws ssm get-parameter --name "/aft/config/oss-backend/primary-region" --query "Parameter.Value" --output text)
          TF_KMS_KEY_ID=$(aws ssm get-parameter --name "/aft/config/oss-backend/kms-key-id" --query "Parameter.Value" --output text)
          TF_DDB_TABLE=$(aws ssm get-parameter --name "/aft/config/oss-backend/table-id" --query "Parameter.Value" --output text)
          TF_S3_BUCKET=$(aws ssm get-parameter --name "/aft/config/oss-backend/bucket-id" --query "Parameter.Value" --output text)
          TF_S3_KEY=$VENDED_ACCOUNT_ID-aft-global-customizations/terraform.tfstate

          cd /tmp
          echo "Installing Terraform"
          curl -q -o terraform_$TF_VERSION_linux_amd64.zip https://releases.hashicorp.com/terraform/$TF_VERSION/terraform_$TF_VERSION_linux_amd64.zip
          mkdir -p /opt/aft/bin
          unzip -q -o terraform_$TF_VERSION_linux_amd64.zip
          mv terraform /opt/aft/bin
          /opt/aft/bin/terraform -no-color --version

          # Move back to customization module
          cd $DEFAULT_PATH/terraform
          for f in *.jinja; do jinja2 $f -D timestamp="$TIMESTAMP" -D tf_distribution_type=$TF_DISTRIBUTION -D provider_region=$CT_MGMT_REGION -D region=$TF_BACKEND_REGION -D aft_admin_role_arn=$AFT_EXEC_ROLE_ARN -D target_admin_role_arn=$VENDED_EXEC_ROLE_ARN -D bucket=$TF_S3_BUCKET -D key=$TF_S3_KEY -D dynamodb_table=$TF_DDB_TABLE -D kms_key_id=$TF_KMS_KEY_ID -D tf_version=$TF_VERSION >> ./$(basename $f .jinja).tf; done
          for f in *.tf; do echo "\n \n"; echo $f; cat $f; done

          cd $DEFAULT_PATH/terraform
          export AWS_PROFILE=aft-management-admin
          /opt/aft/bin/terraform init -no-color
          /opt/aft/bin/terraform apply -no-color --auto-approve
        else
          TF_ORG_NAME=$(aws ssm get-parameter --name "/aft/config/terraform/org-name" --query "Parameter.Value" --output text)
          TF_TOKEN=$(aws ssm get-parameter --name "/aft/config/terraform/token" --with-decryption --query "Parameter.Value" --output text)
          TF_ENDPOINT=$(aws ssm get-parameter --name "/aft/config/terraform/api-endpoint" --query "Parameter.Value" --output text)
          TF_WORKSPACE_NAME=$VENDED_ACCOUNT_ID-aft-global-customizations
          TF_CONFIG_PATH="./temp_configuration_file.tar.gz"
          cd $DEFAULT_PATH/terraform
          for f in *.jinja; do jinja2 $f -D timestamp="$TIMESTAMP" -D provider_region=$CT_MGMT_REGION -D tf_distribution_type=$TF_DISTRIBUTION -D aft_admin_role_arn=$AFT_EXEC_ROLE_ARN -D target_admin_role_arn=$VENDED_EXEC_ROLE_ARN -D terraform_org_name=$TF_ORG_NAME -D terraform_workspace_name=$TF_WORKSPACE_NAME  >> ./$(basename $f .jinja).tf; done
          for f in *.tf; do echo "\n \n"; echo $f; cat $f; done
          cd $DEFAULT_PATH
          tar -czf temp_configuration_file.tar.gz -C terraform --exclude .git --exclude venv .
          python3 $DEFAULT_PATH/aws-aft-core-framework/sources/scripts/workspace_manager.py --operation "deploy" --organization_name $TF_ORG_NAME --workspace_name $TF_WORKSPACE_NAME --assume_role_arn $AFT_ADMIN_ROLE_ARN --assume_role_session_name $ROLE_SESSION_NAME --api_endpoint $TF_ENDPOINT --api_token $TF_TOKEN --terraform_version $TF_VERSION --config_file $TF_CONFIG_PATH
        fi

  post_build:
    on-failure: ABORT
    commands:
      - export PYTHONPATH="$DEFAULT_PATH/aws-aft-core-framework/sources/aft-lambda-layer:$PYTHONPATH"
      - export AWS_PROFILE=aft-management
      - python3 $DEFAULT_PATH/aws-aft-core-framework/sources/aft-lambda-layer/aft_common/metrics.py --codebuild-name "aft-global-customizations" --codebuild-status $CODEBUILD_BUILD_SUCCEEDING
      - unset AWS_PROFILE
      - |
        if [[ $CODEBUILD_BUILD_SUCCEEDING == 0 ]]; then
          exit 1
        fi
      - source $DEFAULT_PATH/api-helpers-venv/bin/activate
      - export AWS_PROFILE=aft-target
      - $DEFAULT_PATH/api_helpers/post-api-helpers.sh

  EOT
}

variable "aft_create_pipeline" {
  description = "build spec config for to replace modules/aft-customizations/buildspecs/aft-create-pipeline.yml"
  type        = string
  default     = <<EOT
# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
version: 0.2

phases:
  install:
    commands:
      - set -e
      # Populate Required Variables
      - DEFAULT_PATH=$(pwd)
      - TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
      - TF_S3_BUCKET=$(aws ssm get-parameter --name $SSM_TF_S3_BUCKET --query "Parameter.Value" --output text)
      - TF_S3_KEY=$VENDED_ACCOUNT_ID-customizations-pipeline/terraform.tfstate
      - TF_BACKEND_REGION=$(aws ssm get-parameter --name $SSM_TF_BACKEND_REGION --query "Parameter.Value" --output text)
      - TF_KMS_KEY_ID=$(aws ssm get-parameter --name $SSM_TF_KMS_KEY_ID --query "Parameter.Value" --output text)
      - TF_DDB_TABLE=$(aws ssm get-parameter --name $SSM_TF_DDB_TABLE --query "Parameter.Value" --output text)
      - TF_VERSION=$(aws ssm get-parameter --name $SSM_TF_VERSION --query "Parameter.Value" --output text)


      # Configure Development SSH Key
      - |
        ssh_key_parameter=$(aws ssm get-parameter --name /aft/config/aft-ssh-key --with-decryption 2> /dev/null || echo "None")
        if [[ $ssh_key_parameter != "None" ]]; then
          ssh_key=$(jq --raw-output ".Parameter.Value" <<< $ssh_key_parameter)
          mkdir -p ~/.ssh
          echo "Host *" >> ~/.ssh/config
          echo "StrictHostKeyChecking no" >> ~/.ssh/config
          echo "UserKnownHostsFile=/dev/null" >> ~/.ssh/config
          echo "$ssh_key" > ~/.ssh/ssh_key
          echo -e "\n\n" >>  ~/.ssh/ssh_key
          chmod 600 ~/.ssh/ssh_key
          eval "$(ssh-agent -s)"
          ssh-add ~/.ssh/ssh_key
        fi

      # Clone AFT
      - AWS_MODULE_SOURCE=$(aws ssm get-parameter --name $SSM_AWS_MODULE_SOURCE --query "Parameter.Value" --output text)
      - AWS_MODULE_GIT_REF=$(aws ssm get-parameter --name $SSM_AWS_MODULE_GIT_REF --query "Parameter.Value" --output text)
      - git config --global credential.helper '!aws codecommit credential-helper $@'
      - git config --global credential.UseHttpPath true
      - git clone --quiet -b $AWS_MODULE_GIT_REF $AWS_MODULE_SOURCE aws-aft-core-framework

      # Generate session profiles
      - chmod +x $DEFAULT_PATH/aws-aft-core-framework/sources/scripts/creds.sh
      - $DEFAULT_PATH/aws-aft-core-framework/sources/scripts/creds.sh

      # Install Terraform
      - cd /tmp
      - echo "Installing Terraform"
      - curl -q -o terraform_$TF_VERSION_linux_amd64.zip https://releases.hashicorp.com/terraform/$TF_VERSION/terraform_$TF_VERSION_linux_amd64.zip
      - unzip -q -o terraform_$TF_VERSION_linux_amd64.zip && mv terraform /usr/bin
      - terraform --version

      # Install Python Dependencies
      - python3 -m venv ./venv
      - source ./venv/bin/activate
      - pip install pip==22.1.2
      - pip install jinja2-cli==0.7.0 Jinja2==3.0.1

  pre_build:
    on-failure: ABORT
    commands:
      - cd $DEFAULT_PATH/aws-aft-core-framework/sources/aft-customizations-common/templates/customizations_pipeline
      - for f in *.jinja; do jinja2 $f -D timestamp="$TIMESTAMP" -D region=$TF_BACKEND_REGION -D bucket=$TF_S3_BUCKET -D key=$TF_S3_KEY -D dynamodb_table=$TF_DDB_TABLE -D kms_key_id=$TF_KMS_KEY_ID -D tf_version=$TF_VERSION >> $(basename $f .jinja).tf; done
      - for f in *.tf; do echo "\n \n"; echo $f; cat $f; done
  build:
    on-failure: ABORT
    commands:
      - export AWS_PROFILE=aft-management-admin
      - terraform init -no-color
      - terraform apply -var="account_id=$VENDED_ACCOUNT_ID" -no-color --auto-approve

  EOT
}

variable "aft_account_customizations_terraform" {
  description = "build spec config for to replace modules/aft-customizations/buildspecs/aft-account-customizations-terraform.yml"
  type        = string
  default     = <<EOT
  # Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
version: 0.2

phases:
  install:
    on-failure: ABORT
    commands:
      - set -e
      # Populate Required Variables
      - DEFAULT_PATH=$(pwd)
      - TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
      - TF_VERSION=$(aws ssm get-parameter --name "/aft/config/terraform/version" --query "Parameter.Value" --output text)
      - TF_DISTRIBUTION=$(aws ssm get-parameter --name "/aft/config/terraform/distribution" --query "Parameter.Value" --output text)
      - CT_MGMT_REGION=$(aws ssm get-parameter --name "/aft/config/ct-management-region" --query "Parameter.Value" --output text)
      - AFT_MGMT_ACCOUNT=$(aws ssm get-parameter --name "/aft/account/aft-management/account-id" --query "Parameter.Value" --output text)
      - AFT_EXEC_ROLE_ARN=arn:$AWS_PARTITION:iam::$AFT_MGMT_ACCOUNT:role/AWSAFTExecution
      - VENDED_EXEC_ROLE_ARN=arn:$AWS_PARTITION:iam::$VENDED_ACCOUNT_ID:role/AWSAFTExecution
      - AFT_ADMIN_ROLE_NAME=$(aws ssm get-parameter --name /aft/resources/iam/aft-administrator-role-name | jq --raw-output ".Parameter.Value")
      - AFT_ADMIN_ROLE_ARN=arn:$AWS_PARTITION:iam::$AFT_MGMT_ACCOUNT:role/$AFT_ADMIN_ROLE_NAME
      - ROLE_SESSION_NAME=$(aws ssm get-parameter --name /aft/resources/iam/aft-session-name | jq --raw-output ".Parameter.Value")
      - |
        CUSTOMIZATION=$(aws dynamodb get-item --table-name aft-request-metadata --key "{\"id\": {\"S\": \"$VENDED_ACCOUNT_ID\"}}" --attributes-to-get "account_customizations_name" | jq --raw-output ".Item.account_customizations_name.S")

      # Check if customization directory exists       
      - |
        if [[ ! -z "$CUSTOMIZATION" ]]; then  
          if [[ ! -d "$DEFAULT_PATH/$CUSTOMIZATION" ]]; then
            echo "Error: $CUSTOMIZATION directory does not exist"
            exit 1
          fi
          
          echo "Found customization" $CUSTOMIZATION

          # Configure Development SSH Key
          ssh_key_parameter=$(aws ssm get-parameter --name /aft/config/aft-ssh-key --with-decryption 2> /dev/null || echo "None")

          if [[ $ssh_key_parameter != "None" ]]; then
            ssh_key=$(jq --raw-output ".Parameter.Value" <<< $ssh_key_parameter)
            mkdir -p ~/.ssh
            echo "Host *" >> ~/.ssh/config
            echo "StrictHostKeyChecking no" >> ~/.ssh/config
            echo "UserKnownHostsFile=/dev/null" >> ~/.ssh/config
            echo "$ssh_key" > ~/.ssh/ssh_key
            echo -e "\n\n" >>  ~/.ssh/ssh_key
            chmod 600 ~/.ssh/ssh_key
            eval "$(ssh-agent -s)"
            ssh-add ~/.ssh/ssh_key
          fi   

          # Clone AFT
          AWS_MODULE_SOURCE=$(aws ssm get-parameter --name "/aft/config/aft-pipeline-code-source/repo-url" --query "Parameter.Value" --output text)
          AWS_MODULE_GIT_REF=$(aws ssm get-parameter --name "/aft/config/aft-pipeline-code-source/repo-git-ref" --query "Parameter.Value" --output text)
          git config --global credential.helper '!aws codecommit credential-helper $@'
          git config --global credential.UseHttpPath true
          git clone --quiet -b $AWS_MODULE_GIT_REF $AWS_MODULE_SOURCE aws-aft-core-framework

          # Install AFT Python Dependencies
          python3 -m venv $DEFAULT_PATH/aft-venv
          $DEFAULT_PATH/aft-venv/bin/pip install pip==22.1.2
          $DEFAULT_PATH/aft-venv/bin/pip install jinja2-cli==0.7.0 Jinja2==3.0.1 MarkupSafe==2.0.1 boto3==1.18.56 requests==2.26.0

          # Install API Helper Python Dependencies
          python3 -m venv $DEFAULT_PATH/api-helpers-venv
          $DEFAULT_PATH/api-helpers-venv/bin/pip install -r $DEFAULT_PATH/$CUSTOMIZATION/api_helpers/python/requirements.txt

          # Mark helper scripts as executable
          chmod +x $DEFAULT_PATH/$CUSTOMIZATION/api_helpers/pre-api-helpers.sh
          chmod +x $DEFAULT_PATH/$CUSTOMIZATION/api_helpers/post-api-helpers.sh

          # Generate session profiles
          chmod +x $DEFAULT_PATH/aws-aft-core-framework/sources/scripts/creds.sh
          $DEFAULT_PATH/aws-aft-core-framework/sources/scripts/creds.sh
        fi


  pre_build:
    on-failure: ABORT
    commands:
      - |
        if [[ ! -z "$CUSTOMIZATION" ]]; then 
          source $DEFAULT_PATH/api-helpers-venv/bin/activate
          export AWS_PROFILE=aft-target
          $DEFAULT_PATH/$CUSTOMIZATION/api_helpers/pre-api-helpers.sh
          unset AWS_PROFILE
        fi

  build:
    on-failure: CONTINUE
    commands:
      # Apply Customizations
      - |
        if [[ ! -z "$CUSTOMIZATION" ]]; then 
          source $DEFAULT_PATH/aft-venv/bin/activate
          if [ $TF_DISTRIBUTION = "oss" ]; then
            TF_BACKEND_REGION=$(aws ssm get-parameter --name "/aft/config/oss-backend/primary-region" --query "Parameter.Value" --output text)
            TF_KMS_KEY_ID=$(aws ssm get-parameter --name "/aft/config/oss-backend/kms-key-id" --query "Parameter.Value" --output text)
            TF_DDB_TABLE=$(aws ssm get-parameter --name "/aft/config/oss-backend/table-id" --query "Parameter.Value" --output text)
            TF_S3_BUCKET=$(aws ssm get-parameter --name "/aft/config/oss-backend/bucket-id" --query "Parameter.Value" --output text)
            TF_S3_KEY=$VENDED_ACCOUNT_ID-aft-account-customizations/terraform.tfstate

            cd /tmp
            echo "Installing Terraform"
            curl -q -o terraform_$TF_VERSION_linux_amd64.zip https://releases.hashicorp.com/terraform/$TF_VERSION/terraform_$TF_VERSION_linux_amd64.zip
            mkdir -p /opt/aft/bin
            unzip -q -o terraform_$TF_VERSION_linux_amd64.zip 
            mv terraform /opt/aft/bin
            /opt/aft/bin/terraform -no-color --version

            cd $DEFAULT_PATH/$CUSTOMIZATION/terraform
            for f in *.jinja; do jinja2 $f -D timestamp="$TIMESTAMP" -D tf_distribution_type=$TF_DISTRIBUTION -D provider_region=$CT_MGMT_REGION -D region=$TF_BACKEND_REGION -D aft_admin_role_arn=$AFT_EXEC_ROLE_ARN -D target_admin_role_arn=$VENDED_EXEC_ROLE_ARN -D bucket=$TF_S3_BUCKET -D key=$TF_S3_KEY -D dynamodb_table=$TF_DDB_TABLE -D kms_key_id=$TF_KMS_KEY_ID -D tf_version=$TF_VERSION >> ./$(basename $f .jinja).tf; done
            for f in *.tf; do echo "\n \n"; echo $f; cat $f; done
            
            cd $DEFAULT_PATH/$CUSTOMIZATION/terraform
            export AWS_PROFILE=aft-management-admin
            /opt/aft/bin/terraform init -no-color
            /opt/aft/bin/terraform apply -no-color --auto-approve
          else
            TF_BACKEND_REGION=$(aws ssm get-parameter --name "/aft/config/oss-backend/primary-region" --query "Parameter.Value" --output text)
            TF_ORG_NAME=$(aws ssm get-parameter --name "/aft/config/terraform/org-name" --query "Parameter.Value" --output text)
            TF_TOKEN=$(aws ssm get-parameter --name "/aft/config/terraform/token" --with-decryption --query "Parameter.Value" --output text)
            TF_ENDPOINT=$(aws ssm get-parameter --name "/aft/config/terraform/api-endpoint" --query "Parameter.Value" --output text)
            TF_WORKSPACE_NAME=$VENDED_ACCOUNT_ID-aft-account-customizations
            TF_CONFIG_PATH="./temp_configuration_file.tar.gz"

            cd $DEFAULT_PATH/$CUSTOMIZATION/terraform
            for f in *.jinja; do jinja2 $f -D timestamp="$TIMESTAMP" -D provider_region=$CT_MGMT_REGION -D tf_distribution_type=$TF_DISTRIBUTION -D aft_admin_role_arn=$AFT_EXEC_ROLE_ARN -D target_admin_role_arn=$VENDED_EXEC_ROLE_ARN -D terraform_org_name=$TF_ORG_NAME -D terraform_workspace_name=$TF_WORKSPACE_NAME  >> ./$(basename $f .jinja).tf; done
            for f in *.tf; do echo "\n \n"; echo $f; cat $f; done
            
            cd $DEFAULT_PATH/$CUSTOMIZATION
            tar -czf temp_configuration_file.tar.gz -C terraform --exclude .git --exclude venv .
            python3 $DEFAULT_PATH/aws-aft-core-framework/sources/scripts/workspace_manager.py --operation "deploy" --organization_name $TF_ORG_NAME --workspace_name $TF_WORKSPACE_NAME --assume_role_arn $AFT_ADMIN_ROLE_ARN --assume_role_session_name $ROLE_SESSION_NAME --api_endpoint $TF_ENDPOINT --api_token $TF_TOKEN --terraform_version $TF_VERSION --config_file $TF_CONFIG_PATH
          fi
        fi
  post_build:
    on-failure: ABORT
    commands:
      - |
        if [[ ! -z "$CUSTOMIZATION" ]]; then
          export PYTHONPATH="$DEFAULT_PATH/aws-aft-core-framework/sources/aft-lambda-layer:$PYTHONPATH"
          export AWS_PROFILE=aft-management
          python3 $DEFAULT_PATH/aws-aft-core-framework/sources/aft-lambda-layer/aft_common/metrics.py --codebuild-name "aft-account-customizations" --codebuild-status $CODEBUILD_BUILD_SUCCEEDING
          unset AWS_PROFILE
        fi
      - |
        if [[ $CODEBUILD_BUILD_SUCCEEDING == 0 ]]; then
          exit 1
        fi
      - |
        if [[ ! -z "$CUSTOMIZATION" ]]; then 
          source $DEFAULT_PATH/api-helpers-venv/bin/activate
          export AWS_PROFILE=aft-target
          $DEFAULT_PATH/$CUSTOMIZATION/api_helpers/post-api-helpers.sh
        fi

  EOT
}

variable "aft_lambda_layer" {
  description = "build spec config for to replace modules/aft-lambda-layer/buildspecs/aft-lambda-layer.yml"
  type        = string
  default     = <<EOT
# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
version: 0.2

phases:
  install:
    runtime-versions:
      python: $PYTHON_VERSION
    commands:
      - DEFAULT_PATH=$(pwd)
      - AWS_MODULE_SOURCE=$(aws ssm get-parameter --name $SSM_AWS_MODULE_SOURCE --query "Parameter.Value" --output text)
      - AWS_MODULE_GIT_REF=$(aws ssm get-parameter --name $SSM_AWS_MODULE_GIT_REF --query "Parameter.Value" --output text)
      # URL Without Access ID
      - URL=$(echo "$AWS_MODULE_SOURCE" | awk '{split($0,a,"@"); print a[2]}')
      - |
        ssh_key_parameter=$(aws ssm get-parameter --name /aft/config/aft-ssh-key --with-decryption 2> /dev/null || echo "None")
        if [[ $ssh_key_parameter != "None" ]]; then
          ssh_key=$(jq --raw-output ".Parameter.Value" <<< $ssh_key_parameter)
          mkdir -p ~/.ssh
          echo "Host *" >> ~/.ssh/config
          echo "StrictHostKeyChecking no" >> ~/.ssh/config
          echo "UserKnownHostsFile=/dev/null" >> ~/.ssh/config
          echo "$ssh_key" > ~/.ssh/ssh_key
          echo -e "\n\n" >>  ~/.ssh/ssh_key
          chmod 600 ~/.ssh/ssh_key
          eval "$(ssh-agent -s)"
          ssh-add ~/.ssh/ssh_key
        fi
      - git config --global credential.helper '!aws codecommit credential-helper $@'
      - git config --global credential.UseHttpPath true
      - echo "Building aft_common from $URL:$AWS_MODULE_GIT_REF"
      - git clone -b $AWS_MODULE_GIT_REF $AWS_MODULE_SOURCE aws-aft-core-framework
      - python3 -m pip install virtualenv
      - python3 -m venv .venv
      - . .venv/bin/activate
      - python3 -m pip install ./aws-aft-core-framework/sources/aft-lambda-layer
  build:
    commands:
      - mkdir -p python
      - ls
      - mv -v ./.venv/lib/ ./python/
      - zip -r layer.zip python
      - aws s3 cp layer.zip s3://$BUCKET_NAME/layer.zip

  EOT
}