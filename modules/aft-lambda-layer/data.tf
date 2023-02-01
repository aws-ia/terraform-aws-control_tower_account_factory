# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
data "aws_partition" "current" {}

data "aws_caller_identity" "session" {}

data "local_file" "aft_lambda_layer" {
  filename = "${path.module}/buildspecs/aft-lambda-layer.yml"
}
