# MDLZ CUSTOMIZATION
resource "aws_iam_role_policy" "account_request_codebuild_policy_custom" {
  name = "ct-aft-codebuild-account-request-policy-custom"
  role = aws_iam_role.account_request_codebuild_role.id

  policy = templatefile("${path.module}/iam/role-policies/ct_aft_codebuild_policy_custom.tpl", {
    application_request_table_arn = var.application_request_table_arn
    network_request_table_arn     = var.network_request_table_arn
  })
}
