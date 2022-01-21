resource "aws_kms_key" "aft" {
  description         = "AFT KMS key"
  enable_key_rotation = "true"
}
resource "aws_kms_alias" "aft" {
  name          = "alias/aft"
  target_key_id = aws_kms_key.aft.key_id
}
