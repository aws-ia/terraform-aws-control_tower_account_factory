# Mondelez Modifications to AFT
## Application/Network Request Table
### AFT Enhancement Request
IAM permissions for the ct-aft-codebuild-account-request-role should be able to be supplemented by user input.
### Purpose
To restrict a grouping of accounts to a specific application name that cannot be reused.
### Modifications
- [main.tf](main.tf) passing of value between modules
- [modules/aft-account-request-framework/ddb_custom.tf](modules/aft-account-request-framework/ddb_custom.tf) addition of the DynamoDB table
- [modules/aft-account-request-framework/outputs_custom.tf](modules/aft-account-request-framework/outputs_custom.tf) addition of an output to pass the table name
- [modules/aft-code-repositories/variables.tf](modules/aft-code-repositories/variables.tf) adding a variable to pass the table name to iam
- [modules/aft-code-repositories/iam.tf](modules/aft-code-repositories/iam.tf) passing the table name to an iam template
- [modules/aft-code-repositories/iam/role-policies/ct_aft_codebuild_policy.tpl](modules/aft-code-repositories/iam/role-policies/ct_aft_codebuild_policy.tpl) adding the table to the iam template
## Terraformrc for Private Modules
### AFT Enhancement Request
Commands should be able to be added at the beginning/end of each AFT CodeBuild project build phase.
### Purpose
To allow private module use within the AFT Terraform CodeBuild projects.
### Modifications
- [modules/aft-code-repositories/buildspecs/ct-aft-account-provisioning-customizations.yml](modules/aft-code-repositories/buildspecs/ct-aft-account-provisioning-customizations.yml) retrieve .terraformrc from SSM and save to ~/.terraformrc
- [modules/aft-customizations/buildspecs/aft-account-customizations-terraform.yml](modules/aft-customizations/buildspecs/aft-account-customizations-terraform.yml) retrieve .terraformrc from SSM and save to ~/.terraformrc
- [modules/aft-customizations/buildspecs/aft-global-customizations-terraform.yml](modules/aft-customizations/buildspecs/aft-global-customizations-terraform.yml) retrieve .terraformrc from SSM and save to ~/.terraformrc
- [modules/aft-ssm-parameters/secrets/039570753310/spacelift_terraformrc.enc](modules/aft-ssm-parameters/secrets/039570753310/spacelift_terraformrc.enc) added encrypted .terraformrc to repo
- [modules/aft-ssm-parameters/data_custom.tf](modules/aft-ssm-parameters/data.tf) added decryption for the .terraformrc
- [modules/aft-ssm-parameters/ssm_secrets_custom.tf](modules/aft-ssm-parameters/ssm_secrets.tf) added the SSM secret

## Secrets
### Purpose
To enable AFT to leverage custom secrets.
### Modifications
- [data_custom.tf](data.tf) decryption of the secrets
- [ssm_custom.tf](ssm_custom.tf) added the SSM secrets
