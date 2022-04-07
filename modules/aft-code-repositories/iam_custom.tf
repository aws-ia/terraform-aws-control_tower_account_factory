# MDLZ CUSTOMIZATION
resource "aws_iam_role_policy" "account_request_codebuild_policy_custom" {
  name = "ct-aft-codebuild-account-request-policy-custom"
  role = aws_iam_role.account_request_codebuild_role.id

  policy = templatefile("${path.module}/iam/role-policies/ct_aft_codebuild_policy_custom.tpl", {
    data_aws_region_current_name                = data.aws_region.current.name
    data_aws_caller_identity_current_account_id = data.aws_caller_identity.current.account_id
    data_aws_dynamo_application_request_table   = var.application_request_table_name
  })
}
