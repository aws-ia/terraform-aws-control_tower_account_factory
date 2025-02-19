# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

resource "aws_iam_role" "role" {
  name = var.role_name

  assume_role_policy = templatefile("${path.module}/trust_policy.tpl",
    {
      trusted_entity_type        = var.trusted_entity_type
      trusted_entity             = var.trusted_entity
      aft_admin_assumed_role_arn = var.aft_admin_session_arn
    }
  )
}

resource "aws_iam_role_policy_attachment" "administrator-access-attachment" {
  role       = aws_iam_role.role.name
  policy_arn = "arn:${data.aws_partition.current.partition}:iam::aws:policy/AdministratorAccess"
}

data "aws_iam_policy_document" "cross_account_secret_access" {
  statement {
    sid    = "CrossAccountAccessKMS"
    effect = "Allow"
    actions = [
      "kms:Decrypt",
      "kms:DescribeKey",
    ]
    resources = ["arn:aws:kms:us-east-1:232020727462:key/de189df0-e928-4f00-89a8-19cc43776822"]
  }

  statement {
    sid    = "CrossAccountAccessSecretsManager"
    effect = "Allow"
    actions = [
      "secretsmanager:DescribeSecret",
      "secretsmanager:GetSecretValue",
    ]
    resources = ["arn:aws:secretsmanager:us-east-1:232020727462:secret:opentofu-github-pat-for-flux-terraform-provider-20240928210314109300000001-6WHEIx"]
  }
}

resource "aws_iam_policy" "cross_account_secret_access" {
  name        = "cross-account-secret-access"
  description = "Allows access to secrets in the secret manager"
  policy      = data.aws_iam_policy_document.cross_account_secret_access.json
}

resource "aws_iam_role_policy_attachment" "cross_account_secret_access" {
  role       = aws_iam_role.role.name
  policy_arn = aws_iam_policy.cross_account_secret_access.arn
}
