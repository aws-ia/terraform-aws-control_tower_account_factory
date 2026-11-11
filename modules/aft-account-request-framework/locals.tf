# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
locals {
  lambda_managed_policies = [data.aws_iam_policy.AWSLambdaBasicExecutionRole.arn, data.aws_iam_policy.AWSLambdaVPCAccessExecutionRole.arn]
  orgs_endpoint_supported = data.aws_region.aft-management.region == "us-east-1" ? true : false
  service_catalog_backend = var.account_vending_method == "service_catalog"

  # Lambda functions backing the organizations account-provisioning Step Function.
  # Only created for the Organizations vending method (count gated on
  # service_catalog_backend).
  orgs_provisioning_lambda_function_names = {
    create_account      = "aft-organizations-create-account"
    poll_create_status  = "aft-organizations-poll-create-status"
    move_account        = "aft-organizations-move-account"
    baseline_status     = "aft-organizations-baseline-status"
    lookup_account      = "aft-organizations-lookup-account"
    notify_failure      = "aft-organizations-notify-failure"
    publish_event       = "aft-organizations-publish-event"
    validate_governance = "aft-organizations-validate-governance"
    delete_default_vpcs = "aft-organizations-delete-default-vpcs"
  }

  vpc_private_route_table_ids = local.vpc_deployment ? try(data.aws_route_tables.aft_private_route_tables[0].ids, []) : []
  vpc_public_route_table_ids  = local.vpc_deployment ? try(data.aws_route_tables.aft_public_route_tables[0].ids, []) : []
  vpc_route_table_ids         = concat(local.vpc_private_route_table_ids, local.vpc_public_route_table_ids)

  vpc_private_subnet_ids = var.aft_enable_vpc || var.aft_customer_vpc_id != null ? concat(try(tolist([aws_subnet.aft_vpc_private_subnet_01[0].id, aws_subnet.aft_vpc_private_subnet_02[0].id]), []), var.aft_customer_private_subnets) : []
  # public subnets are only applicable when AFT deploys the VPC
  vpc_public_subnet_ids = var.aft_enable_vpc && var.aft_customer_vpc_id == null ? tolist([aws_subnet.aft_vpc_public_subnet_01[0].id, aws_subnet.aft_vpc_public_subnet_02[0].id]) : []

  vpc_cidr       = local.vpc_deployment ? data.aws_vpc.aft[0].cidr_block : null
  vpc_deployment = var.aft_enable_vpc || var.aft_customer_vpc_id != null ? true : false
  vpc_id         = var.aft_enable_vpc || var.aft_customer_vpc_id != null ? try(aws_vpc.aft_vpc[0].id, var.aft_customer_vpc_id) : null
}
