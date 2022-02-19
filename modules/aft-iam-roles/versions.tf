# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
terraform {
  required_version = ">= 0.15.1"

  required_providers {
    aws = {
      source                = "hashicorp/aws"
      version               = ">= 3.72, < 4.0.0"
      configuration_aliases = [aws.ct_management, aws.log_archive, aws.audit, aws.aft_management]
    }
  }
}
