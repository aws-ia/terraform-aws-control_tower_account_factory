
### VALIDATE REQUEST FUNCTION

data "archive_file" "validate_request" {
  type        = "zip"
  source_dir  = "${path.module}/lambda/aft-account-provisioning-framework-validate-request/"
  output_path = "${path.module}/validate_request.zip"
}

resource "aws_lambda_function" "validate_request" {
  filename         = data.archive_file.validate_request.output_path
  function_name    = "aft-account-provisioning-framework-validate-request"
  description      = "AFT account provisioning framework - validate_request"
  role             = aws_iam_role.aft_lambda_aft_account_provisioning_framework_validate_request.arn
  handler          = "aft_account_provisioning_framework_validate_request.lambda_handler"
  source_code_hash = data.archive_file.validate_request.output_base64sha256
  runtime          = "python3.8"
  timeout          = 300
  layers           = [var.aft_common_layer_arn]

  vpc_config {
    subnet_ids         = var.aft_vpc_private_subnets
    security_group_ids = var.aft_vpc_default_sg
  }
}

resource "aws_cloudwatch_log_group" "validate_request" {
  name              = "/aws/lambda/${aws_lambda_function.validate_request.function_name}"
  retention_in_days = var.cloudwatch_log_group_retention
}

### GET ACCOUNT INFO FUNCTION

data "archive_file" "get_account_info" {
  type        = "zip"
  source_dir  = "${path.module}/lambda/aft-account-provisioning-framework-get-account-info/"
  output_path = "${path.module}/get_account_info.zip"
}

resource "aws_lambda_function" "get_account_info" {
  filename         = data.archive_file.get_account_info.output_path
  function_name    = "aft-account-provisioning-framework-get-account-info"
  description      = "AFT account provisioning framework - get_account_info"
  role             = aws_iam_role.aft_lambda_aft_account_provisioning_framework_get_account_info.arn
  handler          = "aft_account_provisioning_framework_get_account_info.lambda_handler"
  source_code_hash = data.archive_file.get_account_info.output_base64sha256
  runtime          = "python3.8"
  timeout          = 300
  layers           = [var.aft_common_layer_arn]

  vpc_config {
    subnet_ids         = var.aft_vpc_private_subnets
    security_group_ids = var.aft_vpc_default_sg
  }
}

resource "aws_cloudwatch_log_group" "get_account_info" {
  name              = "/aws/lambda/${aws_lambda_function.get_account_info.function_name}"
  retention_in_days = var.cloudwatch_log_group_retention
}

###  CREATE ROLE FUNCTION

data "archive_file" "create_role" {
  type        = "zip"
  source_dir  = "${path.module}/lambda/aft-account-provisioning-framework-create-role/"
  output_path = "${path.module}/create_role.zip"
}

resource "aws_lambda_function" "create_role" {
  filename         = data.archive_file.create_role.output_path
  function_name    = "aft-account-provisioning-framework-create-aft-execution-role"
  description      = "AFT account provisioning framework - create_role"
  role             = aws_iam_role.aft_lambda_aft_account_provisioning_framework_create_role.arn
  handler          = "aft_account_provisioning_framework_create_role.lambda_handler"
  source_code_hash = data.archive_file.create_role.output_base64sha256
  runtime          = "python3.8"
  timeout          = 300
  layers           = [var.aft_common_layer_arn]

  vpc_config {
    subnet_ids         = var.aft_vpc_private_subnets
    security_group_ids = var.aft_vpc_default_sg
  }
}

resource "aws_cloudwatch_log_group" "create_role" {
  name              = "/aws/lambda/${aws_lambda_function.create_role.function_name}"
  retention_in_days = var.cloudwatch_log_group_retention
}


###  TAG ACCOUNT FUNCTION

data "archive_file" "tag_account" {
  type        = "zip"
  source_dir  = "${path.module}/lambda/aft-account-provisioning-framework-tag-account/"
  output_path = "${path.module}/tag_account.zip"
}

resource "aws_lambda_function" "tag_account" {
  filename         = data.archive_file.tag_account.output_path
  function_name    = "aft-account-provisioning-framework-tag-account"
  description      = "AFT account provisioning framework - tag_account"
  role             = aws_iam_role.aft_lambda_aft_account_provisioning_framework_tag_account.arn
  handler          = "aft_account_provisioning_framework_tag_account.lambda_handler"
  source_code_hash = data.archive_file.tag_account.output_base64sha256
  runtime          = "python3.8"
  timeout          = 300
  layers           = [var.aft_common_layer_arn]

  vpc_config {
    subnet_ids         = var.aft_vpc_private_subnets
    security_group_ids = var.aft_vpc_default_sg
  }
}

resource "aws_cloudwatch_log_group" "tag_account" {
  name              = "/aws/lambda/${aws_lambda_function.tag_account.function_name}"
  retention_in_days = var.cloudwatch_log_group_retention
}

###  PERSIST METADATA FUNCTION

data "archive_file" "persist_metadata" {
  type        = "zip"
  source_dir  = "${path.module}/lambda/aft-account-provisioning-framework-persist-metadata/"
  output_path = "${path.module}/persist_metadata.zip"
}

resource "aws_lambda_function" "persist_metadata" {
  filename         = data.archive_file.persist_metadata.output_path
  function_name    = "aft-account-provisioning-framework-persist-metadata"
  description      = "AFT account provisioning framework - persist_metadata"
  role             = aws_iam_role.aft_lambda_aft_account_provisioning_framework_persist_metadata.arn
  handler          = "aft_account_provisioning_framework_persist_metadata.lambda_handler"
  source_code_hash = data.archive_file.persist_metadata.output_base64sha256
  runtime          = "python3.8"
  timeout          = 300
  layers           = [var.aft_common_layer_arn]

  vpc_config {
    subnet_ids         = var.aft_vpc_private_subnets
    security_group_ids = var.aft_vpc_default_sg
  }
}

resource "aws_cloudwatch_log_group" "persist_metadata" {
  name              = "/aws/lambda/${aws_lambda_function.persist_metadata.function_name}"
  retention_in_days = var.cloudwatch_log_group_retention
}

###  Account Metadata SSM Function

data "archive_file" "account_metadata_ssm" {
  type        = "zip"
  source_dir  = "${path.module}/lambda/aft-account-provisioning-framework-account-metadata-ssm/"
  output_path = "${path.module}/account_metadata_ssm.zip"
}

resource "aws_lambda_function" "account_metadata_ssm" {
  filename         = data.archive_file.account_metadata_ssm.output_path
  function_name    = "aft-account-provisioning-framework-account-metadata-ssm"
  description      = "AFT account provisioning framework - account_metadata_ssm"
  role             = aws_iam_role.aft_lambda_aft_account_provisioning_framework_persist_metadata.arn
  handler          = "aft_account_provisioning_framework_account_metadata_ssm.lambda_handler"
  source_code_hash = data.archive_file.account_metadata_ssm.output_base64sha256
  runtime          = "python3.8"
  timeout          = 300
  layers           = [var.aft_common_layer_arn]

  vpc_config {
    subnet_ids         = var.aft_vpc_private_subnets
    security_group_ids = var.aft_vpc_default_sg
  }
}

resource "aws_cloudwatch_log_group" "account_metadata_ssm" {
  name              = "/aws/lambda/${aws_lambda_function.account_metadata_ssm.function_name}"
  retention_in_days = var.cloudwatch_log_group_retention
}
