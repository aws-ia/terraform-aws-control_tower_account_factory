# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
resource "aws_kms_key" "aft" {
  description         = "AFT KMS key"
  enable_key_rotation = "true"
  # Use inline policy instead of 'aws_kms_key_policy' resource
  # to always make sure policy is fully propagated before the key is used
  # e.g. for CloudWatch Log Groups
  policy = jsonencode(
    {
      "Version" : "2012-10-17",
      "Id" : "key-default-1",
      "Statement" : concat([
        {
          "Sid" : "Enable IAM User Permissions",
          "Effect" : "Allow",
          "Principal" : {
            "AWS" : "arn:${data.aws_partition.current.partition}:iam::${data.aws_caller_identity.aft-management.account_id}:root"
          },
          "Action" : "kms:*",
          "Resource" : "*"
          }], var.cloudwatch_log_group_enable_cmk_encryption ? [{
          "Sid" : "Allow CloudWatch Logs access", # Reference: https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/encrypt-log-data-kms.html
          "Effect" : "Allow",
          "Principal" : {
            "Service" : "logs.${data.aws_region.aft-management.name}.amazonaws.com"
          },
          "Action" : [
            "kms:Encrypt",
            "kms:Decrypt",
            "kms:ReEncrypt*",
            "kms:GenerateDataKey*",
            "kms:Describe*"
          ],
          "Resource" : "*",
          "Condition" : {
            "ArnEquals" : {
              # Allow all log groups in AFT Mgmt Account
              "kms:EncryptionContext:aws:logs:arn" : "arn:${data.aws_partition.current.partition}:logs:${data.aws_region.aft-management.name}:${data.aws_caller_identity.aft-management.account_id}:*"
            }
          }
      }] : [])
  })
}


resource "aws_kms_alias" "aft" {
  name          = "alias/aft"
  target_key_id = aws_kms_key.aft.key_id
}
