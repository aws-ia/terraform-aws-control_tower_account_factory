terraform {
  required_version = ">= 0.15.1"

  required_providers {
    aws = {
      source                = "hashicorp/aws"
      version               = ">= 3.72"
      configuration_aliases = [aws.ct_management, aws.log_archive, aws.audit, aws.aft_management, aws.tf_backend_secondary_region]
    }
  }
}
