# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
resource "aws_sns_topic" "aft_codepipeline_customizations_notifications" {
  name              = "aft-codepipeline-notifications"
  kms_master_key_id = "alias/aws/sns" #tfsec:ignore:aws-sns-topic-encryption-use-cmk
}