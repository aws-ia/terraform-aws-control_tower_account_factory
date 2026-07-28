# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Blocks public sharing of SSM documents in the AFT management account. The
# setting is account-level but evaluated per region, so it is managed in every
# Control Tower governed region. Addresses Security Hub control SSM.7 - "SSM
# documents should have the block public sharing setting enabled".
resource "aws_ssm_service_setting" "block_public_sharing" {
  for_each      = var.create_ssm_block_public_sharing ? toset(var.ssm_block_public_sharing_regions) : toset([])
  region        = each.value
  setting_id    = "/ssm/documents/console/public-sharing-permission"
  setting_value = "Disable"
}
