# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
resource "aws_backup_vault" "aft_controltower_backup_vault" {
  name        = "aft-controltower-backup-vault"
  kms_key_arn = aws_kms_key.aft.arn
}
resource "aws_backup_plan" "aft_controltower_backup_plan" {
  name = "aft-controltower-backup-plan"
  rule {
    rule_name         = "aft_controltower_backup_rule"
    target_vault_name = aws_backup_vault.aft_controltower_backup_vault.name
    schedule          = "cron(0 * * * ? *)"

    dynamic "lifecycle" {
      for_each = var.backup_recovery_point_retention != null ? [1] : []
      content {
        delete_after = var.backup_recovery_point_retention
      }
    }

  }
}

resource "aws_backup_selection" "aft_controltower_backup_selection" {
  iam_role_arn = aws_iam_role.aft_aws_backup.arn
  name         = "aft-controltower-backup-selection"
  plan_id      = aws_backup_plan.aft_controltower_backup_plan.id
  resources = [
    aws_dynamodb_table.aft_request_metadata.arn,
    aws_dynamodb_table.aft_request.arn,
    aws_dynamodb_table.aft_request_audit.arn,
    aws_dynamodb_table.aft_controltower_events.arn
  ]

  # Explicit workaround due to https://github.com/hashicorp/terraform-provider-aws/issues/22595
  condition {}
  not_resources = []

}
