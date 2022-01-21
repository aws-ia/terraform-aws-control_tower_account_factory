resource "aws_cloudwatch_event_rule" "codebuild_trigger" {
  lifecycle {
    ignore_changes = [is_enabled]
  }

  name                = "${local.common_name}-${replace(time_sleep.eventbridge_rule.triggers["lambda_layer_version"], ".", "-")}"
  description         = "Triggers the python layer builder codebuild job."
  schedule_expression = "rate(2 minutes)"
}

resource "aws_cloudwatch_event_target" "codebuild_trigger" {
  rule      = aws_cloudwatch_event_rule.codebuild_trigger.name
  target_id = local.target_id
  arn       = aws_codebuild_project.codebuild.id
  role_arn  = aws_iam_role.codebuild.arn
}
