# MDLZ CUSTOMIZATION
resource "aws_dynamodb_table" "aft_application_request" {
  name           = "aft-application-request"
  read_capacity  = 1
  write_capacity = 1
  hash_key       = "ApplicationName"

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
