# MDLZ CUSTOMIZTAION
output "application_request_table_arn" {
  value = aws_dynamodb_table.aft_application_request.arn
}

# MDLZ CUSTOMIZTAION
output "network_request_table_arn" {
  value = aws_dynamodb_table.aft_network_request.arn
}
