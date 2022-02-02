######## aft_account_request_audit_trigger ########

resource "aws_lambda_function" "aft_account_request_audit_trigger" {

  filename      = var.request_framework_archive_path
  function_name = "aft-account-request-audit-trigger"
  description   = "Receives trigger from DynamoDB aft-request table and inserts the event into aft-request-audit table"
  role          = aws_iam_role.aft_account_request_audit_trigger.arn
  handler       = "aft_account_request_audit_trigger.lambda_handler"

  source_code_hash = var.request_framework_archive_hash

  runtime = "python3.8"
  timeout = "300"
  layers  = [var.aft_common_layer_arn]

  vpc_config {
    subnet_ids         = tolist([aws_subnet.aft_vpc_private_subnet_01.id, aws_subnet.aft_vpc_private_subnet_02.id])
    security_group_ids = tolist([aws_security_group.aft_vpc_default_sg.id])
  }

}

resource "time_sleep" "wait_60_seconds" {
  depends_on      = [aws_dynamodb_table.aft_request, aws_lambda_function.aft_account_request_audit_trigger]
  create_duration = "60s"
}

resource "aws_lambda_event_source_mapping" "aft_account_request_audit_trigger" {
  depends_on        = [time_sleep.wait_60_seconds]
  event_source_arn  = aws_dynamodb_table.aft_request.stream_arn
  function_name     = aws_lambda_function.aft_account_request_audit_trigger.arn
  starting_position = "LATEST"
  batch_size        = 1
}

resource "aws_cloudwatch_log_group" "aft_account_request_audit_trigger" {
  name              = "/aws/lambda/${aws_lambda_function.aft_account_request_audit_trigger.function_name}"
  retention_in_days = var.cloudwatch_log_group_retention
}

######## aft_account_request_action_trigger ########


resource "aws_lambda_function" "aft_account_request_action_trigger" {

  filename      = var.request_framework_archive_path
  function_name = "aft-account-request-action-trigger"
  description   = "Receives trigger from DynamoDB aft-request table and determines action target - SQS or Lambda aft-invoke-aft-account-provisioning-framework"
  role          = aws_iam_role.aft_account_request_action_trigger.arn
  handler       = "aft_account_request_action_trigger.lambda_handler"

  source_code_hash = var.request_framework_archive_hash

  runtime = "python3.8"
  timeout = "300"
  layers  = [var.aft_common_layer_arn]

  vpc_config {
    subnet_ids         = tolist([aws_subnet.aft_vpc_private_subnet_01.id, aws_subnet.aft_vpc_private_subnet_02.id])
    security_group_ids = tolist([aws_security_group.aft_vpc_default_sg.id])
  }

}

resource "aws_lambda_event_source_mapping" "aft_account_request_action_trigger" {
  event_source_arn  = aws_dynamodb_table.aft_request.stream_arn
  function_name     = aws_lambda_function.aft_account_request_action_trigger.arn
  starting_position = "LATEST"
  batch_size        = 1
}

resource "aws_cloudwatch_log_group" "aft_account_request_action_trigger" {
  name              = "/aws/lambda/${aws_lambda_function.aft_account_request_action_trigger.function_name}"
  retention_in_days = var.cloudwatch_log_group_retention
}

######## aft_controltower_event_logger ########


resource "aws_lambda_function" "aft_controltower_event_logger" {

  filename      = var.request_framework_archive_path
  function_name = "aft-controltower-event-logger"
  description   = "Receives Control Tower events through dedicated event bus event and writes event to aft-controltower-events table"
  role          = aws_iam_role.aft_controltower_event_logger.arn
  handler       = "aft_controltower_event_logger.lambda_handler"

  source_code_hash = var.request_framework_archive_hash

  runtime = "python3.8"
  timeout = "300"
  layers  = [var.aft_common_layer_arn]

  vpc_config {
    subnet_ids         = tolist([aws_subnet.aft_vpc_private_subnet_01.id, aws_subnet.aft_vpc_private_subnet_02.id])
    security_group_ids = tolist([aws_security_group.aft_vpc_default_sg.id])
  }
}

resource "aws_lambda_permission" "aft_controltower_event_logger" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.aft_controltower_event_logger.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.aft_controltower_event_trigger.arn
}

resource "aws_cloudwatch_log_group" "aft_controltower_event_logger" {
  name              = "/aws/lambda/${aws_lambda_function.aft_controltower_event_logger.function_name}"
  retention_in_days = var.cloudwatch_log_group_retention
}

######## aft_account_request_processor ########


resource "aws_lambda_function" "aft_account_request_processor" {

  filename      = var.request_framework_archive_path
  function_name = "aft-account-request-processor"
  description   = "Triggered by CW Event, reads aft-account-request.fifo queue and performs needed action"
  role          = aws_iam_role.aft_account_request_processor.arn
  handler       = "aft_account_request_processor.lambda_handler"

  source_code_hash = var.request_framework_archive_hash

  runtime = "python3.8"
  timeout = "300"
  layers  = [var.aft_common_layer_arn]

  vpc_config {
    subnet_ids         = tolist([aws_subnet.aft_vpc_private_subnet_01.id, aws_subnet.aft_vpc_private_subnet_02.id])
    security_group_ids = tolist([aws_security_group.aft_vpc_default_sg.id])
  }

}

resource "aws_lambda_permission" "aft_account_request_processor" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.aft_account_request_processor.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.aft_account_request_processor.arn
}

resource "aws_cloudwatch_log_group" "aft_account_request_processor" {
  name              = "/aws/lambda/${aws_lambda_function.aft_account_request_processor.function_name}"
  retention_in_days = var.cloudwatch_log_group_retention
}

######## aft_invoke_aft_account_provisioning_framework ########


resource "aws_lambda_function" "aft_invoke_aft_account_provisioning_framework" {

  filename      = var.request_framework_archive_path
  function_name = "aft-invoke-aft-account-provisioning-framework"
  description   = "Calls AFT Account Provisioning Framework Step Function based on a formatted incoming event from Lambda or CW Event"
  role          = aws_iam_role.aft_invoke_aft_account_provisioning_framework.arn
  handler       = "aft_invoke_aft_account_provisioning_framework.lambda_handler"

  source_code_hash = var.request_framework_archive_hash

  runtime = "python3.8"
  timeout = "300"
  layers  = [var.aft_common_layer_arn]

  vpc_config {
    subnet_ids         = tolist([aws_subnet.aft_vpc_private_subnet_01.id, aws_subnet.aft_vpc_private_subnet_02.id])
    security_group_ids = tolist([aws_security_group.aft_vpc_default_sg.id])
  }

}

resource "aws_lambda_permission" "aft_invoke_aft_account_provisioning_framework" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.aft_invoke_aft_account_provisioning_framework.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.aft_controltower_event_trigger.arn
}

resource "aws_cloudwatch_log_group" "aft_invoke_aft_account_provisioning_framework" {
  name              = "/aws/lambda/${aws_lambda_function.aft_invoke_aft_account_provisioning_framework.function_name}"
  retention_in_days = var.cloudwatch_log_group_retention
}
