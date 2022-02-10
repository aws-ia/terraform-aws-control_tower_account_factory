# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#
resource "aws_sqs_queue" "aft_account_request" {
  name                              = "aft-account-request.fifo"
  fifo_queue                        = true
  kms_master_key_id                 = aws_kms_alias.aft.name
  visibility_timeout_seconds        = 240
  kms_data_key_reuse_period_seconds = 300
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.aft_account_request_dlq.arn
    maxReceiveCount     = 1
  })
}

resource "aws_sqs_queue" "aft_account_request_dlq" {
  name                              = "aft-account-request-dlq.fifo"
  fifo_queue                        = true
  kms_master_key_id                 = aws_kms_alias.aft.name
  kms_data_key_reuse_period_seconds = 300
}
