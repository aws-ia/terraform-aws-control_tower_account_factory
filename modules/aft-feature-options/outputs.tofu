# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
output "aws_aft_access_logs_s3_bucket_id" {
  value       = aws_s3_bucket.aft_access_logs.id
  description = "The name of the bucket."
}

output "aws_aft_access_logs_s3_bucket_arn" {
  value       = aws_s3_bucket.aft_access_logs.arn
  description = "The ARN of the bucket. Will be of format arn:<partition>:s3:::bucketname."
}

output "aws_aft_access_logs_s3_bucket_region" {
  value       = aws_s3_bucket.aft_access_logs.region
  description = "The AWS region this bucket resides in."
}

output "aws_aft_logs_s3_bucket_id" {
  value       = aws_s3_bucket.aft_logging_bucket.id
  description = "The name of the bucket."
}

output "aws_aft_logs_s3_bucket_arn" {
  value       = aws_s3_bucket.aft_logging_bucket.arn
  description = "The ARN of the bucket. Will be of format arn:<partition>:s3:::bucketname."
}

output "aws_aft_logs_s3_bucket_region" {
  value       = aws_s3_bucket.aft_logging_bucket.region
  description = "The AWS region this bucket resides in."
}

output "aws_aft_log_key_arn" {
  value       = aws_kms_key.aft_log_key.arn
  description = "The ARN of the KMS key used to encrypt contents in the Log bucket"
}
