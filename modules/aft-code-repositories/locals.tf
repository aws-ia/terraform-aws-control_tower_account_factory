# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
locals {
  vcs = {
    is_codecommit        = lower(var.vcs_provider) == "codecommit" ? true : false
    is_s3                = lower(var.vcs_provider) == "s3" ? true : false
    is_bitbucket         = lower(var.vcs_provider) == "bitbucket" ? true : false
    is_github            = lower(var.vcs_provider) == "github" ? true : false
    is_github_enterprise = lower(var.vcs_provider) == "githubenterprise" ? true : false
  }
  connection_arn = {
    bitbucket        = lower(var.vcs_provider) == "bitbucket" ? aws_codestarconnections_connection.bitbucket[0].arn : ""
    github           = lower(var.vcs_provider) == "github" ? aws_codestarconnections_connection.github[0].arn : ""
    githubenterprise = lower(var.vcs_provider) == "githubenterprise" ? aws_codestarconnections_connection.githubenterprise[0].arn : ""
    codecommit       = "null"
  }
}
