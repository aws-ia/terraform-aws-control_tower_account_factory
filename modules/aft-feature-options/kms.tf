# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
resource "aws_kms_key" "aft_log_key" {
  provider            = aws.log_archive
  description         = "KMS key for encrypt/decrypt log files"
  enable_key_rotation = "true"
  policy = templatefile("${path.module}/kms/key-policies/log-key.tpl", {
    log_archive_account_id               = var.log_archive_account_id
    data_aws_partition_current_partition = data.aws_partition.current.partition
  })
}

resource "aws_kms_alias" "aft_log_key_alias" {
  provider = aws.log_archive

  name          = "alias/aft"
  target_key_id = aws_kms_key.aft_log_key.key_id
}
