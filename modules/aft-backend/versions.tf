terraform {
  required_version = ">= 0.15.1"

  required_providers {
    aws = {
      source                = "hashicorp/aws"
      version               = ">= 3.72"
      configuration_aliases = [aws.primary_region, aws.secondary_region]
    }
  }
}
