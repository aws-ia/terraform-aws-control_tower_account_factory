# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
output "codeconnections_connection_arn" {
  value = lookup(local.connection_arn, var.vcs_provider)
}
