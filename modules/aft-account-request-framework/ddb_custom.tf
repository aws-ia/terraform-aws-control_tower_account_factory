# MDLZ CUSTOMIZATION
resource "aws_dynamodb_table" "aft_application_request" {
  name           = "aft-application-request"
  hash_key       = "ApplicationName"
  billing_mode   = "PAY_PER_REQUEST"

  attribute {
    name = "ApplicationName"
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

# MDLZ CUSTOMIZATION
resource "aws_dynamodb_table" "aft_network_request_configuration" {
  name           = "aft-network-request-configuration"
  hash_key       = "NetworkName"
  billing_mode   = "PAY_PER_REQUEST"

  attribute {
    name = "NetworkName"
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

resource "aws_dynamodb_table" "aft_network_request_grant" {
  name           = "aft-network-request-grant"
  hash_key       = "NetworkName"
  range_key      = "AccountSlug"
  billing_mode   = "PAY_PER_REQUEST"

  attribute {
    name = "NetworkName"
    type = "S"
  }

  attribute {
    name = "AccountSlug"
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
