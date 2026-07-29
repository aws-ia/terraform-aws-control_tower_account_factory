# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
data "aws_partition" "current" {}

data "aws_caller_identity" "session" {}

data "local_file" "aft_lambda_layer" {
  filename = "${path.module}/buildspecs/aft-lambda-layer.yml"
}

data "aws_s3_bucket_object" "aft_lambda_layer" {
  bucket = var.s3_bucket_name
  key    = "layer.zip"
}