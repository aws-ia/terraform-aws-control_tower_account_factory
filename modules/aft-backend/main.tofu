# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
data "aws_caller_identity" "current" {
  provider = aws.primary_region
}

# S3 Resources
#tfsec:ignore:aws-s3-enable-bucket-logging
resource "aws_s3_bucket" "primary-backend-bucket" {
  provider = aws.primary_region

  bucket = "aft-backend-${data.aws_caller_identity.current.account_id}-primary-region"

  tags = {
    "Name" = "aft-backend-${data.aws_caller_identity.current.account_id}-primary-region"
  }
}
resource "aws_s3_bucket_logging" "primary-backend-bucket-logging" {
  provider      = aws.primary_region
  bucket        = aws_s3_bucket.primary-backend-bucket.id
  target_bucket = aws_s3_bucket.aft_access_logs_primary_backend_bucket.id
  target_prefix = "log/"
}

#tfsec:ignore:aws-s3-enable-bucket-logging
resource "aws_s3_bucket" "secondary-backend-bucket" {
  count    = var.secondary_region == "" ? 0 : 1
  provider = aws.secondary_region
  bucket   = "aft-backend-${data.aws_caller_identity.current.account_id}-secondary-region"
  tags = {
    "Name" = "aft-backend-${data.aws_caller_identity.current.account_id}-secondary-region"
  }
}

resource "aws_s3_bucket_replication_configuration" "primary-backend-bucket-replication" {
  count    = var.secondary_region == "" ? 0 : 1
  provider = aws.primary_region
  bucket   = aws_s3_bucket.primary-backend-bucket.id
  role     = aws_iam_role.replication[0].arn

  rule {
    id       = "0"
    priority = "0"
    status   = "Enabled"
    source_selection_criteria {
      sse_kms_encrypted_objects {
        status = "Enabled"
      }
    }

    destination {
      bucket        = aws_s3_bucket.secondary-backend-bucket[0].arn
      storage_class = "STANDARD"
      encryption_configuration {
        replica_kms_key_id = aws_kms_key.encrypt-secondary-region[0].arn
      }
    }
  }
}

resource "aws_s3_bucket_versioning" "primary-backend-bucket-versioning" {
  provider = aws.primary_region
  bucket   = aws_s3_bucket.primary-backend-bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "primary-backend-bucket-encryption" {
  provider = aws.primary_region
  bucket   = aws_s3_bucket.primary-backend-bucket.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.encrypt-primary-region.arn
      sse_algorithm     = "aws:kms"
    }
  }
}


resource "aws_s3_bucket_public_access_block" "primary-backend-bucket" {
  provider = aws.primary_region

  bucket = aws_s3_bucket.primary-backend-bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "secondary-backend-bucket-versioning" {
  count    = var.secondary_region == "" ? 0 : 1
  provider = aws.secondary_region
  bucket   = aws_s3_bucket.secondary-backend-bucket[0].id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "secondary-backend-bucket-encryption" {
  count    = var.secondary_region == "" ? 0 : 1
  provider = aws.secondary_region
  bucket   = aws_s3_bucket.secondary-backend-bucket[0].id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.encrypt-secondary-region[0].arn
      sse_algorithm     = "aws:kms"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "secondary-backend-bucket" {
  count    = var.secondary_region == "" ? 0 : 1
  provider = aws.secondary_region

  bucket = aws_s3_bucket.secondary-backend-bucket[0].id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_iam_role" "replication" {
  count    = var.secondary_region == "" ? 0 : 1
  provider = aws.primary_region
  name     = "aft-s3-terraform-backend-replication"

  assume_role_policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "s3.amazonaws.com"
      },
      "Effect": "Allow"
    }
  ]
}
POLICY
}

resource "aws_iam_policy" "replication" {
  count    = var.secondary_region == "" ? 0 : 1
  provider = aws.primary_region
  name     = "aft-s3-terraform-backend-replication-policy"

  policy = <<POLICY
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": [
                "s3:GetReplicationConfiguration",
                "s3:ListBucket"
            ],
            "Effect": "Allow",
            "Resource": [
                "${aws_s3_bucket.primary-backend-bucket.arn}"
            ]
        },
        {
            "Action": [
                "s3:GetObjectVersionForReplication",
                "s3:GetObjectVersionAcl",
                "s3:GetObjectVersionTagging"
            ],
            "Effect": "Allow",
            "Resource": [
                "${aws_s3_bucket.primary-backend-bucket.arn}/*"
            ]
        },
        {
            "Action": [
                "s3:ReplicateObject",
                "s3:ReplicateDelete",
                "s3:ReplicateTags"
            ],
            "Effect": "Allow",
            "Condition": {
                "StringLikeIfExists": {
                    "s3:x-amz-server-side-encryption": [
                        "aws:kms",
                        "AES256"
                    ],
                    "s3:x-amz-server-side-encryption-aws-kms-key-id": [
                        "${aws_kms_key.encrypt-secondary-region[0].arn}"
                    ]
                }
            },
            "Resource": "${aws_s3_bucket.secondary-backend-bucket[0].arn}/*"
        },
        {
            "Action": [
                "kms:Decrypt"
            ],
            "Effect": "Allow",
            "Condition": {
                "StringLike": {
                    "kms:ViaService": "s3.${var.primary_region}.amazonaws.com",
                    "kms:EncryptionContext:aws:s3:arn": [
                        "${aws_s3_bucket.primary-backend-bucket.arn}/*"
                    ]
                }
            },
            "Resource": [
                "${aws_kms_key.encrypt-primary-region.arn}"
            ]
        },
        {
            "Action": [
                "kms:Encrypt"
            ],
            "Effect": "Allow",
            "Condition": {
                "StringLike": {
                    "kms:ViaService": "s3.${var.primary_region}.amazonaws.com",
                    "kms:EncryptionContext:aws:s3:arn": [
                        "${aws_s3_bucket.primary-backend-bucket.arn}/*"
                    ]
                }
            },
            "Resource": [
                "${aws_kms_key.encrypt-primary-region.arn}"
            ]
        },
        {
            "Action": [
                "kms:Encrypt"
            ],
            "Effect": "Allow",
            "Condition": {
                "StringLike": {
                    "kms:ViaService": "s3.${var.secondary_region}.amazonaws.com",
                    "kms:EncryptionContext:aws:s3:arn": [
                        "${aws_s3_bucket.secondary-backend-bucket[0].arn}/*"
                    ]
                }
            },
            "Resource": [
                "${aws_kms_key.encrypt-secondary-region[0].arn}"
            ]
        }
    ]
}
POLICY
}

resource "aws_iam_role_policy_attachment" "replication" {
  count      = var.secondary_region == "" ? 0 : 1
  provider   = aws.primary_region
  role       = aws_iam_role.replication[0].name
  policy_arn = aws_iam_policy.replication[0].arn
}

#tfsec:ignore:aws-s3-enable-bucket-logging
resource "aws_s3_bucket" "aft_access_logs_primary_backend_bucket" {
  provider = aws.primary_region
  bucket   = "aft-backend-${data.aws_caller_identity.current.account_id}-primary-region-access-logs"
}

resource "aws_s3_bucket_policy" "aft_access_logs_primary_backend_bucket" {
  provider = aws.primary_region
  bucket   = aws_s3_bucket.aft_access_logs_primary_backend_bucket.id
  policy = templatefile("${path.module}/s3/bucket-policies/aft_access_logs_primary_backend_bucket.tpl", {
    aws_s3_bucket_aft_access_logs_arn = aws_s3_bucket.aft_access_logs_primary_backend_bucket.arn
    aws_s3_bucket_primary_backend_arn = aws_s3_bucket.primary-backend-bucket.arn
    aft_management_account_id         = var.aft_management_account_id
  })
}

resource "aws_s3_bucket_versioning" "aft_access_logs_primary_backend_bucket" {
  provider = aws.primary_region
  bucket   = aws_s3_bucket.aft_access_logs_primary_backend_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_kms_key" "aft_access_logs_primary_backend_bucket" {
  provider            = aws.primary_region
  enable_key_rotation = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "aft_access_logs_primary_backend_bucket" {
  provider = aws.primary_region
  bucket   = aws_s3_bucket.aft_access_logs_primary_backend_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.aft_access_logs_primary_backend_bucket.arn
      sse_algorithm     = "aws:kms"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "aft_access_logs_primary_backend_bucket" {
  provider = aws.primary_region
  bucket   = aws_s3_bucket.aft_access_logs_primary_backend_bucket.id
  rule {
    status = "Enabled"
    filter {
      prefix = "log/"
    }
    id = "aft_primary_backend_bucket_access_logs_lifecycle_configuration_rule"

    noncurrent_version_expiration {
      noncurrent_days = var.aft_backend_bucket_access_logs_object_expiration_days
    }
  }

}

resource "aws_s3_bucket_public_access_block" "aft_access_logs_primary_backend_bucket" {
  provider                = aws.primary_region
  bucket                  = aws_s3_bucket.aft_access_logs_primary_backend_bucket.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# DynamoDB Resources
# TFSec incorrectly reports no DAX SSE encryption for a DDB table (SSE encryption is default-on)
# TF locks are transient and do not require restore capabilility
#tfsec:ignore:aws-dynamodb-enable-recovery tfsec:ignore:aws-dynamodb-table-customer-key tfsec:ignore:aws-dynamodb-enable-at-rest-encryption
resource "aws_dynamodb_table" "lock-table" {
  provider = aws.primary_region

  name             = "aft-backend-${data.aws_caller_identity.current.account_id}"
  billing_mode     = "PAY_PER_REQUEST"
  hash_key         = "LockID"
  stream_enabled   = true
  stream_view_type = "NEW_AND_OLD_IMAGES"
  attribute {
    name = "LockID"
    type = "S"
  }

  # If secondary_region is provided, there will be 1 iteration of the dynamic replica block
  # If secondary region is omitted, there will be 0 iteration of the dynamic replica block
  dynamic "replica" {
    for_each = var.secondary_region == "" ? [] : [1]
    content {
      region_name = var.secondary_region
      kms_key_arn = aws_kms_key.encrypt-secondary-region[0].arn
    }
  }

  server_side_encryption {
    enabled     = true
    kms_key_arn = aws_kms_key.encrypt-primary-region.arn
  }

  tags = {
    "Name" = "aft-backend-${data.aws_caller_identity.current.account_id}"
  }
}


# KMS Resources

resource "aws_kms_key" "encrypt-primary-region" {
  provider = aws.primary_region

  description             = "Terraform backend KMS key."
  deletion_window_in_days = 30
  enable_key_rotation     = "true"
  tags = {
    "Name" = "aft-backend-${data.aws_caller_identity.current.account_id}-primary-region-kms-key"
  }
}

resource "aws_kms_alias" "encrypt-alias-primary-region" {
  provider = aws.primary_region

  name          = "alias/aft-backend-${data.aws_caller_identity.current.account_id}-kms-key"
  target_key_id = aws_kms_key.encrypt-primary-region.key_id
}

resource "aws_kms_key" "encrypt-secondary-region" {
  count    = var.secondary_region == "" ? 0 : 1
  provider = aws.secondary_region

  description             = "Terraform backend KMS key."
  deletion_window_in_days = 30
  enable_key_rotation     = "true"
  tags = {
    "Name" = "aft-backend-${data.aws_caller_identity.current.account_id}-secondary-region-kms-key"
  }
}

resource "aws_kms_alias" "encrypt-alias-secondary-region" {
  count    = var.secondary_region == "" ? 0 : 1
  provider = aws.secondary_region

  name          = "alias/aft-backend-${data.aws_caller_identity.current.account_id}-kms-key"
  target_key_id = aws_kms_key.encrypt-secondary-region[0].key_id
}
