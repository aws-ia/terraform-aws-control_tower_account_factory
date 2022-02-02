data "aws_caller_identity" "current" {
  provider = aws.primary_region
}

# S3 Resources

resource "aws_s3_bucket" "primary-backend-bucket" {
  provider = aws.primary_region

  bucket = "aft-backend-${data.aws_caller_identity.current.account_id}-primary-region"
  acl    = "private"

  versioning {
    enabled = true
  }
  replication_configuration {
    role = aws_iam_role.replication.arn

    rules {
      id       = "0"
      priority = "0"
      status   = "Enabled"
      source_selection_criteria {
        sse_kms_encrypted_objects {
          enabled = true
        }
      }

      destination {
        bucket             = aws_s3_bucket.secondary-backend-bucket.arn
        storage_class      = "STANDARD"
        replica_kms_key_id = aws_kms_key.encrypt-secondary-region.arn
      }
    }
  }
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        kms_master_key_id = aws_kms_key.encrypt-primary-region.arn
        sse_algorithm     = "aws:kms"
      }
    }
  }
  tags = {
    "Name" = "aft-backend-${data.aws_caller_identity.current.account_id}-primary-region"
  }
}

resource "aws_s3_bucket_policy" "allow_AWSAFTExecution_role_primary" {
  bucket = aws_s3_bucket.primary-backend-bucket.id
  policy = data.aws_iam_policy_document.allow_AWSAFTExecution_primary.json
}

data "aws_iam_policy_document" "allow_AWSAFTExecution_primary" {
  statement {
    principals {
      type        = "AWS"
      identifiers = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/AWSAFTExecution"
    }

    actions = [
      "s3:GetObject",
      "s3:GetObjectVersion",
      "s3:GetBucketVersioning",
      "s3:List*",
      "s3:PutObjectAcl",
      "s3:PutObject"
    ]

    resources = [
      aws_s3_bucket.primary-backend-bucket.arn,
      "${aws_s3_bucket.primary-backend-bucket.arn}/*",
    ]
  }
}

resource "aws_s3_bucket_public_access_block" "primary-backend-bucket" {
  provider = aws.primary_region

  bucket = aws_s3_bucket.primary-backend-bucket.id

  block_public_acls   = true
  block_public_policy = true
}

resource "aws_s3_bucket" "secondary-backend-bucket" {
  provider = aws.secondary_region

  bucket = "aft-backend-${data.aws_caller_identity.current.account_id}-secondary-region"
  acl    = "private"

  versioning {
    enabled = true
  }
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        kms_master_key_id = aws_kms_key.encrypt-secondary-region.arn
        sse_algorithm     = "aws:kms"
      }
    }
  }
  tags = {
    "Name" = "aft-backend-${data.aws_caller_identity.current.account_id}-secondary-region"
  }
}

resource "aws_s3_bucket_policy" "allow_AWSAFTExecution_role_secondary" {
  bucket = aws_s3_bucket.secondary-backend-bucket.id
  policy = data.aws_iam_policy_document.allow_AWSAFTExecution_secondary.json
}

data "aws_iam_policy_document" "allow_AWSAFTExecution_primary" {
  statement {
    principals {
      type        = "AWS"
      identifiers = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/AWSAFTExecution"
    }

    actions = [
      "s3:GetObject",
      "s3:GetObjectVersion",
      "s3:GetBucketVersioning",
      "s3:List*",
      "s3:PutObjectAcl",
      "s3:PutObject"
    ]

    resources = [
      aws_s3_bucket.secondary-backend-bucket.arn,
      "${aws_s3_bucket.secondary-backend-bucket.arn}/*",
    ]
  }
}

resource "aws_s3_bucket_public_access_block" "secondary-backend-bucket" {
  provider = aws.secondary_region

  bucket = aws_s3_bucket.secondary-backend-bucket.id

  block_public_acls   = true
  block_public_policy = true
}

resource "aws_iam_role" "replication" {
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
                        "${aws_kms_key.encrypt-secondary-region.arn}"
                    ]
                }
            },
            "Resource": "${aws_s3_bucket.secondary-backend-bucket.arn}/*"
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
                        "${aws_s3_bucket.secondary-backend-bucket.arn}/*"
                    ]
                }
            },
            "Resource": [
                "${aws_kms_key.encrypt-secondary-region.arn}"
            ]
        }
    ]
}
POLICY
}

resource "aws_iam_role_policy_attachment" "replication" {
  provider   = aws.primary_region
  role       = aws_iam_role.replication.name
  policy_arn = aws_iam_policy.replication.arn
}


# DynamoDB Resources
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

  replica {
    region_name = var.secondary_region
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
  provider = aws.secondary_region

  description             = "Terraform backend KMS key."
  deletion_window_in_days = 30
  enable_key_rotation     = "true"
  tags = {
    "Name" = "aft-backend-${data.aws_caller_identity.current.account_id}-secondary-region-kms-key"
  }
}

resource "aws_kms_alias" "encrypt-alias-secondary-region" {
  provider = aws.secondary_region

  name          = "alias/aft-backend-${data.aws_caller_identity.current.account_id}-kms-key"
  target_key_id = aws_kms_key.encrypt-secondary-region.key_id
}
