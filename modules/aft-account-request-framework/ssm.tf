# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Blocks public sharing of SSM documents in the AFT management account for the
# Control Tower home region. Addresses Security Hub control SSM.7 - "SSM
# documents should not be public".
resource "aws_ssm_service_setting" "block_public_sharing" {
  count         = var.create_ssm_block_public_sharing ? 1 : 0
  setting_id    = "/ssm/documents/console/public-sharing-permission"
  setting_value = "Disable"
}
