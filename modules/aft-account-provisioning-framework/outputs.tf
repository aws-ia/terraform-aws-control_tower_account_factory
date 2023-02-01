# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
output "state_machine_arn" {
  value = aws_sfn_state_machine.aft_account_provisioning_framework_sfn.arn
}

output "create_role_function_arn" {
  value = aws_lambda_function.create_role.arn
}
output "tag_account_function_arn" {
  value = aws_lambda_function.tag_account.arn
}
output "persist_metadata_function_arn" {
  value = aws_lambda_function.persist_metadata.arn
}
