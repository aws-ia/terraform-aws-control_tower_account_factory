# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#
resource "aws_ssm_parameter" "example_parameter_prod" {
  name  = "/aft/example/parameter_prod"
  type  = "String"
  value = "Production customizations"
}
