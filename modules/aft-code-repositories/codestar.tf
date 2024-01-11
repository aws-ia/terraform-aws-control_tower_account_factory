# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
resource "aws_codestarconnections_connection" "bitbucket" {
  count         = local.vcs.is_bitbucket ? 1 : 0
  name          = "ct-aft-bitbucket-connection"
  provider_type = "Bitbucket"
}

resource "aws_codestarconnections_connection" "github" {
  count         = local.vcs.is_github ? 1 : 0
  name          = "ct-aft-github-connection"
  provider_type = "GitHub"
}

resource "aws_codestarconnections_connection" "githubenterprise" {
  count    = local.vcs.is_github_enterprise ? 1 : 0
  name     = "ct-aft-github-ent-connection"
  host_arn = aws_codestarconnections_host.githubenterprise[0].arn
}

resource "aws_codestarconnections_host" "githubenterprise" {
  count             = local.vcs.is_github_enterprise ? 1 : 0
  name              = "github-enterprise-host"
  provider_endpoint = var.github_enterprise_url
  provider_type     = "GitHubEnterpriseServer"

  vpc_configuration {
    security_group_ids = var.security_group_ids
    subnet_ids         = var.subnet_ids
    vpc_id             = var.vpc_id
  }
}
