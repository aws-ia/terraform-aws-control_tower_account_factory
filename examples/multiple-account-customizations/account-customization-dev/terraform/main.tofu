# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#
module "developer_customizations" {
  source = "../../modules/development"
  providers = {
    aws = aws
  }
}

module "security_customizations" {
  source = "../../modules/security"
  providers = {
    aws = aws
  }
}
