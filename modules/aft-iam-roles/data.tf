# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
data "aws_caller_identity" "aft_management" {
  provider = aws.aft_management
}

data "aws_partition" "current" {}
