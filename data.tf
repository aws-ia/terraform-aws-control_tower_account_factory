# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# data "local_file" "version" {
#   filename = "${path.module}/VERSION"
# }
# 
# data "local_file" "python_version" {
#   filename = "${path.module}/PYTHON_VERSION"
# }

data "aws_partition" "current" {}
