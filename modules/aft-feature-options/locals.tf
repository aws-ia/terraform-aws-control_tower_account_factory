# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
locals {
  lambda_managed_policies = [data.aws_iam_policy.AWSLambdaBasicExecutionRole.arn, data.aws_iam_policy.AWSLambdaVPCAccessExecutionRole.arn]
  lambda_subnet_ids       =  var.aft_feature_disable_private_networking ? var.aft_vpc_public_subnets : var.aft_vpc_private_subnets
}
