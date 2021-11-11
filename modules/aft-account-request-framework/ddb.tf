# Table that stores account-meta data
resource "aws_dynamodb_table" "aft_request_metadata" {
  name           = "aft-request-metadata"
  read_capacity  = 1
  write_capacity = 1
  hash_key       = "id"

  attribute {
    name = "id"
    type = "S"
  }

  attribute {
    name = "email"
    type = "S"
  }

  attribute {
    name = "type"
    type = "S"
  }

  global_secondary_index {
    name            = "typeIndex"
    hash_key        = "type"
    write_capacity  = 1
    read_capacity   = 1
    projection_type = "ALL"
  }

  global_secondary_index {
    name               = "emailIndex"
    hash_key           = "email"
    write_capacity     = 1
    read_capacity      = 1
    projection_type    = "INCLUDE"
    non_key_attributes = ["id"]
  }

  point_in_time_recovery {
    enabled = true
  }

  server_side_encryption {
    enabled     = true
    kms_key_arn = aws_kms_key.aft.arn
  }
}
resource "aws_backup_vault" "aft_controltower_request_request_metadata_vault" {
  name        = "aft-controltower-events-request-metadata-vault"
  kms_key_arn = aws_kms_key.aft.arn
}
resource "aws_backup_plan" "aft_controltower_request_request_metadata_plan" {
  name = "aft-controltower-request-request-metadata-plan"
  rule {
    rule_name         = "aft_controltower_request_request_metadata_rule"
    target_vault_name = aws_backup_vault.aft_controltower_request_request_metadata_vault.name
    schedule          = "cron(0 * * * ? *)" # Every hour
  }
}

# Table that stores the configuration details for the account vending machine
resource "aws_dynamodb_table" "aft_request" {
  name             = "aft-request"
  read_capacity    = 1
  write_capacity   = 1
  hash_key         = "id"
  stream_enabled   = true
  stream_view_type = "NEW_AND_OLD_IMAGES"

  attribute {
    name = "id"
    type = "S"
  }

  point_in_time_recovery {
    enabled = true
  }

  server_side_encryption {
    enabled     = true
    kms_key_arn = aws_kms_key.aft.arn
  }
}
resource "aws_backup_vault" "aft_controltower_request_vault" {
  name        = "aft-controltower-events-request-vault"
  kms_key_arn = aws_kms_key.aft.arn
}
resource "aws_backup_plan" "aft_controltower_request_plan" {
  name = "aft-controltower-request-plan"
  rule {
    rule_name         = "aft_controltower_request_rule"
    target_vault_name = aws_backup_vault.aft_controltower_request_vault.name
    schedule          = "cron(0 * * * ? *)" # Every hour
  }
}

# Table that stores the audit history for the account
resource "aws_dynamodb_table" "aft_request_audit" {
  name             = "aft-request-audit"
  read_capacity    = 1
  write_capacity   = 1
  hash_key         = "id"
  range_key        = "timestamp"
  stream_enabled   = true
  stream_view_type = "NEW_AND_OLD_IMAGES"

  attribute {
    name = "id"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "S"
  }

  point_in_time_recovery {
    enabled = true
  }

  server_side_encryption {
    enabled     = true
    kms_key_arn = aws_kms_key.aft.arn
  }
}
resource "aws_backup_vault" "aft_controltower_request_audit_backup_vault" {
  name        = "aft-controltower-events-request-audit-vault"
  kms_key_arn = aws_kms_key.aft.arn
}
resource "aws_backup_plan" "aft_controltower_request_audit_plan" {
  name = "aft-controltower-request-audit-plan"
  rule {
    rule_name         = "aft_controltower_request_audit_rule"
    target_vault_name = aws_backup_vault.aft_controltower_request_audit_backup_vault.name
    schedule          = "cron(0 * * * ? *)" # Every hour
  }
}

# Table that stores the audit history for the account
resource "aws_dynamodb_table" "aft_controltower_events" {
  name             = "aft-controltower-events"
  read_capacity    = 5
  write_capacity   = 5
  hash_key         = "id"
  range_key        = "time"
  stream_enabled   = true
  stream_view_type = "NEW_AND_OLD_IMAGES"

  attribute {
    name = "id"
    type = "S"
  }

  attribute {
    name = "time"
    type = "S"
  }

  point_in_time_recovery {
    enabled = true
  }

  server_side_encryption {
    enabled     = true
    kms_key_arn = aws_kms_key.aft.arn
  }
}
resource "aws_backup_vault" "aft_controltower_events_backup_vault" {
  name        = "aft-controltower-events-backup-vault"
  kms_key_arn = aws_kms_key.aft.arn
}
resource "aws_backup_plan" "aft_controltower_events_backup_plan" {
  name = "aft-controltower-events-backup-plan"
  rule {
    rule_name         = "aft_controltower_events_backup_rule"
    target_vault_name = aws_backup_vault.aft_controltower_events_backup_vault.name
    schedule          = "cron(0 * * * ? *)" # Every hour
  }
}