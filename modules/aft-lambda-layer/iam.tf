resource "aws_iam_role" "codebuild" {
  name               = local.common_name
  assume_role_policy = file("${path.module}/iam/trust-policies/codebuild.tpl")
}

resource "aws_iam_role_policy" "codebuild" {
  role = aws_iam_role.codebuild.name
  policy = templatefile("${path.module}/iam/role-policies/codebuild.tpl", {
    "aws_region"                                = var.aws_region
    "account_id"                                = local.account_id
    "layer_name"                                = var.lambda_layer_name
    "s3_bucket_name"                            = var.s3_bucket_name
    "cloudwatch_event_name"                     = local.common_name
    "data_aws_kms_alias_aft_key_target_key_arn" = var.aft_kms_key_arn
  })
}