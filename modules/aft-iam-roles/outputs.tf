# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#
output "aft_admin_role_arn" {
  value = aws_iam_role.aft_admin_role.arn
}
output "ct_management_exec_role_arn" {
  value = module.ct_management_exec_role.arn
}
output "log_archive_exec_role_arn" {
  value = module.log_archive_exec_role.arn
}
output "audit_exec_role_arn" {
  value = module.audit_exec_role.arn
}
output "aft_exec_role_arn" {
  value = module.aft_exec_role.arn
}
