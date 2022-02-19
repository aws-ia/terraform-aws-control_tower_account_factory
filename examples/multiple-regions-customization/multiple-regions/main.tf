# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#

resource "aws_ssm_parameter" "param-us-east-2" {
  name  = "/aft/example/region"
  type  = "String"
  value = "us-east-2"

  # Declare the custom provider using the alias
  provider = aws.us_east_2
}

resource "aws_ssm_parameter" "param-us-west-1" {
  name  = "/aft/example/region"
  type  = "String"
  value = "us-west-1"

  # Declare the custom provider using the alias
  provider = aws.us_west_1
}
