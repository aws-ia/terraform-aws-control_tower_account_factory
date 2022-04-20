resource "aws_kms_key" "kms-primary" {
  multi_region        = true
  description         = "multiple region KMS key"
  enable_key_rotation = true
  #policy              = data.aws_iam_policy_document.kms-test.json
  
  tags = merge(
    var.tags,
    {
      "Multi-Region" = "true",
      "Primary"      = "true"
    }
  )

}

resource "aws_kms_alias" "alias" {
  name          = "alias/${var.aws_region}-kms-key"
  target_key_id = aws_kms_key.kms-primary.key_id
}

resource "aws_kms_replica_key" "replica1" {
  provider = aws.replica

  description             = "kms key description"
  primary_key_arn         = aws_kms_key.kms-primary.arn
 # policy                  = data.aws_iam_policy_document.kms-test.json

  tags = merge(
    var.tags,
    {
      "Multi-Region" = "true",
      "Primary"      = "false"
    }
  )

}

# Add an alias to the replica key
resource "aws_kms_alias" "replica1" {
  provider = aws.replica

  name          = "alias/${var.replica_region}-kms-key"
  target_key_id = aws_kms_replica_key.replica1.key_id
}


resource "aws_kms_replica_key" "replica2" {
  provider = aws.replica2

  description             = "kms key description"
  primary_key_arn         = aws_kms_key.kms-primary.arn
  #policy                  = data.aws_iam_policy_document.kms-test.json

  tags = merge(
    var.tags,
    {
      "Multi-Region" = "true",
      "Primary"      = "false"
    }
  )
  
}
# Add an alias to the replica key
resource "aws_kms_alias" "replica2" {
  provider = aws.replica2

  name          = "alias/${var.replica_region2}-kms-key"
  target_key_id = aws_kms_replica_key.replica2.key_id
}

