######## aft_delete_default_vpc ########
data "archive_file" "aft_delete_default_vpc" {
  type        = "zip"
  source_dir  = "${path.module}/lambda/aft-delete-default-vpc"
  output_path = "${path.module}/lambda/aft-delete-default-vpc.zip"
}

resource "aws_lambda_function" "aft_delete_default_vpc" {
  provider      = aws.aft_management
  filename      = "${path.module}/lambda/aft-delete-default-vpc.zip"
  function_name = "aft-delete-default-vpc"
  description   = "Deletes default VPCs in all regions. Called from aft-features SFN."
  role          = aws_iam_role.aft_delete_default_vpc_lambda.arn
  handler       = "aft_delete_default_vpc.lambda_handler"

  source_code_hash = data.archive_file.aft_delete_default_vpc.output_base64sha256

  runtime = "python3.8"
  timeout = "300"
  layers  = [var.aft_common_layer_arn]

  vpc_config {
    subnet_ids         = var.aft_vpc_private_subnets
    security_group_ids = var.aft_vpc_default_sg
  }
}

resource "aws_cloudwatch_log_group" "aft_delete_default_vpc" {
  provider          = aws.aft_management
  name              = "/aws/lambda/${aws_lambda_function.aft_delete_default_vpc.function_name}"
  retention_in_days = var.cloudwatch_log_group_retention
}


######## aft_enroll_support ########
data "archive_file" "aft_enroll_support" {
  type        = "zip"
  source_dir  = "${path.module}/lambda/aft-enroll-support"
  output_path = "${path.module}/lambda/aft-enroll-support.zip"
}

resource "aws_lambda_function" "aft_enroll_support" {
  provider      = aws.aft_management
  filename      = "${path.module}/lambda/aft-enroll-support.zip"
  function_name = "aft-enroll-support"
  description   = "Creates request to enroll an account in Enterprise support. Called from aft-features SFN."
  role          = aws_iam_role.aft_enroll_support.arn
  handler       = "aft_enroll_support.lambda_handler"

  source_code_hash = data.archive_file.aft_enroll_support.output_base64sha256

  runtime = "python3.8"
  timeout = "300"
  layers  = [var.aft_common_layer_arn]

  vpc_config {
    subnet_ids         = var.aft_vpc_private_subnets
    security_group_ids = var.aft_vpc_default_sg
  }
}

resource "aws_cloudwatch_log_group" "aft_enroll_support" {
  provider          = aws.aft_management
  name              = "/aws/lambda/${aws_lambda_function.aft_enroll_support.function_name}"
  retention_in_days = var.cloudwatch_log_group_retention
}

######## aft_enable_cloudtrail ########
data "archive_file" "aft_enable_cloudtrail" {
  type        = "zip"
  source_dir  = "${path.module}/lambda/aft-enable-cloudtrail"
  output_path = "${path.module}/lambda/aft-enable-cloudtrail.zip"
}

resource "aws_lambda_function" "aft_enable_cloudtrail" {
  provider      = aws.aft_management
  filename      = "${path.module}/lambda/aft-enable-cloudtrail.zip"
  function_name = "aft-enable-cloudtrail"
  description   = "Creates an Org Trail to capture data events. Called from aft-features SFN."
  role          = aws_iam_role.aft_enable_cloudtrail.arn
  handler       = "aft_enable_cloudtrail.lambda_handler"

  source_code_hash = data.archive_file.aft_enable_cloudtrail.output_base64sha256

  runtime = "python3.8"
  timeout = "300"
  layers  = [var.aft_common_layer_arn]

  vpc_config {
    subnet_ids         = var.aft_vpc_private_subnets
    security_group_ids = var.aft_vpc_default_sg
  }
}

resource "aws_cloudwatch_log_group" "aft_enable_cloudtrail" {
  provider          = aws.aft_management
  name              = "/aws/lambda/${aws_lambda_function.aft_enable_cloudtrail.function_name}"
  retention_in_days = var.cloudwatch_log_group_retention
}
