# MDLZ CUSTOMIZATION
data "aws_caller_identity" "current" {}

data "aws_kms_alias" "aft" {
  name = "alias/aft"
}

data "aws_kms_secrets" "spacelift_terraformrc" {
  secret {
    name    = "spacelift_terraformrc"
    payload = file("${path.module}/secrets/${data.aws_caller_identity.current.account_id}/spacelift_terraformrc.enc")
    context = {
      AccountID = data.aws_caller_identity.current.account_id
    }
  }
}
