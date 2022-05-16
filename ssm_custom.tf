resource "aws_ssm_parameter" "github_app_credentials" {
  name = "/aft/config/github/app-credentials"
  type = "SecureString"
  value = jsonencode({
    app_id          = 164830
    installation_id = 22274219
    owner           = "mondelez-ctiso"
    pem_file        = data.aws_kms_secrets.mondelez.plaintext.github_app_private_key
  })
  key_id = "alias/aws/ssm"
}

resource "aws_ssm_parameter" "spacelift_api_credentials" {
  name = "/aft/config/spacelift/api-credentials"
  type = "SecureString"
  value = jsonencode({
    api_key_id       = "01FX5W7Z54VYZTE8TYN0X3BJFB",
    api_key_secret   = data.aws_kms_secrets.mondelez.plaintext.spacelift_api_key
    api_key_endpoint = "https://mondelez-ctiso.app.spacelift.io"
  })
  key_id = "alias/aws/ssm"
}
