data "aws_region" "aft_management" {}
data "aws_caller_identity" "aft_management" {}
data "aws_iam_policy" "AWSLambdaBasicExecutionRole" {
  name = "AWSLambdaBasicExecutionRole"
}

data "aws_iam_policy" "AWSLambdaVPCAccessExecutionRole" {
  name = "AWSLambdaVPCAccessExecutionRole"
}