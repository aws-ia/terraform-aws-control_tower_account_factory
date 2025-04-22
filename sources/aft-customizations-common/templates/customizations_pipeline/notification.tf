resource "aws_codestarnotifications_notification_rule" "codepipeline_events" {
  detail_type    = "BASIC"
  event_type_ids = ["codepipeline-pipeline-pipeline-execution-failed",
                    "codepipeline-pipeline-pipeline-execution-canceled",
                    "codepipeline-pipeline-pipeline-execution-started",
                    "codepipeline-pipeline-pipeline-execution-resumed",
                    "codepipeline-pipeline-pipeline-execution-succeeded",
                    "codepipeline-pipeline-pipeline-execution-superseded"]

  name     = "${var.account_id}-customizations-pipeline-notify"
  resource = local.vcs.is_codecommit ? aws_codepipeline.aft_codecommit_customizations_codepipeline.arn : aws_codepipeline.aft_codeconnections_customizations_codepipeline.arn

  target {
    address = data.aws_ssm_parameter.aft_codepipeline_customizations_sns_topic.value
  }
}