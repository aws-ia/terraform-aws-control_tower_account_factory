######## customizations_identify_targets ########
data "archive_file" "aft_customizations_identify_targets" {
  type        = "zip"
  source_dir  = "${path.module}/lambda/aft-customizations-identify-targets"
  output_path = "${path.module}/lambda/aft-customizations-identify-targets.zip"
}

resource "aws_lambda_function" "aft_customizations_identify_targets" {
  filename      = "${path.module}/lambda/aft-customizations-identify-targets.zip"
  function_name = "aft-customizations-identify-targets"
  description   = "Identifies targets to be customized. Called from aft-trigger-customizations SFN."
  role          = aws_iam_role.aft_customizations_identify_targets_lambda.arn
  handler       = "lambda_function.lambda_handler"

  source_code_hash = data.archive_file.aft_customizations_identify_targets.output_base64sha256

  runtime = "python3.8"
  timeout = "300"
  layers  = [var.aft_common_layer_arn]

  vpc_config {
    subnet_ids         = var.aft_vpc_private_subnets
    security_group_ids = var.aft_vpc_default_sg
  }
}

resource "aws_cloudwatch_log_group" "aft_customizations_identify_targets" {
  name              = "/aws/lambda/${aws_lambda_function.aft_customizations_identify_targets.function_name}"
  retention_in_days = var.cloudwatch_log_group_retention
}


######## customizations_execute_pipeline ########
data "archive_file" "aft_customizations_execute_pipeline" {
  type        = "zip"
  source_dir  = "${path.module}/lambda/aft-customizations-execute-pipeline"
  output_path = "${path.module}/lambda/aft-customizations-execute-pipeline.zip"
}

resource "aws_lambda_function" "aft_customizations_execute_pipeline" {
  filename      = "${path.module}/lambda/aft-customizations-execute-pipeline.zip"
  function_name = "aft-customizations-execute-pipeline"
  description   = "Executes the CodePipeline for account baselining. Called from aft-trigger-customizations SFN"
  role          = aws_iam_role.aft_customizations_execute_pipeline_lambda.arn
  handler       = "lambda_function.lambda_handler"

  source_code_hash = data.archive_file.aft_customizations_execute_pipeline.output_base64sha256

  runtime = "python3.8"
  timeout = "300"
  layers  = [var.aft_common_layer_arn]

  vpc_config {
    subnet_ids         = var.aft_vpc_private_subnets
    security_group_ids = var.aft_vpc_default_sg
  }
}

resource "aws_cloudwatch_log_group" "aft_execute_pipeline" {
  name              = "/aws/lambda/${aws_lambda_function.aft_customizations_execute_pipeline.function_name}"
  retention_in_days = var.cloudwatch_log_group_retention
}

######## customizations_get_pipeline_executions ########
data "archive_file" "aft_customizations_get_pipeline_executions" {
  type        = "zip"
  source_dir  = "${path.module}/lambda/aft-customizations-get-pipeline-executions"
  output_path = "${path.module}/lambda/aft-customizations-get-pipeline-executions.zip"
}

resource "aws_lambda_function" "aft_customizations_get_pipeline_executions" {
  filename      = "${path.module}/lambda/aft-customizations-get-pipeline-executions.zip"
  function_name = "aft-customizations-get-pipeline-executions"
  description   = "Gets status of executing pipelines for baselining. Called from aft-trigger-customizations SFN"
  role          = aws_iam_role.aft_customizations_get_pipeline_executions_lambda.arn
  handler       = "lambda_function.lambda_handler"

  source_code_hash = data.archive_file.aft_customizations_get_pipeline_executions.output_base64sha256

  runtime = "python3.8"
  timeout = "300"
  layers  = [var.aft_common_layer_arn]

  vpc_config {
    subnet_ids         = var.aft_vpc_private_subnets
    security_group_ids = var.aft_vpc_default_sg
  }

}

resource "aws_cloudwatch_log_group" "aft_get_pipeline_executions" {
  name              = "/aws/lambda/${aws_lambda_function.aft_customizations_get_pipeline_executions.function_name}"
  retention_in_days = var.cloudwatch_log_group_retention
}

######## customizations_invoke_account_provisioning ########
data "archive_file" "aft_customizations_invoke_account_provisioning" {
  type        = "zip"
  source_dir  = "${path.module}/lambda/aft-customizations-invoke-account-provisioning-framework"
  output_path = "${path.module}/lambda/aft-customizations-invoke-account-provisioning-framework.zip"
}

resource "aws_lambda_function" "aft_customizations_invoke_account_provisioning" {
  filename      = "${path.module}/lambda/aft-customizations-invoke-account-provisioning-framework.zip"
  function_name = "aft-customizations-invoke-account-provisioning"
  description   = "Invokes the account-provisioning SFN."
  role          = aws_iam_role.aft_customizations_invoke_account_provisioning_lambda.arn
  handler       = "lambda_function.lambda_handler"

  source_code_hash = data.archive_file.aft_customizations_invoke_account_provisioning.output_base64sha256

  runtime = "python3.8"
  timeout = "300"
  layers  = [var.aft_common_layer_arn]

  vpc_config {
    subnet_ids         = var.aft_vpc_private_subnets
    security_group_ids = var.aft_vpc_default_sg
  }
}

resource "aws_cloudwatch_log_group" "aft_customizations_invoke_account_provisioning" {
  name              = "/aws/lambda/${aws_lambda_function.aft_customizations_invoke_account_provisioning.function_name}"
  retention_in_days = var.cloudwatch_log_group_retention
}
