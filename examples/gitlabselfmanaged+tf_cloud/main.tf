# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
module "aft" {
  source = "github.com/aws-ia/terraform-aws-control_tower_account_factory"
  # Required Vars
  ct_management_account_id    = "111122223333"
  log_archive_account_id      = "444455556666"
  audit_account_id            = "123456789012"
  aft_management_account_id   = "777788889999"
  ct_home_region              = "us-east-1"
  tf_backend_secondary_region = "us-west-2"
  # VCS Vars
  vcs_provider                                  = "gitlabselfmanaged"
  gitlab_selfmanaged_url                        = "https://gitlab.example.com"
  account_request_repo_name                     = "ExampleProject/example-repo-1"
  global_customizations_repo_name               = "ExampleProject/example-repo-2"
  account_customizations_repo_name              = "ExampleProject/example-repo-3"
  account_provisioning_customizations_repo_name = "ExampleProject/example-repo-4"
  # TF Vars
  terraform_distribution = "tfc"
  terraform_token        = "EXAMPLE-uoc1c1qsw7poexampleewjeno1pte3rw"
  terraform_org_name     = "ExampleOrg"
}
