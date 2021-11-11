resource "random_string" "resource_suffix" {
  length  = "8"
  lower   = true
  upper   = false
  special = false
}

resource "time_sleep" "eventbridge_rule" {
  create_duration = "5s"
  triggers = {
    lambda_layer_version = var.aft_version
  }
}

resource "time_sleep" "lambda_layer_wait" {
  depends_on = [aws_codebuild_project.codebuild, time_sleep.eventbridge_rule]
  # Provisioning the codebuild container can take some time. This value gives us a buffer to ensure the codebuild job runs.
  create_duration = var.lambda_layer_codebuild_delay
  triggers = {
    lambda_layer_version = var.aft_version
  }
}

resource "aws_lambda_layer_version" "layer_version" {
  lifecycle {
    create_before_destroy = true
  }

  layer_name          = "${var.lambda_layer_name}-${replace(time_sleep.lambda_layer_wait.triggers["lambda_layer_version"], ".", "-")}"
  compatible_runtimes = ["python${var.lambda_layer_python_version}"]
  s3_bucket           = var.s3_bucket_name
  s3_key              = "layer.zip"
}
