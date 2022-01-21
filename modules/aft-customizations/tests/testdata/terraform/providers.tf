provider "aws" {
  region                  = "us-west-2"
  shared_credentials_file = "~/.aws/credentials"
  profile                 = "aft-management"
  default_tags {
    tags = {
      "aft:terraform:module-name" = "global-customizations"
      managed_by                  = "AFT"
    }
  }
}
