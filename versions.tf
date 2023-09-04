# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
terraform {
  required_version = ">= 0.15.1, < 2.0.0"

  required_providers {
    aws = {
      source                = "hashicorp/aws"
      version               = ">= 4.27.0, < 6.0.0"
      configuration_aliases = [aws.ct_management, aws.log_archive, aws.audit, aws.aft_management, aws.tf_backend_secondary_region]
    }
  }
}
