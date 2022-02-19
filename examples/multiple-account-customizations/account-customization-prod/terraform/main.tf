# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#
module "prod_customizations" {
  source = "../../modules/production"
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
