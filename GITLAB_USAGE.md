# Using AWS Control Tower Account Factory for Terraform with GitLab

This repository contains the official AWS Control Tower Account Factory for Terraform (AFT) module, configured for use with GitLab CI/CD.

## Overview

This is an **exact clone** of the official AWS AFT repository at:
https://github.com/aws-ia/terraform-aws-control_tower_account_factory

## Repository Structure

```
terraform-aws-control_tower_account_factory/
├── .gitlab-ci.yml              # GitLab CI/CD configuration
├── main.tf                     # Main AFT module
├── variables.tf                # Input variables
├── outputs.tf                  # Module outputs
├── versions.tf                 # Provider requirements
├── examples/                   # Example configurations
│   ├── gitlab+tf_oss/         # GitLab + Terraform OSS example
│   └── ...                    # Other VCS examples
├── modules/                    # AFT sub-modules
└── src/                       # Python Lambda sources
```

## Prerequisites

### AWS Requirements
- AWS Control Tower deployed and configured
- Control Tower Management Account with AdministratorAccess
- AFT Management Account (separate from CT Management Account)
- Log Archive and Audit Accounts (created by Control Tower)

### GitLab Requirements
- GitLab project with CI/CD enabled
- GitLab Runner with appropriate permissions
- AWS credentials configured in GitLab CI/CD variables

## Setup Instructions

### 1. Clone or Fork This Repository

This repository is an exact clone of the official AWS AFT module. You can:

- **Fork this repository** in GitLab
- **Clone and push** to your own GitLab project

### 2. Configure GitLab CI/CD Variables

Set the following variables in your GitLab project settings:

| Variable Name | Description | Type |
|---------------|-------------|------|
| `AWS_ACCESS_KEY_ID` | AWS access key | Variable |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | Variable (masked) |
| `AWS_DEFAULT_REGION` | AWS region for AFT | Variable |
| `TF_VAR_ct_management_account_id` | Control Tower management account ID | Variable |
| `TF_VAR_log_archive_account_id` | Log archive account ID | Variable |
| `TF_VAR_audit_account_id` | Audit account ID | Variable |
| `TF_VAR_aft_management_account_id` | AFT management account ID | Variable |

### 3. Create Your AFT Configuration

Create a `terraform.tfvars` file with your specific configuration:

```hcl
# Control Tower Configuration
ct_management_account_id  = "123456789012"
log_archive_account_id    = "123456789013"
audit_account_id          = "123456789014"
aft_management_account_id = "123456789015"
ct_home_region           = "us-east-1"

# GitLab Configuration
vcs_provider = "gitlab"
account_request_repo_name                      = "your-org/aft-account-request"
global_customizations_repo_name                = "your-org/aft-global-customizations"
account_customizations_repo_name               = "your-org/aft-account-customizations"
account_provisioning_customizations_repo_name = "your-org/aft-account-provisioning-customizations"

# Terraform Configuration
terraform_version      = "1.6.0"
terraform_distribution = "oss"

# Feature Configuration
aft_feature_delete_default_vpcs_enabled = true
aft_feature_cloudtrail_data_events      = false
aft_feature_enterprise_support          = false
```

### 4. Set Up Backend Configuration

Configure your Terraform backend for state management:

```hcl
terraform {
  backend "s3" {
    bucket         = "your-terraform-state-bucket"
    key            = "aft/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-state-lock"
    encrypt        = true
  }
}
```

### 5. Deploy AFT

#### Option A: GitLab CI/CD (Recommended)

1. Push your configuration to the `main` branch
2. The pipeline will automatically validate your configuration
3. Manually trigger the `deploy-production` job to deploy AFT

#### Option B: Local Deployment

```bash
terraform init
terraform plan -var-file="terraform.tfvars"
terraform apply -var-file="terraform.tfvars"
```

## GitLab CI/CD Pipeline

The included `.gitlab-ci.yml` provides:

### Validation Stage
- **Terraform validation**: Syntax and configuration checks
- **Python validation**: Code formatting and linting
- **Security scanning**: Infrastructure security analysis with tfsec

### Testing Stage
- **Multi-version testing**: Tests against multiple Terraform versions
- **Example testing**: Validates all example configurations
- **Documentation generation**: Automated docs with terraform-docs

### Deployment Stage
- **Staging deployment**: Manual deployment to staging environment
- **Production deployment**: Manual deployment to production (main branch only)

## AFT Repository Structure

After AFT deployment, you'll need to create these repositories:

### 1. AFT Account Request Repository
Contains Terraform files that define account provisioning requests.

**Example structure:**
```
aft-account-request/
└── terraform/
    ├── sandbox-account.tf
    └── production-account.tf
```

### 2. AFT Global Customizations Repository
Contains Terraform configurations applied to ALL accounts.

**Example structure:**
```
aft-global-customizations/
└── terraform/
    ├── main.tf
    ├── variables.tf
    └── cloudtrail.tf
```

### 3. AFT Account Customizations Repository
Contains account-specific Terraform configurations.

**Example structure:**
```
aft-account-customizations/
├── 123456789012/
│   └── terraform/
│       └── main.tf
└── 123456789013/
    └── terraform/
        └── main.tf
```

### 4. AFT Account Provisioning Customizations Repository
Contains custom logic for account provisioning process.

**Example structure:**
```
aft-account-provisioning-customizations/
└── terraform/
    ├── main.tf
    └── custom-roles.tf
```

## Usage Examples

See the `examples/` directory for complete configuration examples:

- `examples/gitlab+tf_oss/` - GitLab with Terraform OSS
- `examples/codecommit+tf_oss/` - AWS CodeCommit with Terraform OSS
- `examples/github+tf_oss/` - GitHub with Terraform OSS

## Monitoring and Troubleshooting

### GitLab Pipeline Monitoring
- Monitor pipeline status in GitLab CI/CD interface
- Check job logs for detailed error information
- Use artifacts to download generated reports

### AFT Monitoring in AWS
- **Step Functions**: Monitor account provisioning workflows
- **CodePipeline**: Track customization deployments
- **CloudWatch Logs**: View detailed AFT execution logs

### Common Issues
1. **Permission errors**: Ensure AWS credentials have sufficient permissions
2. **State lock issues**: Check S3 bucket and DynamoDB table access
3. **Validation failures**: Review Terraform syntax and required variables

## Security Considerations

- Store sensitive variables (AWS credentials, tokens) as masked variables in GitLab
- Use IAM roles with minimal required permissions
- Enable S3 bucket encryption for Terraform state
- Regular rotation of access keys and tokens
- Enable GitLab CI/CD security scanning

## Contributing

This repository mirrors the official AWS AFT module. For contributions to the AFT module itself, please contribute to the upstream repository at:
https://github.com/aws-ia/terraform-aws-control_tower_account_factory

For GitLab-specific improvements, create issues or merge requests in this repository.

## Support

- **AWS AFT Documentation**: https://docs.aws.amazon.com/controltower/latest/userguide/aft-overview.html
- **Official AFT Repository**: https://github.com/aws-ia/terraform-aws-control_tower_account_factory
- **GitLab CI/CD Documentation**: https://docs.gitlab.com/ee/ci/

## License

This project maintains the same license as the original AWS AFT module. See [LICENSE](LICENSE) for details. 