data "aws_kms_secrets" "mondelez" {
  secret {
    name    = "github_app_private_key"
    payload = file("${path.module}/secrets/${data.aws_caller_identity.current.account_id}/github-app-private-key.pem.enc")
    context = {
      AccountID = data.aws_caller_identity.current.account_id
    }
  }

  secret {
    name    = "spacelift_api_key"
    payload = file("${path.module}/secrets/${data.aws_caller_identity.current.account_id}/spacelift-api-key.enc")
    context = {
      AccountID = data.aws_caller_identity.current.account_id
    }
  }
}
