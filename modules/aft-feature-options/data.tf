# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
data "aws_partition" "current" {
  provider = aws.aft_management
}

data "aws_region" "current" {
  provider = aws.aft_management
}

data "aws_caller_identity" "current" {
  provider = aws.aft_management
}

data "aws_caller_identity" "ct_management" {
  provider = aws.ct_management
}

data "aws_caller_identity" "ct_audit" {
  provider = aws.audit
}

data "aws_caller_identity" "ct_log" {
  provider = aws.log_archive
}

data "aws_iam_policy" "AWSLambdaBasicExecutionRole" {
  provider = aws.aft_management
  name     = "AWSLambdaBasicExecutionRole"
}

data "aws_iam_policy" "AWSLambdaVPCAccessExecutionRole" {
  provider = aws.aft_management
  name     = "AWSLambdaVPCAccessExecutionRole"
}

data "aws_organizations_organization" "aft_organization" {
  provider = aws.ct_management
}
