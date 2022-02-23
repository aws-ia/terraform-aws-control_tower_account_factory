module "network_account" {
  source = "./modules/aft-account-request"

  control_tower_parameters = {
    AccountEmail = "network-account@gft-aws.com"
    AccountName  = "network-account"
    # Syntax for top-level OU
    ManagedOrganizationalUnit = "Infrastructure"
    # Syntax for nested OU
    # ManagedOrganizationalUnit = "Network (ou-sa0f-8eu78feo)"
    SSOUserEmail     = "network-account@gft-aws.com"
    SSOUserFirstName = "Network"
    SSOUserLastName  = "Acc"
  }

  account_tags = {
    "ABC:Owner"       = "network-account@gft-aws.com"
    "ABC:Division"    = "Infrastructure"
    "ABC:Environment" = "Dev"
    "ABC:CostCenter"  = "123456"
    "ABC:Vended"      = "true"
    "ABC:DivCode"     = "102"
    "ABC:BUCode"      = "ABC003"
    "ABC:Project"     = "123456"
  }

  change_management_parameters = {
    change_requested_by = "Network team"
    change_reason       = "Creating new account"
  }

  custom_fields = {
    custom1 = "a"
    custom2 = "b"
  }

  account_customizations_name = "network_customizations"
}