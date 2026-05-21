locals {
  tf_distribution = nonsensitive(data.aws_ssm_parameter.aft_tf_distribution.value)

  # workflow_type apply-with-approval is available only when terraform distribution is oss
  workflow_type = local.tf_distribution != "oss" ? "apply" : var.workflow_type
}
