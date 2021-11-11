module "aft" {
  source = ""
  # Required Vars
  ct_management_account_id    = "111122223333"
  log_archive_account_id      = "444455556666"
  audit_account_id            = "123456789012"
  aft_management_account_id   = "777788889999"
  ct_home_region              = "us-east-1"
  tf_backend_secondary_region = "us-west-2"
}