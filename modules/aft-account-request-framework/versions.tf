# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
terraform {
  required_version = ">= 1.6.1, < 2.0.0"

  required_providers {
    aws = {
      source = "hashicorp/aws"
      # >= 6.0.0 required for per-resource `region` support, used by
      # aws_ssm_service_setting.block_public_sharing
      version               = ">= 6.0.0, < 7.0.0"
      configuration_aliases = [aws.ct_management]
    }
  }
}
