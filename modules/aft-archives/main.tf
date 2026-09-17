# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
locals {
  aft_lambda_src = "${path.module}/../../src/aft_lambda"

  # Content digest per Lambda source directory. Embedding this in output_path
  # makes any source change alter output_path, which forces the archive_file
  # resource to be recreated during apply. This ensures the zip is regenerated
  # on the apply runner in split-stage pipelines where plan and apply run on
  # separate filesystems (otherwise the plan-time zip is missing at apply). See
  # https://github.com/aws-ia/terraform-aws-control_tower_account_factory/issues/633
  aft_lambda_source_hashes = {
    for name in [
      "aft_account_provisioning_framework",
      "aft_account_request_framework",
      "aft_customizations",
      "aft_feature_options",
    ] :
    name => sha1(join("", [
      for f in sort(fileset("${local.aft_lambda_src}/${name}", "**")) :
      filesha1("${local.aft_lambda_src}/${name}/${f}")
    ]))
  }
}

resource "archive_file" "provisioning_framework" {
  type        = "zip"
  source_dir  = "${local.aft_lambda_src}/aft_account_provisioning_framework"
  output_path = "${local.aft_lambda_src}/aft_account_provisioning_framework_${local.aft_lambda_source_hashes["aft_account_provisioning_framework"]}.zip"
}

resource "archive_file" "request_framework" {
  type        = "zip"
  source_dir  = "${local.aft_lambda_src}/aft_account_request_framework"
  output_path = "${local.aft_lambda_src}/aft_account_request_framework_${local.aft_lambda_source_hashes["aft_account_request_framework"]}.zip"
}

resource "archive_file" "customizations" {
  type        = "zip"
  source_dir  = "${local.aft_lambda_src}/aft_customizations"
  output_path = "${local.aft_lambda_src}/aft_customizations_${local.aft_lambda_source_hashes["aft_customizations"]}.zip"
}

resource "archive_file" "feature_options" {
  type        = "zip"
  source_dir  = "${local.aft_lambda_src}/aft_feature_options"
  output_path = "${local.aft_lambda_src}/aft_feature_options_${local.aft_lambda_source_hashes["aft_feature_options"]}.zip"
}

# aft_builder intentionally left on a static output_path (see note above).
resource "archive_file" "builder" {
  type        = "zip"
  source_dir  = "${local.aft_lambda_src}/aft_builder"
  output_path = "${local.aft_lambda_src}/aft_builder.zip"
}
