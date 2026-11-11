# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
data "local_file" "version" {
  filename = "${path.module}/VERSION"
}

data "local_file" "python_version" {
  filename = "${path.module}/PYTHON_VERSION"
}

data "aws_service" "home_region_validation" {
  service_id = "controltower"
  lifecycle {
    precondition {
      # The Organizations vending method does not use Service Catalog, so it is
      # not bound to Service Catalog's regional availability.
      condition     = var.account_vending_method == "organizations" || contains(local.service_catalog_regional_availability, var.ct_home_region)
      error_message = "account_vending_method is \"service_catalog\" but Service Catalog is not available in Control Tower home region ${var.ct_home_region}. Set account_vending_method = \"organizations\" to vend accounts in this region, or refer to https://docs.aws.amazon.com/controltower/latest/userguide/limits.html for supported regions."
    }
  }
}

data "aws_partition" "current" {
}
