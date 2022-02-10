# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#
output "codestar_connection_arn" {
  value = lookup(local.connection_arn, var.vcs_provider)
}
