# AWS Control Tower Account Factory for Terraform 
AWS Control Tower Account Factory for Terraform (AFT) follows a GitOps model to automate the processes of account provisioning and account updating in AWS Control Tower. You'll create an *account request* Terraform file, which provides the necessary input that triggers the AFT workflow for account provisioning.


For more information on AFT, see [Overview of AWS Control Tower Account Factory for Terraform](https://docs.aws.amazon.com/controltower/latest/userguide/aft-overview.html)

## Getting started

This guide is intended for administrators of AWS Control Tower environments who wish to set up Account Factory for Terraform (AFT) in their environment. It describes how to set up an Account Factory for Terraform (AFT) environment with a new, dedicated AFT management account. This guide follows the deployment steps outlined in [Deploy AWS Control Tower Account Factory for Terraform (AFT)](https://docs.aws.amazon.com/controltower/latest/userguide/aft-getting-started.html)

## Configure and launch your AWS Control Tower Account Factory for Terraform

Five steps are required to configure and launch your AFT environment.

**Step 1**: Launch your AWS Control Tower landing zone

Before launching AFT, you must have a working AWS Control Tower landing zone in your AWS account. You will configure and launch AFT from the AWS Control Tower management account.

**Step 2**: Create a new organizational unit for AFT (recommended)

We recommend that you create a separate OU in your AWS Organization, where you will deploy the AFT management account. Create an OU through your AWS Control Tower management account. For instructions on how to create an OU, refer to Create an organization in the AWS Organizations User Guide.

**Step 3**: Provision the AFT management account

AFT requires a separate AWS account to manage and orchestrate its own requests. From the AWS Control Tower management account that's associated with your AWS Control Tower landing zone, you'll provision this account for AFT.

To provision the AFT management account, see [Provisioning Account Factory Accounts With AWS Service Catalog](https://docs.aws.amazon.com/controltower/latest/userguide/provision-as-end-user.html). When specifying an OU, be sure to select the OU you created in Step 2. When specifying a name, use "AFT-Management".

Note: It can take up to 30 minutes for the account to be fully provisioned. Validate that you have access to the AFT management account.

**Step 4**: Ensure that the Terraform environment is available for deployment

This step assumes that you are experienced with Terraform, and that you have procedures in place for executing Terraform. AFT supports Terraform Version 0.15.x or later.

**Step 5**: Call the Account Factory for Terraform module to deploy AFT

The Account Factory for Terraform module must be called while you are authenticated with AdministratorAccess credentials in your AWS Control Tower management account.

AWS Control Tower, through the AWS Control Tower management account, vends a Terraform module that establishes all infrastructure necessary to orchestrate your AWS Control Tower account factory requests. You can view that module in the AFT repository.

Refer to the module’s README file for information about the input required to run the module and deploy AFT.

If you have established pipelines for managing Terraform in your environment, you can integrate this module into your existing workflow. Otherwise, run the module from any environment that is authenticated with the required credentials.

> Note: The AFT Terraform module does not manage a backend Terraform state. Be sure to preserve the Terraform state file that’s generated, after applying the module, or set up a Terraform backend using Amazon S3 and DynamoDB.

Certain input variables may contain sensitive values, such as a private ssh key or Terraform token. These values may be viewable as plain text in Terraform state file, depending on your deployment method. It is your responsibility to protect the Terraform state file, which may contain sensitive data. See the Terraform documentation

for more information.

> Note: Deploying AFT through the Terraform module requires several minutes. Initial deployment may require up to 30 minutes. As a best practice, use AWS Security Token Service (STS) credentials and ensure that the credentials have a timeout sufficient for a full deployment, because a timeout causes the deployment to fail. The minimum timeout for AWS STS credentials is 60 minutes or more. Alternatively, you can leverage any IAM user that has AdministratorAccess permissions in the AWS Control Tower management account.

## Next Steps:

Now that you have configured and deployed AWS Control Tower Account Factory for Terraform, follow the steps outlined in [Post-deployment steps](https://docs.aws.amazon.com/controltower/latest/userguide/aft-post-deployment.html) and [Provision accounts with AWS Control Tower Account Factory for Terraform](https://docs.aws.amazon.com/controltower/latest/userguide/taf-account-provisioning.html) to begin using your environment.

## Collection of Operational Metrics
As of version 1.6.0, AFT collects anonymous operational metrics to help AWS improve the quality and features of the solution. For more information, including how to disable this capability, please see the [documentation here](https://docs.aws.amazon.com/controltower/latest/userguide/aft-operational-metrics.html).


<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.2.0, < 2.0.0 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | >= 5.11.0, < 6.0.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | >= 5.11.0, < 6.0.0 |
| <a name="provider_local"></a> [local](#provider\_local) | n/a |

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_aft_account_provisioning_framework"></a> [aft\_account\_provisioning\_framework](#module\_aft\_account\_provisioning\_framework) | ./modules/aft-account-provisioning-framework | n/a |
| <a name="module_aft_account_request_framework"></a> [aft\_account\_request\_framework](#module\_aft\_account\_request\_framework) | ./modules/aft-account-request-framework | n/a |
| <a name="module_aft_backend"></a> [aft\_backend](#module\_aft\_backend) | ./modules/aft-backend | n/a |
| <a name="module_aft_code_repositories"></a> [aft\_code\_repositories](#module\_aft\_code\_repositories) | ./modules/aft-code-repositories | n/a |
| <a name="module_aft_customizations"></a> [aft\_customizations](#module\_aft\_customizations) | ./modules/aft-customizations | n/a |
| <a name="module_aft_feature_options"></a> [aft\_feature\_options](#module\_aft\_feature\_options) | ./modules/aft-feature-options | n/a |
| <a name="module_aft_iam_roles"></a> [aft\_iam\_roles](#module\_aft\_iam\_roles) | ./modules/aft-iam-roles | n/a |
| <a name="module_aft_lambda_layer"></a> [aft\_lambda\_layer](#module\_aft\_lambda\_layer) | ./modules/aft-lambda-layer | n/a |
| <a name="module_aft_ssm_parameters"></a> [aft\_ssm\_parameters](#module\_aft\_ssm\_parameters) | ./modules/aft-ssm-parameters | n/a |
| <a name="module_packaging"></a> [packaging](#module\_packaging) | ./modules/aft-archives | n/a |

## Resources

| Name | Type |
|------|------|
| [aws_partition.current](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/partition) | data source |
| [aws_service.home_region_validation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/service) | data source |
| [aws_ssm_parameters_by_path.servicecatalog_regional_data](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/ssm_parameters_by_path) | data source |
| [local_file.python_version](https://registry.terraform.io/providers/hashicorp/local/latest/docs/data-sources/file) | data source |
| [local_file.version](https://registry.terraform.io/providers/hashicorp/local/latest/docs/data-sources/file) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_account_customizations_repo_branch"></a> [account\_customizations\_repo\_branch](#input\_account\_customizations\_repo\_branch) | Branch to source account customizations repo from | `string` | `"main"` | no |
| <a name="input_account_customizations_repo_name"></a> [account\_customizations\_repo\_name](#input\_account\_customizations\_repo\_name) | Repository name for the account customizations files. For non-CodeCommit repos, name should be in the format of Org/Repo | `string` | `"aft-account-customizations"` | no |
| <a name="input_account_provisioning_customizations_repo_branch"></a> [account\_provisioning\_customizations\_repo\_branch](#input\_account\_provisioning\_customizations\_repo\_branch) | Branch to source account provisioning customization files | `string` | `"main"` | no |
| <a name="input_account_provisioning_customizations_repo_name"></a> [account\_provisioning\_customizations\_repo\_name](#input\_account\_provisioning\_customizations\_repo\_name) | Repository name for the account provisioning customizations files. For non-CodeCommit repos, name should be in the format of Org/Repo | `string` | `"aft-account-provisioning-customizations"` | no |
| <a name="input_account_request_repo_branch"></a> [account\_request\_repo\_branch](#input\_account\_request\_repo\_branch) | Branch to source account request repo from | `string` | `"main"` | no |
| <a name="input_account_request_repo_name"></a> [account\_request\_repo\_name](#input\_account\_request\_repo\_name) | Repository name for the account request files. For non-CodeCommit repos, name should be in the format of Org/Repo | `string` | `"aft-account-request"` | no |
| <a name="input_aft_backend_bucket_access_logs_object_expiration_days"></a> [aft\_backend\_bucket\_access\_logs\_object\_expiration\_days](#input\_aft\_backend\_bucket\_access\_logs\_object\_expiration\_days) | Amount of days to keep the objects stored in the access logs bucket for AFT backend buckets | `number` | `365` | no |
| <a name="input_aft_enable_vpc"></a> [aft\_enable\_vpc](#input\_aft\_enable\_vpc) | Flag turning use of VPC on/off for AFT | `bool` | `true` | no |
| <a name="input_aft_feature_cloudtrail_data_events"></a> [aft\_feature\_cloudtrail\_data\_events](#input\_aft\_feature\_cloudtrail\_data\_events) | Feature flag toggling CloudTrail data events on/off | `bool` | `false` | no |
| <a name="input_aft_feature_delete_default_vpcs_enabled"></a> [aft\_feature\_delete\_default\_vpcs\_enabled](#input\_aft\_feature\_delete\_default\_vpcs\_enabled) | Feature flag toggling deletion of default VPCs on/off | `bool` | `false` | no |
| <a name="input_aft_feature_enterprise_support"></a> [aft\_feature\_enterprise\_support](#input\_aft\_feature\_enterprise\_support) | Feature flag toggling Enterprise Support enrollment on/off | `bool` | `false` | no |
| <a name="input_aft_framework_repo_git_ref"></a> [aft\_framework\_repo\_git\_ref](#input\_aft\_framework\_repo\_git\_ref) | Git branch from which the AFT framework should be sourced from | `string` | `null` | no |
| <a name="input_aft_framework_repo_url"></a> [aft\_framework\_repo\_url](#input\_aft\_framework\_repo\_url) | Git repo URL where the AFT framework should be sourced from | `string` | `"https://github.com/aws-ia/terraform-aws-control_tower_account_factory.git"` | no |
| <a name="input_aft_management_account_id"></a> [aft\_management\_account\_id](#input\_aft\_management\_account\_id) | AFT Management Account ID | `string` | n/a | yes |
| <a name="input_aft_metrics_reporting"></a> [aft\_metrics\_reporting](#input\_aft\_metrics\_reporting) | Flag toggling reporting of operational metrics | `bool` | `true` | no |
| <a name="input_aft_vpc_cidr"></a> [aft\_vpc\_cidr](#input\_aft\_vpc\_cidr) | CIDR Block to allocate to the AFT VPC | `string` | `"192.168.0.0/22"` | no |
| <a name="input_aft_vpc_endpoints"></a> [aft\_vpc\_endpoints](#input\_aft\_vpc\_endpoints) | Flag turning VPC endpoints on/off for AFT VPC | `bool` | `true` | no |
| <a name="input_aft_vpc_private_subnet_01_cidr"></a> [aft\_vpc\_private\_subnet\_01\_cidr](#input\_aft\_vpc\_private\_subnet\_01\_cidr) | CIDR Block to allocate to the Private Subnet 01 | `string` | `"192.168.0.0/24"` | no |
| <a name="input_aft_vpc_private_subnet_02_cidr"></a> [aft\_vpc\_private\_subnet\_02\_cidr](#input\_aft\_vpc\_private\_subnet\_02\_cidr) | CIDR Block to allocate to the Private Subnet 02 | `string` | `"192.168.1.0/24"` | no |
| <a name="input_aft_vpc_public_subnet_01_cidr"></a> [aft\_vpc\_public\_subnet\_01\_cidr](#input\_aft\_vpc\_public\_subnet\_01\_cidr) | CIDR Block to allocate to the Public Subnet 01 | `string` | `"192.168.2.0/25"` | no |
| <a name="input_aft_vpc_public_subnet_02_cidr"></a> [aft\_vpc\_public\_subnet\_02\_cidr](#input\_aft\_vpc\_public\_subnet\_02\_cidr) | CIDR Block to allocate to the Public Subnet 02 | `string` | `"192.168.2.128/25"` | no |
| <a name="input_audit_account_id"></a> [audit\_account\_id](#input\_audit\_account\_id) | Audit Account Id | `string` | n/a | yes |
| <a name="input_backup_recovery_point_retention"></a> [backup\_recovery\_point\_retention](#input\_backup\_recovery\_point\_retention) | Number of days to keep backup recovery points in AFT DynamoDB tables. Default = Never Expire | `number` | `null` | no |
| <a name="input_cloudwatch_log_group_retention"></a> [cloudwatch\_log\_group\_retention](#input\_cloudwatch\_log\_group\_retention) | Amount of days to keep CloudWatch Log Groups for Lambda functions. 0 = Never Expire | `string` | `"0"` | no |
| <a name="input_concurrent_account_factory_actions"></a> [concurrent\_account\_factory\_actions](#input\_concurrent\_account\_factory\_actions) | Maximum number of accounts that can be provisioned in parallel. | `number` | `5` | no |
| <a name="input_ct_home_region"></a> [ct\_home\_region](#input\_ct\_home\_region) | The region from which this module will be executed. This MUST be the same region as Control Tower is deployed. | `string` | n/a | yes |
| <a name="input_ct_management_account_id"></a> [ct\_management\_account\_id](#input\_ct\_management\_account\_id) | Control Tower Management Account Id | `string` | n/a | yes |
| <a name="input_github_enterprise_url"></a> [github\_enterprise\_url](#input\_github\_enterprise\_url) | GitHub enterprise URL, if GitHub Enterprise is being used | `string` | `"null"` | no |
| <a name="input_gitlab_selfmanaged_url"></a> [gitlab\_selfmanaged\_url](#input\_gitlab\_selfmanaged\_url) | GitLab SelfManaged URL, if GitLab SelfManaged is being used | `string` | `"null"` | no |
| <a name="input_global_codebuild_timeout"></a> [global\_codebuild\_timeout](#input\_global\_codebuild\_timeout) | Codebuild build timeout | `number` | `60` | no |
| <a name="input_global_customizations_repo_branch"></a> [global\_customizations\_repo\_branch](#input\_global\_customizations\_repo\_branch) | Branch to source global customizations repo from | `string` | `"main"` | no |
| <a name="input_global_customizations_repo_name"></a> [global\_customizations\_repo\_name](#input\_global\_customizations\_repo\_name) | Repository name for the global customization files. For non-CodeCommit repos, name should be in the format of Org/Repo | `string` | `"aft-global-customizations"` | no |
| <a name="input_log_archive_account_id"></a> [log\_archive\_account\_id](#input\_log\_archive\_account\_id) | Log Archive Account Id | `string` | n/a | yes |
| <a name="input_log_archive_bucket_object_expiration_days"></a> [log\_archive\_bucket\_object\_expiration\_days](#input\_log\_archive\_bucket\_object\_expiration\_days) | Amount of days to keep the objects stored in the AFT logging bucket | `number` | `365` | no |
| <a name="input_maximum_concurrent_customizations"></a> [maximum\_concurrent\_customizations](#input\_maximum\_concurrent\_customizations) | Maximum number of customizations/pipelines to run at once | `number` | `5` | no |
| <a name="input_terraform_api_endpoint"></a> [terraform\_api\_endpoint](#input\_terraform\_api\_endpoint) | API Endpoint for Terraform. Must be in the format of https://xxx.xxx. | `string` | `"https://app.terraform.io/api/v2/"` | no |
| <a name="input_terraform_distribution"></a> [terraform\_distribution](#input\_terraform\_distribution) | Terraform distribution being used for AFT - valid values are oss, tfc, or tfe | `string` | `"oss"` | no |
| <a name="input_terraform_org_name"></a> [terraform\_org\_name](#input\_terraform\_org\_name) | Organization name for Terraform Cloud or Enterprise | `string` | `"null"` | no |
| <a name="input_terraform_token"></a> [terraform\_token](#input\_terraform\_token) | Terraform token for Cloud or Enterprise | `string` | `"null"` | no |
| <a name="input_terraform_version"></a> [terraform\_version](#input\_terraform\_version) | Terraform version being used for AFT | `string` | `"1.6.0"` | no |
| <a name="input_tf_backend_secondary_region"></a> [tf\_backend\_secondary\_region](#input\_tf\_backend\_secondary\_region) | AFT creates a backend for state tracking for its own state as well as OSS cases. The backend's primary region is the same as the AFT region, but this defines the secondary region to replicate to. | `string` | `""` | no |
| <a name="input_vcs_provider"></a> [vcs\_provider](#input\_vcs\_provider) | Customer VCS Provider - valid inputs are codecommit, bitbucket, github, githubenterprise, gitlab, or gitLab self-managed | `string` | `"codecommit"` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_account_customizations_repo_branch"></a> [account\_customizations\_repo\_branch](#output\_account\_customizations\_repo\_branch) | n/a |
| <a name="output_account_customizations_repo_name"></a> [account\_customizations\_repo\_name](#output\_account\_customizations\_repo\_name) | n/a |
| <a name="output_account_provisioning_customizations_repo_branch"></a> [account\_provisioning\_customizations\_repo\_branch](#output\_account\_provisioning\_customizations\_repo\_branch) | n/a |
| <a name="output_account_provisioning_customizations_repo_name"></a> [account\_provisioning\_customizations\_repo\_name](#output\_account\_provisioning\_customizations\_repo\_name) | n/a |
| <a name="output_account_request_repo_branch"></a> [account\_request\_repo\_branch](#output\_account\_request\_repo\_branch) | n/a |
| <a name="output_account_request_repo_name"></a> [account\_request\_repo\_name](#output\_account\_request\_repo\_name) | n/a |
| <a name="output_aft_feature_cloudtrail_data_events"></a> [aft\_feature\_cloudtrail\_data\_events](#output\_aft\_feature\_cloudtrail\_data\_events) | n/a |
| <a name="output_aft_feature_delete_default_vpcs_enabled"></a> [aft\_feature\_delete\_default\_vpcs\_enabled](#output\_aft\_feature\_delete\_default\_vpcs\_enabled) | n/a |
| <a name="output_aft_feature_enterprise_support"></a> [aft\_feature\_enterprise\_support](#output\_aft\_feature\_enterprise\_support) | n/a |
| <a name="output_aft_management_account_id"></a> [aft\_management\_account\_id](#output\_aft\_management\_account\_id) | n/a |
| <a name="output_aft_vpc_cidr"></a> [aft\_vpc\_cidr](#output\_aft\_vpc\_cidr) | n/a |
| <a name="output_aft_vpc_private_subnet_01_cidr"></a> [aft\_vpc\_private\_subnet\_01\_cidr](#output\_aft\_vpc\_private\_subnet\_01\_cidr) | n/a |
| <a name="output_aft_vpc_private_subnet_02_cidr"></a> [aft\_vpc\_private\_subnet\_02\_cidr](#output\_aft\_vpc\_private\_subnet\_02\_cidr) | n/a |
| <a name="output_aft_vpc_public_subnet_01_cidr"></a> [aft\_vpc\_public\_subnet\_01\_cidr](#output\_aft\_vpc\_public\_subnet\_01\_cidr) | n/a |
| <a name="output_aft_vpc_public_subnet_02_cidr"></a> [aft\_vpc\_public\_subnet\_02\_cidr](#output\_aft\_vpc\_public\_subnet\_02\_cidr) | n/a |
| <a name="output_audit_account_id"></a> [audit\_account\_id](#output\_audit\_account\_id) | n/a |
| <a name="output_backup_recovery_point_retention"></a> [backup\_recovery\_point\_retention](#output\_backup\_recovery\_point\_retention) | n/a |
| <a name="output_cloudwatch_log_group_retention"></a> [cloudwatch\_log\_group\_retention](#output\_cloudwatch\_log\_group\_retention) | n/a |
| <a name="output_ct_home_region"></a> [ct\_home\_region](#output\_ct\_home\_region) | n/a |
| <a name="output_ct_management_account_id"></a> [ct\_management\_account\_id](#output\_ct\_management\_account\_id) | n/a |
| <a name="output_github_enterprise_url"></a> [github\_enterprise\_url](#output\_github\_enterprise\_url) | n/a |
| <a name="output_gitlab_selfmanaged_url"></a> [gitlab\_selfmanaged\_url](#output\_gitlab\_selfmanaged\_url) | n/a |
| <a name="output_global_customizations_repo_branch"></a> [global\_customizations\_repo\_branch](#output\_global\_customizations\_repo\_branch) | n/a |
| <a name="output_global_customizations_repo_name"></a> [global\_customizations\_repo\_name](#output\_global\_customizations\_repo\_name) | n/a |
| <a name="output_log_archive_account_id"></a> [log\_archive\_account\_id](#output\_log\_archive\_account\_id) | n/a |
| <a name="output_maximum_concurrent_customizations"></a> [maximum\_concurrent\_customizations](#output\_maximum\_concurrent\_customizations) | n/a |
| <a name="output_terraform_api_endpoint"></a> [terraform\_api\_endpoint](#output\_terraform\_api\_endpoint) | n/a |
| <a name="output_terraform_distribution"></a> [terraform\_distribution](#output\_terraform\_distribution) | n/a |
| <a name="output_terraform_org_name"></a> [terraform\_org\_name](#output\_terraform\_org\_name) | n/a |
| <a name="output_terraform_version"></a> [terraform\_version](#output\_terraform\_version) | n/a |
| <a name="output_tf_backend_secondary_region"></a> [tf\_backend\_secondary\_region](#output\_tf\_backend\_secondary\_region) | n/a |
| <a name="output_vcs_provider"></a> [vcs\_provider](#output\_vcs\_provider) | n/a |
<!-- END_TF_DOCS -->
