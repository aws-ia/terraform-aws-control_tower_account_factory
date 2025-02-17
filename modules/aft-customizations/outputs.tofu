# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
output "aft_customizations_identify_targets_function_arn" {
  value = aws_lambda_function.aft_customizations_identify_targets.arn
}

output "aft_customizations_execute_pipeline_function_arn" {
  value = aws_lambda_function.aft_customizations_execute_pipeline.arn
}

output "aft_customizations_get_pipeline_executions_function_arn" {
  value = aws_lambda_function.aft_customizations_get_pipeline_executions.arn
}

output "aft_codepipeline_customizations_bucket_name" {
  value = aws_s3_bucket.aft_codepipeline_customizations_bucket.id
}

output "aft_codepipeline_customizations_bucket_arn" {
  value = aws_s3_bucket.aft_codepipeline_customizations_bucket.arn
}
