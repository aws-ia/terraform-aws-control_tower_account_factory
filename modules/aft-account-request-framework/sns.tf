# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
resource "aws_sns_topic" "aft_notifications" {
  name = "aft-notifications"
  #tfsec:ignore:aws-sns-topic-encryption-use-cmk
  kms_master_key_id = var.sns_topic_enable_cmk_encryption ? aws_kms_key.aft.id : "alias/aws/sns"
}

resource "aws_sns_topic" "aft_failure_notifications" {
  name = "aft-failure-notifications"
  #tfsec:ignore:aws-sns-topic-encryption-use-cmk
  kms_master_key_id = var.sns_topic_enable_cmk_encryption ? aws_kms_key.aft.id : "alias/aws/sns"
}
