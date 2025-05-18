# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
provider "aws" {
  alias  = "ct_management"
  region = var.ct_home_region
  # The default profile or environment variables should authenticate to the Control Tower Management Account as Administrator
  default_tags {
    tags = local.aft_tags
  }
}

provider "aws" {
  alias  = "aft_management"
  region = var.ct_home_region
  assume_role {
    role_arn     = "arn:${data.aws_partition.current.partition}:iam::${var.aft_management_account_id}:role/AWSControlTowerExecution"
    session_name = local.aft_session_name
  }
  default_tags {
    tags = local.aft_tags
  }
}
provider "aws" {
  alias  = "tf_backend_secondary_region"
  region = var.tf_backend_secondary_region
  assume_role {
    role_arn     = "arn:${data.aws_partition.current.partition}:iam::${var.aft_management_account_id}:role/AWSControlTowerExecution"
    session_name = local.aft_session_name
  }
  default_tags {
    tags = local.aft_tags
  }
}
provider "aws" {
  alias  = "audit"
  region = var.ct_home_region
  assume_role {
    role_arn     = "arn:${data.aws_partition.current.partition}:iam::${var.audit_account_id}:role/AWSControlTowerExecution"
    session_name = local.aft_session_name
  }
  default_tags {
    tags = local.aft_tags
  }
}
provider "aws" {
  alias  = "log_archive"
  region = var.ct_home_region
  assume_role {
    role_arn     = "arn:${data.aws_partition.current.partition}:iam::${var.log_archive_account_id}:role/AWSControlTowerExecution"
    session_name = local.aft_session_name
  }
  default_tags {
    tags = local.aft_tags
  }
}
