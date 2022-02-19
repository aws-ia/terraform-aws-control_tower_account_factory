# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
locals {
  common_name                     = "python-layer-builder-${var.lambda_layer_name}-${random_string.resource_suffix.result}"
  account_id                      = data.aws_caller_identity.session.account_id
  target_id                       = "trigger_build"
  codebuild_invoker_function_name = "aft-lambda-layer-codebuild-invoker"
}
