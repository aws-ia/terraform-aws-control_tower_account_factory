# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
resource "aws_sns_topic" "aft_notifications" {
  name              = "aft-notifications"
  kms_master_key_id = "alias/aws/sns" #tfsec:ignore:aws-sns-topic-encryption-use-cmk
}

resource "aws_sns_topic" "aft_failure_notifications" {
  name              = "aft-failure-notifications"
  kms_master_key_id = "alias/aws/sns" #tfsec:ignore:aws-sns-topic-encryption-use-cmk
}
