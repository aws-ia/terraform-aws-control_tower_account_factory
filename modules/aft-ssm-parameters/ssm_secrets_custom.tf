# MDLZ CUSTOMIZATION
resource "aws_ssm_parameter" "spacelift_terraformrc" {
  name   = "/aft/config/terraform/spacelift-terraformrc"
  type   = "SecureString"
  value  = data.aws_kms_secrets.spacelift_terraformrc.plaintext.spacelift_terraformrc
  key_id = data.aws_kms_alias.aft.name
}
