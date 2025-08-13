# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Table that stores account-meta data
resource "aws_dynamodb_table" "aft_request_metadata" {
  name         = "aft-request-metadata"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id"

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
    projection_type = "ALL"
  }

  global_secondary_index {
    name               = "emailIndex"
    hash_key           = "email"
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

# Table that stores the configuration details for the account vending machine
resource "aws_dynamodb_table" "aft_request" {
  name             = "aft-request"
  billing_mode     = "PAY_PER_REQUEST"
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

# Table that stores the audit history for the account
resource "aws_dynamodb_table" "aft_request_audit" {
  name             = "aft-request-audit"
  billing_mode     = "PAY_PER_REQUEST"
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

# Table that stores the audit history for the account
resource "aws_dynamodb_table" "aft_controltower_events" {
  name             = "aft-controltower-events"
  billing_mode     = "PAY_PER_REQUEST"
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
