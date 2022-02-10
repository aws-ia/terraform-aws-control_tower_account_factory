# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#
data "aws_caller_identity" "session" {}

data "local_file" "aft_lambda_layer" {
  filename = "${path.module}/buildspecs/aft-lambda-layer.yml"
}
