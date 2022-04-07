# Mondelez Modifications to AFT
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
