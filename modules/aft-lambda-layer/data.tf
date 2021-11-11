data "aws_caller_identity" "session" {}

data "local_file" "aft_lambda_layer" {
  filename = "${path.module}/buildspecs/aft-lambda-layer.yml"
}
