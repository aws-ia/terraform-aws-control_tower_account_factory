# AWS Control Tower Account Factory for Terraform 
AWS Control Tower Account Factory for Terraform (AFT) is an AWS solution that enables you to leverage Terraform Infrastructure as Code (IaC) to provision and customize AWS Control Tower managed accounts.

## Getting started

This getting started guide is meant for administrators of AWS Control Tower environments who wish to set up Account Factory for Terraform (AFT) for their environment. At the end of the guide, you will have an Account Factory for Terraform environment set up in a new dedicated AFT management account.

> **Please Note:** The deployment of the solution is via a Terraform Module. Details on Terraform Modules is available [here](https://www.terraform.io/docs/language/modules/index.html) if you are inexperienced with these. At release, you are recommended to reference the modules from the GitHub source and not clone it. This will allow you to control and consume updates to the module(s) as they are made available.

## Prerequisites

AFT has prerequisites for installation, as well as execution. This guide assumes you have access to create and interact with each of the following resources in order to deploy the AFT solution:

* A valid AWS Control Tower landing zone.
* Supported Git-based repositories for account requests, account pre-customizations, global, and account customization configurations with programmatic access to each repository.
* An execution environment in which to run the Terraform module which installs AFT.

## Configure and launch your AWS Control Tower Account Factory for Terraform

**Step 1: Launch Control Tower setup
**

Before launching AFT, ensure a valid AWS Control Tower landing zone has been established in your AWS account. This account will be referred to as the AFT Control Tower management account.

**Step 2: Create new Organizational Unit**

AFT expects a dedicated OU to exist in your AWS Organization where the AFT Management account will be deployed. Create an OU through your AFT Control Tower management account. For guide on how to create an OU, refer to [Creating an OU](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_ous.html#create_ou).

**Step 3: Launch the AFT management account**

AFT uses a separate account to manage and orchestrate its own requests, separated from your AFT Control Tower management account. This establishes a clear boundary so that there are no conflicts between accounts managed by the core AWS Control Tower service and accounts managed by AFT.

To launch the AFT Management account, see [Provision Account Factory Accounts With AWS Service Catalog](https://docs.aws.amazon.com/controltower/latest/userguide/account-factory.html#provision-as-end-user). When specifying an OU, be sure to select the OU you created in **Step 2**. When specifying a name, use “AFT-Management”. It can take up to 30 minutes for the account to be fully provisioned. Validate access to the AFT management account.

**Step 4: Ensure Terraform is installed on your local machine
**

You are expected to already be experienced in Terraform and will have procedures in place for executing Terraform. AFT currently supports Terraform Version 0.15.x.

**Step 5: Call the Account Factory for Terraform module which will deploy the solution
**


> When deploying AFT via the Terraform Module it will run for several minutes and initial deployment can take up to 30 minutes. Ensure the STS credentials you are using have a timeout which will allow for a full deployment as a timeout will most likely cause the deployment to fail mid-stream.



AWS Control Tower for AFT Control Tower management account vends a Terraform module that establishes all infrastructure necessary to orchestrate your account factory requests. That module can be found here <TODO: provide link to open source repo>. Refer to the module’s README.md for information about inputs needed to run the module and deploy AFT solution.

The Account Factory for Terraform module **expects to be run while authenticated with Administrator privileges in your AFT Control Tower management account**. If you have established pipelines for managing Terraform in your environment, integrate this module into your existing workflow where desired. Otherwise, you can run the module from any environment that is authenticated with the required credentials.

Note: The AWS AFT Control Tower module does not manage a backend Terraform state. Be sure to preserve the [Terraform state file](https://www.terraform.io/docs/language/state/index.html) generated after applying the module, or [set up a Terraform backend using S3 and DynamoDB](https://www.terraform.io/docs/language/settings/backends/s3.html).

TODO Call out Sensitive Values in State — customer is responsible for protecting state file.

**Step 6: (Optional) Accept CodeStar Connections with your desired VCS**

If using a third-party version control system, AFT will establish CodeStar Connections. You can go to [AWS CodeStar Connections documentation](https://docs.aws.amazon.com/dtconsole/latest/userguide/connections-create.html) to read more on CodeStar Connections.

**Note that the initial step of establishing the connection has been accomplished by AFT.**

**Step 7: Populate each repository**

AFT requires that you manage four repositories:

1. **Account Requests** - This repository tracks which accounts are recognized by AFT.
2. **AFT Account Provisioning Customizations** - This repository manages customizations that should be applied to all accounts created by and managed with AFT prior to Global Customizations stage.
3. **Global Customizations** - This repository manages customizations that should be applied to all accounts created by and managed with Account Factory for Terraform.
4. **Account Customizations** - This repository manages customizations that should only be applied to specific accounts created by and managed with Account Factory for Terraform.

AFT expects each of these repositories to follow a specific directory structure. Templates with which to populate your repositories and instructions for how to populate those templates can be found in the documentation for the Account Factory for Terraform module.

**Step 8: Grant access to AWS Control Tower Account Factory Portfolio**

AFT requires access to AWS Control Tower Account Factory Portfolio in AWS Service Catalog in AFT Control Tower management account in order to process the account provisioning requests. To do so, grant access to AWSAFTExecution role to AWS Control Tower Account Factory Portfolio. See https://docs.aws.amazon.com/servicecatalog/latest/adminguide/catalogs_portfolios_users.html for instructions on how to grant access to AWS Service Catalog portfolios.


## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 0.15.0 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | >= 3.15 |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_account_customizations_repo_branch"></a> [account\_customizations\_repo\_branch](#input\_account\_customizations\_repo\_branch) | Branch to source account customizations repo from | `string` | `"main"` | no |
| <a name="input_account_customizations_repo_name"></a> [account\_customizations\_repo\_name](#input\_account\_customizations\_repo\_name) | Repository name for the account customizations files. For non-CodeCommit repos, name should be in the format of Org/Repo | `string` | `"aft-account-customizations"` | no |
| <a name="input_account_provisioning_customizations_repo_branch"></a> [account\_provisioning\_customizations\_repo\_branch](#input\_account\_provisioning\_customizations\_repo\_branch) | Branch to source account provisioning customization files | `string` | `"main"` | no |
| <a name="input_account_provisioning_customizations_repo_name"></a> [account\_provisioning\_customizations\_repo\_name](#input\_account\_provisioning\_customizations\_repo\_name) | Repository name for the account provisioning customizations files. For non-CodeCommit repos, name should be in the format of Org/Repo | `string` | `"aft-account-provisioning-customizations"` | no |
| <a name="input_account_request_repo_branch"></a> [account\_request\_repo\_branch](#input\_account\_request\_repo\_branch) | Branch to source account request repo from | `string` | `"main"` | no |
| <a name="input_account_request_repo_name"></a> [account\_request\_repo\_name](#input\_account\_request\_repo\_name) | Repository name for the account request files. For non-CodeCommit repos, name should be in the format of Org/Repo | `string` | `"aft-account-request"` | no |
| <a name="input_aft_feature_cloudtrail_data_events"></a> [aft\_feature\_cloudtrail\_data\_events](#input\_aft\_feature\_cloudtrail\_data\_events) | Feature flag toggling CloudTrail data events on/off | `bool` | `false` | no |
| <a name="input_aft_feature_delete_default_vpcs_enabled"></a> [aft\_feature\_delete\_default\_vpcs\_enabled](#input\_aft\_feature\_delete\_default\_vpcs\_enabled) | Feature flag toggling deletion of default VPCs on/off | `bool` | `false` | no |
| <a name="input_aft_feature_enterprise_support"></a> [aft\_feature\_enterprise\_support](#input\_aft\_feature\_enterprise\_support) | Feature flag toggling Enterprise Support enrollment on/off | `bool` | `false` | no |
| <a name="input_aft_framework_repo_git_ref"></a> [aft\_framework\_repo\_git\_ref](#input\_aft\_framework\_repo\_git\_ref) | Git branch from which the AFT framework should be sourced from | `string` | `"main"` | no |
| <a name="input_aft_framework_repo_url"></a> [aft\_framework\_repo\_url](#input\_aft\_framework\_repo\_url) | Git repo URL where the AFT framework should be sourced from | `string` | `"TBD"` | no |
| <a name="input_aft_management_account_id"></a> [aft\_management\_account\_id](#input\_aft\_management\_account\_id) | AFT Management Account ID | `string` | n/a | yes |
| <a name="input_aft_vpc_cidr"></a> [aft\_vpc\_cidr](#input\_aft\_vpc\_cidr) | CIDR Block to allocate to the AFT VPC | `string` | `"192.168.0.0/22"` | no |
| <a name="input_aft_vpc_private_subnet_01_cidr"></a> [aft\_vpc\_private\_subnet\_01\_cidr](#input\_aft\_vpc\_private\_subnet\_01\_cidr) | CIDR Block to allocate to the Private Subnet 01 | `string` | `"192.168.0.0/24"` | no |
| <a name="input_aft_vpc_private_subnet_02_cidr"></a> [aft\_vpc\_private\_subnet\_02\_cidr](#input\_aft\_vpc\_private\_subnet\_02\_cidr) | CIDR Block to allocate to the Private Subnet 02 | `string` | `"192.168.1.0/24"` | no |
| <a name="input_aft_vpc_public_subnet_01_cidr"></a> [aft\_vpc\_public\_subnet\_01\_cidr](#input\_aft\_vpc\_public\_subnet\_01\_cidr) | CIDR Block to allocate to the Public Subnet 01 | `string` | `"192.168.2.0/25"` | no |
| <a name="input_aft_vpc_public_subnet_02_cidr"></a> [aft\_vpc\_public\_subnet\_02\_cidr](#input\_aft\_vpc\_public\_subnet\_02\_cidr) | CIDR Block to allocate to the Public Subnet 02 | `string` | `"192.168.2.128/25"` | no |
| <a name="input_audit_account_id"></a> [audit\_account\_id](#input\_audit\_account\_id) | Audit Account Id | `string` | n/a | yes |
| <a name="input_cloudwatch_log_group_retention"></a> [cloudwatch\_log\_group\_retention](#input\_cloudwatch\_log\_group\_retention) | Amount of days to keep CloudWatch Log Groups for Lambda functions. 0 = Never Expire | `string` | `"0"` | no |
| <a name="input_ct_home_region"></a> [ct\_home\_region](#input\_ct\_home\_region) | The region from which this module will be executed. This MUST be the same region as Control Tower is deployed. | `string` | n/a | yes |
| <a name="input_ct_management_account_id"></a> [ct\_management\_account\_id](#input\_ct\_management\_account\_id) | Control Tower Management Account Id | `string` | n/a | yes |
| <a name="input_github_enterprise_url"></a> [github\_enterprise\_url](#input\_github\_enterprise\_url) | GitHub enterprise URL, if GitHub Enterprise is being used | `string` | `"null"` | no |
| <a name="input_global_customizations_repo_branch"></a> [global\_customizations\_repo\_branch](#input\_global\_customizations\_repo\_branch) | Branch to source global customizations repo from | `string` | `"main"` | no |
| <a name="input_global_customizations_repo_name"></a> [global\_customizations\_repo\_name](#input\_global\_customizations\_repo\_name) | Repository name for the global customization files. For non-CodeCommit repos, name should be in the format of Org/Repo | `string` | `"aft-global-customizations"` | no |
| <a name="input_log_archive_account_id"></a> [log\_archive\_account\_id](#input\_log\_archive\_account\_id) | Log Archive Account Id | `string` | n/a | yes |
| <a name="input_maximum_concurrent_customizations"></a> [maximum\_concurrent\_customizations](#input\_maximum\_concurrent\_customizations) | Maximum number of customizations/pipelines to run at once | `number` | `5` | no |
| <a name="input_tf_backend_secondary_region"></a> [s3\_backend\_secondary\_region](#input\_tf\_backend\_secondary\_region) | AFT creates a backend for state tracking for its own state as well as OSS cases. The backend's primary region is the same as the AFT region, but this defines the secondary region to replicate to. | `string` | `"us-west-2"` | no |
| <a name="input_terraform_api_endpoint"></a> [terraform\_api\_endpoint](#input\_terraform\_api\_endpoint) | API Endpoint for Terraform. Must be in the format of https://xxx.xxx. | `string` | `"https://app.terraform.io/api/v2/"` | no |
| <a name="input_terraform_distribution"></a> [terraform\_distribution](#input\_terraform\_distribution) | Terraform distribution being used for AFT - valid values are oss, tfc, or tfe | `string` | `"oss"` | no |
| <a name="input_terraform_org_name"></a> [terraform\_org\_name](#input\_terraform\_org\_name) | Organization name for Terraform Cloud or Enterprise | `string` | `"null"` | no |
| <a name="input_terraform_token"></a> [terraform\_token](#input\_terraform\_token) | Terraform token for Cloud or Enterprise | `string` | `"null"` | no |
| <a name="input_terraform_version"></a> [terraform\_version](#input\_terraform\_version) | Terraform version being used for AFT | `string` | `"0.15.5"` | no |
| <a name="input_vcs_provider"></a> [vcs\_provider](#input\_vcs\_provider) | Customer VCS Provider - valid inputs are codecommit, bitbucket, github, or githubenterprise | `string` | `"codecommit"` | no |

