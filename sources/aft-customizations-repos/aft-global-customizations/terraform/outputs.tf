
output "key_arn" {
  value = aws_kms_key.kms-primary.arn
}
output "key_id" {
  value = aws_kms_key.kms-primary.id
}
output "key_alias_id" {
  value = aws_kms_alias.alias.arn
}
output "key_alias_arn" {
  value = aws_kms_alias.alias.target_key_arn
}
