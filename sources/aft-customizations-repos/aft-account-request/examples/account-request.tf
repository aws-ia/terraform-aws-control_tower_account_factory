module "sandbox_account_01" {
  source = "./modules/aft-account-request"

  create_customizations = true

  control_tower_parameters = {
    AccountEmail              = "john.doe@amazon.com"
    AccountName               = "sandbox-account-01"
    ManagedOrganizationalUnit = "Sandbox"
    SSOUserEmail              = "john.doe@amazon.com"
    SSOUserFirstName          = "John"
    SSOUserLastName           = "Doe"
  }

  account_tags = {
    "ABC:Owner"       = "john.doe@amazon.com"
    "ABC:Division"    = "ENT"
    "ABC:Environment" = "Dev"
    "ABC:CostCenter"  = "123456"
    "ABC:Vended"      = "true"
    "ABC:DivCode"     = "102"
    "ABC:BUCode"      = "ABC003"
    "ABC:Project"     = "123456"
  }

  change_management_parameters = {
    change_requested_by = "John Doe"
    change_reason       = "testing the account vending process"
  }

  custom_fields = {
    custom1 = "a"
    custom2 = "b"
  }

  account_customizations_name = "sandbox-customizations"
}
