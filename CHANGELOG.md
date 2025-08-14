# Support for Multiple Account Customizations per Account

Previously, the `aft-account-customizations` pipeline expected a single value for the account customization.

This made it difficult to combine customizations for accounts that serve more than one purpose. AFT's recommendation was to create a separate account customization for each account type, and then reference a combination of modules in each customization, per [https://github.com/aws-ia/terraform-aws-control_tower_account_factory/issues/458](this Issue).

An example of that approach is here:
```hcl
module "developer_customizations" {
  source = "../../modules/development"
  providers = {
    aws = aws
  }
}

module "security_customizations" {
  source = "../../modules/security"
  providers = {
    aws = aws
  }
}
```

The problem with this approach is that it does not scale particularly well. Many customers have dozens to hundreds of accounts which may each need slightly different functionality. Maintaining account customizations for each is frustrating.

Now, however, with this change, you can now specify multiple values for account customizations in your `aft-account-request` pipeline, and AFT's account customizations pipeline will deploy each of them sequentially in the order specified.

For example, to deploy the development and security modules referenced above, you would create the individual `DEVELOPMENT` and `SECURITY` account customizations in `aft-account-customizations`, and then in your `aft-account-request` repository, reference both customizations, like so:
```hcl
module "web_dev_account" {
  source = "./modules/aft-account-request"

  control_tower_parameters = {
    AccountEmail              = "aws+web-dev@test.lab"
    AccountName               = "web-dev"
    ManagedOrganizationalUnit = "Development (ou-1234-12341234)"
    SSOUserEmail              = "aws+web-dev@test.lab"
    SSOUserFirstName          = "Web"
    SSOUserLastName           = "Dev"
  }

  account_customizations_name = "DEVELOPMENT,SECURITY"
}
```

Now, all I need to do is create a comma-delimited string of customizations in my account request and re-run the customizations pipeline. Both account customizations will be applied.

## Edge Cases as FAQs

- Q. What happens if I want to remove an account customization from my list?
    - A. If an account customization is removed from the list of account customizations, that customization will be destroyed prior to the remaining customizations being applied. This `destroy` logic also applies if the name of a customization changes.