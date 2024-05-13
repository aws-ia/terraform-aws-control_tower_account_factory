# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
locals {
  lambda_managed_policies = [data.aws_iam_policy.AWSLambdaBasicExecutionRole.arn, data.aws_iam_policy.AWSLambdaVPCAccessExecutionRole.arn]
  vpc_endpoint_subnet_ids = var.aft_enable_vpc ? [aws_subnet.aft_vpc_private_subnet_01[0].id, aws_subnet.aft_vpc_private_subnet_02[0].id] : null
}
