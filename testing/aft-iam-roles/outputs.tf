# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#
# output "netops_role_arn" {
#   value = aws_iam_role.netops_role[each.value.arn]
# }
# output "ct_management_exec_role_arn" {
#   value = module.ct_management_exec_role.arn
# }
# output "log_archive_exec_role_arn" {
#   value = module.log_archive_exec_role.arn
# }
# output "audit_exec_role_arn" {
#   value = module.audit_exec_role.arn
# }
# output "netops_execution_role_arn" {
#   value = module.netops_exec_role[each.value.arn]
# }

# output "account_ids" {
#   value = data.aws_organizations_organization.example.non_master_accounts[*].id
# }