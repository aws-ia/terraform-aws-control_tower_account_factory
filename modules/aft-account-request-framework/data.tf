# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
data "aws_partition" "current" {}

data "aws_region" "aft-management" {}

data "aws_caller_identity" "aft-management" {}

data "aws_caller_identity" "ct-management" {
  provider = aws.ct_management
}

data "aws_iam_policy" "AWSLambdaBasicExecutionRole" {
  name = "AWSLambdaBasicExecutionRole"
}

data "aws_iam_policy" "AWSLambdaVPCAccessExecutionRole" {
  name = "AWSLambdaVPCAccessExecutionRole"
}

data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_vpc" "aft" {
  id = local.vpc_id
}

# Lookup route tables associated to customer provided subnets 
# for Gateway endpoint deployments
data "aws_route_tables" "aft_private_route_tables" {
  count = local.vpc_deployment && var.aft_vpc_endpoints ? 1 : 0

  vpc_id = local.vpc_id

  filter {
    name   = "association.subnet-id"
    values = local.vpc_private_subnet_ids
  }
}

data "aws_route_tables" "aft_public_route_tables" {
  count = local.vpc_deployment && var.aft_vpc_endpoints ? 1 : 0

  vpc_id = local.vpc_id

  filter {
    name   = "association.subnet-id"
    values = local.vpc_public_subnet_ids
  }
}

######################################
# VPC Endpoints
######################################

#### CodeBuild ####

data "aws_vpc_endpoint_service" "codebuild" {
  count   = local.vpc_deployment && var.aft_vpc_endpoints ? 1 : 0
  service = "codebuild"
}

data "aws_subnets" "codebuild" {
  count = local.vpc_deployment && var.aft_vpc_endpoints ? 1 : 0

  filter {
    name   = "vpc-id"
    values = [local.vpc_id]
  }

  filter {
    name   = "subnet-id"
    values = local.vpc_private_subnet_ids
  }

  filter {
    name   = "availability-zone"
    values = data.aws_vpc_endpoint_service.codebuild[0].availability_zones
  }
}

#### CodeCommit ####

data "aws_vpc_endpoint_service" "codecommit" {
  count   = local.vpc_deployment && var.aft_vpc_endpoints ? 1 : 0
  service = "codecommit"
}

data "aws_subnets" "codecommit" {
  count = local.vpc_deployment && var.aft_vpc_endpoints ? 1 : 0
  filter {
    name   = "vpc-id"
    values = [local.vpc_id]
  }

  filter {
    name   = "subnet-id"
    values = local.vpc_private_subnet_ids
  }

  filter {
    name   = "availability-zone"
    values = data.aws_vpc_endpoint_service.codecommit[0].availability_zones
  }
}

#### git-codecommit ####

data "aws_vpc_endpoint_service" "git-codecommit" {
  count   = local.vpc_deployment && var.aft_vpc_endpoints ? 1 : 0
  service = "git-codecommit"
}

data "aws_subnets" "git-codecommit" {

  count = local.vpc_deployment && var.aft_vpc_endpoints ? 1 : 0
  filter {
    name   = "vpc-id"
    values = [local.vpc_id]
  }

  filter {
    name   = "subnet-id"
    values = local.vpc_private_subnet_ids
  }

  filter {
    name   = "availability-zone"
    values = data.aws_vpc_endpoint_service.git-codecommit[0].availability_zones
  }
}

#### codepipeline ####

data "aws_vpc_endpoint_service" "codepipeline" {
  count   = local.vpc_deployment && var.aft_vpc_endpoints ? 1 : 0
  service = "codepipeline"
}

data "aws_subnets" "codepipeline" {
  count = local.vpc_deployment && var.aft_vpc_endpoints ? 1 : 0

  filter {
    name   = "vpc-id"
    values = [local.vpc_id]
  }

  filter {
    name   = "subnet-id"
    values = local.vpc_private_subnet_ids
  }

  filter {
    name   = "availability-zone"
    values = data.aws_vpc_endpoint_service.codepipeline[0].availability_zones
  }
}

#### servicecatalog ####

data "aws_vpc_endpoint_service" "servicecatalog" {
  count   = local.vpc_deployment && var.aft_vpc_endpoints ? 1 : 0
  service = "servicecatalog"
}

data "aws_subnets" "servicecatalog" {
  count = local.vpc_deployment && var.aft_vpc_endpoints ? 1 : 0
  filter {
    name   = "vpc-id"
    values = [local.vpc_id]
  }

  filter {
    name   = "subnet-id"
    values = local.vpc_private_subnet_ids
  }

  filter {
    name   = "availability-zone"
    values = data.aws_vpc_endpoint_service.servicecatalog[0].availability_zones
  }
}

#### lambda ####

data "aws_vpc_endpoint_service" "lambda" {
  count   = local.vpc_deployment && var.aft_vpc_endpoints ? 1 : 0
  service = "lambda"
}

data "aws_subnets" "lambda" {
  count = local.vpc_deployment && var.aft_vpc_endpoints ? 1 : 0
  filter {
    name   = "vpc-id"
    values = [local.vpc_id]
  }
  filter {
    name   = "subnet-id"
    values = local.vpc_private_subnet_ids
  }

  filter {
    name   = "availability-zone"
    values = data.aws_vpc_endpoint_service.lambda[0].availability_zones
  }
}

#### kms ####

data "aws_vpc_endpoint_service" "kms" {
  count   = local.vpc_deployment && var.aft_vpc_endpoints ? 1 : 0
  service = "kms"
}

data "aws_subnets" "kms" {
  count = local.vpc_deployment && var.aft_vpc_endpoints ? 1 : 0
  filter {
    name   = "vpc-id"
    values = [local.vpc_id]
  }

  filter {
    name   = "subnet-id"
    values = local.vpc_private_subnet_ids
  }

  filter {
    name   = "availability-zone"
    values = data.aws_vpc_endpoint_service.kms[0].availability_zones
  }
}

#### logs ####

data "aws_vpc_endpoint_service" "logs" {
  count   = local.vpc_deployment && var.aft_vpc_endpoints ? 1 : 0
  service = "logs"
}

data "aws_subnets" "logs" {

  count = local.vpc_deployment && var.aft_vpc_endpoints ? 1 : 0
  filter {
    name   = "vpc-id"
    values = [local.vpc_id]
  }
  filter {
    name   = "subnet-id"
    values = local.vpc_private_subnet_ids
  }

  filter {
    name   = "availability-zone"
    values = data.aws_vpc_endpoint_service.logs[0].availability_zones
  }
}

#### events ####

data "aws_vpc_endpoint_service" "events" {
  count   = local.vpc_deployment && var.aft_vpc_endpoints ? 1 : 0
  service = "events"
}

data "aws_subnets" "events" {
  count = local.vpc_deployment && var.aft_vpc_endpoints ? 1 : 0
  filter {
    name   = "vpc-id"
    values = [local.vpc_id]
  }

  filter {
    name   = "subnet-id"
    values = local.vpc_private_subnet_ids
  }

  filter {
    name   = "availability-zone"
    values = data.aws_vpc_endpoint_service.events[0].availability_zones
  }
}

#### organizations ####

data "aws_vpc_endpoint_service" "organizations" {
  count   = local.vpc_deployment && var.aft_vpc_endpoints && local.orgs_endpoint_supported ? 1 : 0
  service = "organizations"
}

data "aws_subnets" "organizations" {
  count = local.vpc_deployment && var.aft_vpc_endpoints && local.orgs_endpoint_supported ? 1 : 0

  filter {
    name   = "vpc-id"
    values = [local.vpc_id]
  }

  filter {
    name   = "subnet-id"
    values = local.vpc_private_subnet_ids
  }

  filter {
    name   = "availability-zone"
    values = data.aws_vpc_endpoint_service.organizations[0].availability_zones
  }
}

#### states ####

data "aws_vpc_endpoint_service" "states" {
  count   = local.vpc_deployment && var.aft_vpc_endpoints ? 1 : 0
  service = "states"
}

data "aws_subnets" "states" {
  count = local.vpc_deployment && var.aft_vpc_endpoints ? 1 : 0
  filter {
    name   = "vpc-id"
    values = [local.vpc_id]
  }
  filter {
    name   = "subnet-id"
    values = local.vpc_private_subnet_ids
  }

  filter {
    name   = "availability-zone"
    values = data.aws_vpc_endpoint_service.states[0].availability_zones
  }
}

#### ssm ####

data "aws_vpc_endpoint_service" "ssm" {
  count   = local.vpc_deployment && var.aft_vpc_endpoints ? 1 : 0
  service = "ssm"
}

data "aws_subnets" "ssm" {

  count = local.vpc_deployment && var.aft_vpc_endpoints ? 1 : 0
  filter {
    name   = "vpc-id"
    values = [local.vpc_id]
  }

  filter {
    name   = "subnet-id"
    values = local.vpc_private_subnet_ids
  }

  filter {
    name   = "availability-zone"
    values = data.aws_vpc_endpoint_service.ssm[0].availability_zones
  }
}

#### sns ####

data "aws_vpc_endpoint_service" "sns" {
  count   = local.vpc_deployment && var.aft_vpc_endpoints ? 1 : 0
  service = "sns"
}

data "aws_subnets" "sns" {
  count = local.vpc_deployment && var.aft_vpc_endpoints ? 1 : 0
  filter {
    name   = "vpc-id"
    values = [local.vpc_id]
  }

  filter {
    name   = "subnet-id"
    values = local.vpc_private_subnet_ids
  }

  filter {
    name   = "availability-zone"
    values = data.aws_vpc_endpoint_service.sns[0].availability_zones
  }
}

#### sqs ####

data "aws_vpc_endpoint_service" "sqs" {
  count   = local.vpc_deployment && var.aft_vpc_endpoints ? 1 : 0
  service = "sqs"
}

data "aws_subnets" "sqs" {
  count = local.vpc_deployment && var.aft_vpc_endpoints ? 1 : 0
  filter {
    name   = "vpc-id"
    values = [local.vpc_id]
  }

  filter {
    name   = "subnet-id"
    values = local.vpc_private_subnet_ids
  }

  filter {
    name   = "availability-zone"
    values = data.aws_vpc_endpoint_service.sqs[0].availability_zones
  }
}

#### sts ####

data "aws_vpc_endpoint_service" "sts" {
  count   = local.vpc_deployment && var.aft_vpc_endpoints ? 1 : 0
  service = "sts"
}

data "aws_subnets" "sts" {
  count = local.vpc_deployment && var.aft_vpc_endpoints ? 1 : 0
  filter {
    name   = "vpc-id"
    values = [local.vpc_id]
  }

  filter {
    name   = "subnet-id"
    values = local.vpc_private_subnet_ids
  }

  filter {
    name   = "availability-zone"
    values = data.aws_vpc_endpoint_service.sts[0].availability_zones
  }
}
