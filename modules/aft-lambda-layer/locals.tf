locals {
  common_name = "python-layer-builder-${var.lambda_layer_name}-${random_string.resource_suffix.result}"
  account_id  = data.aws_caller_identity.session.account_id
  target_id   = "trigger_build"
}
