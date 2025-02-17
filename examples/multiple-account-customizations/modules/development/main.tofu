# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#

resource "aws_ssm_parameter" "example_parameter_dev" {
  name  = "/aft/example/parameter_dev"
  type  = "String"
  value = "developer customizations"
}
