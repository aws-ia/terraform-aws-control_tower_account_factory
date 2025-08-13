# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
output "bucket_id" {
  description = "The name of the primary bucket."
  value       = aws_s3_bucket.primary-backend-bucket.id
}

output "secondary_bucket_id" {
  description = "The name of the secondary bucket."
  value       = var.secondary_region == "" ? "" : aws_s3_bucket.secondary-backend-bucket[0].id
}

output "access_logs_bucket_id" {
  description = "The name of the access logs bucket for primary bucket."
  value       = aws_s3_bucket.aft_access_logs_primary_backend_bucket.id
}

output "table_id" {
  description = "The name of the primary table."
  value       = aws_dynamodb_table.lock-table.id
}

output "kms_key_id" {
  description = "The globally unique identifier for the primary key."
  value       = aws_kms_key.encrypt-primary-region.key_id
}

output "kms_key_alias_arn" {
  description = "The ARN for the primary key alias."
  value       = aws_kms_alias.encrypt-alias-primary-region.arn
}

output "secondary_kms_key_id" {
  description = "The globally unique identifier for the secondary key."
  value       = var.secondary_region == "" ? "" : aws_kms_key.encrypt-secondary-region[0].key_id
}

output "secondary_kms_key_alias_arn" {
  description = "The ARN for the secondary key alias."
  value       = var.secondary_region == "" ? "" : aws_kms_alias.encrypt-alias-secondary-region[0].arn
}
