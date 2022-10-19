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

######################################
# VPC Endpoints
######################################

#### CodeBuild ####

data "aws_vpc_endpoint_service" "codebuild" {
  count   = var.aft_vpc_endpoints ? 1 : 0
  service = "codebuild"
}

data "aws_subnets" "codebuild" {
  count = var.aft_vpc_endpoints ? 1 : 0

  filter {
    name   = "vpc-id"
    values = [aws_vpc.aft_vpc.id]
  }

  filter {
    name   = "subnet-id"
    values = [aws_subnet.aft_vpc_private_subnet_01.id, aws_subnet.aft_vpc_private_subnet_02.id]
  }

  filter {
    name   = "availability-zone"
    values = data.aws_vpc_endpoint_service.codebuild[0].availability_zones
  }
}

#### CodeCommit ####

data "aws_vpc_endpoint_service" "codecommit" {
  count   = var.aft_vpc_endpoints ? 1 : 0
  service = "codecommit"
}

data "aws_subnets" "codecommit" {
  count = var.aft_vpc_endpoints ? 1 : 0
  filter {
    name   = "vpc-id"
    values = [aws_vpc.aft_vpc.id]
  }

  filter {
    name   = "subnet-id"
    values = [aws_subnet.aft_vpc_private_subnet_01.id, aws_subnet.aft_vpc_private_subnet_02.id]
  }

  filter {
    name   = "availability-zone"
    values = data.aws_vpc_endpoint_service.codecommit[0].availability_zones
  }
}

#### git-codecommit ####

data "aws_vpc_endpoint_service" "git-codecommit" {
  count   = var.aft_vpc_endpoints ? 1 : 0
  service = "git-codecommit"
}

data "aws_subnets" "git-codecommit" {

  count = var.aft_vpc_endpoints ? 1 : 0
  filter {
    name   = "vpc-id"
    values = [aws_vpc.aft_vpc.id]
  }

  filter {
    name   = "subnet-id"
    values = [aws_subnet.aft_vpc_private_subnet_01.id, aws_subnet.aft_vpc_private_subnet_02.id]
  }

  filter {
    name   = "availability-zone"
    values = data.aws_vpc_endpoint_service.git-codecommit[0].availability_zones
  }
}

#### codepipeline ####

data "aws_vpc_endpoint_service" "codepipeline" {
  count   = var.aft_vpc_endpoints ? 1 : 0
  service = "codepipeline"
}

data "aws_subnets" "codepipeline" {
  count = var.aft_vpc_endpoints ? 1 : 0

  filter {
    name   = "vpc-id"
    values = [aws_vpc.aft_vpc.id]
  }

  filter {
    name   = "subnet-id"
    values = [aws_subnet.aft_vpc_private_subnet_01.id, aws_subnet.aft_vpc_private_subnet_02.id]
  }

  filter {
    name   = "availability-zone"
    values = data.aws_vpc_endpoint_service.codepipeline[0].availability_zones
  }
}

#### servicecatalog ####

data "aws_vpc_endpoint_service" "servicecatalog" {
  count   = var.aft_vpc_endpoints ? 1 : 0
  service = "servicecatalog"
}

data "aws_subnets" "servicecatalog" {
  count = var.aft_vpc_endpoints ? 1 : 0
  filter {
    name   = "vpc-id"
    values = [aws_vpc.aft_vpc.id]
  }

  filter {
    name   = "subnet-id"
    values = [aws_subnet.aft_vpc_private_subnet_01.id, aws_subnet.aft_vpc_private_subnet_02.id]
  }

  filter {
    name   = "availability-zone"
    values = data.aws_vpc_endpoint_service.servicecatalog[0].availability_zones
  }
}

#### lambda ####

data "aws_vpc_endpoint_service" "lambda" {
  count   = var.aft_vpc_endpoints ? 1 : 0
  service = "lambda"
}

data "aws_subnets" "lambda" {
  count = var.aft_vpc_endpoints ? 1 : 0
  filter {
    name   = "vpc-id"
    values = [aws_vpc.aft_vpc.id]
  }
  filter {
    name   = "subnet-id"
    values = [aws_subnet.aft_vpc_private_subnet_01.id, aws_subnet.aft_vpc_private_subnet_02.id]
  }

  filter {
    name   = "availability-zone"
    values = data.aws_vpc_endpoint_service.lambda[0].availability_zones
  }
}

#### kms ####

data "aws_vpc_endpoint_service" "kms" {
  count   = var.aft_vpc_endpoints ? 1 : 0
  service = "kms"
}

data "aws_subnets" "kms" {
  count = var.aft_vpc_endpoints ? 1 : 0
  filter {
    name   = "vpc-id"
    values = [aws_vpc.aft_vpc.id]
  }

  filter {
    name   = "subnet-id"
    values = [aws_subnet.aft_vpc_private_subnet_01.id, aws_subnet.aft_vpc_private_subnet_02.id]
  }

  filter {
    name   = "availability-zone"
    values = data.aws_vpc_endpoint_service.kms[0].availability_zones
  }
}

#### logs ####

data "aws_vpc_endpoint_service" "logs" {
  count   = var.aft_vpc_endpoints ? 1 : 0
  service = "logs"
}

data "aws_subnets" "logs" {

  count = var.aft_vpc_endpoints ? 1 : 0
  filter {
    name   = "vpc-id"
    values = [aws_vpc.aft_vpc.id]
  }
  filter {
    name   = "subnet-id"
    values = [aws_subnet.aft_vpc_private_subnet_01.id, aws_subnet.aft_vpc_private_subnet_02.id]
  }

  filter {
    name   = "availability-zone"
    values = data.aws_vpc_endpoint_service.logs[0].availability_zones
  }
}

#### events ####

data "aws_vpc_endpoint_service" "events" {
  count   = var.aft_vpc_endpoints ? 1 : 0
  service = "events"
}

data "aws_subnets" "events" {
  count = var.aft_vpc_endpoints ? 1 : 0
  filter {
    name   = "vpc-id"
    values = [aws_vpc.aft_vpc.id]
  }

  filter {
    name   = "subnet-id"
    values = [aws_subnet.aft_vpc_private_subnet_01.id, aws_subnet.aft_vpc_private_subnet_02.id]
  }

  filter {
    name   = "availability-zone"
    values = data.aws_vpc_endpoint_service.events[0].availability_zones
  }
}

#### states ####

data "aws_vpc_endpoint_service" "states" {
  count   = var.aft_vpc_endpoints ? 1 : 0
  service = "states"
}

data "aws_subnets" "states" {
  count = var.aft_vpc_endpoints ? 1 : 0
  filter {
    name   = "vpc-id"
    values = [aws_vpc.aft_vpc.id]
  }
  filter {
    name   = "subnet-id"
    values = [aws_subnet.aft_vpc_private_subnet_01.id, aws_subnet.aft_vpc_private_subnet_02.id]
  }

  filter {
    name   = "availability-zone"
    values = data.aws_vpc_endpoint_service.states[0].availability_zones
  }
}

#### ssm ####

data "aws_vpc_endpoint_service" "ssm" {
  count   = var.aft_vpc_endpoints ? 1 : 0
  service = "ssm"
}

data "aws_subnets" "ssm" {

  count = var.aft_vpc_endpoints ? 1 : 0
  filter {
    name   = "vpc-id"
    values = [aws_vpc.aft_vpc.id]
  }

  filter {
    name   = "subnet-id"
    values = [aws_subnet.aft_vpc_private_subnet_01.id, aws_subnet.aft_vpc_private_subnet_02.id]
  }

  filter {
    name   = "availability-zone"
    values = data.aws_vpc_endpoint_service.ssm[0].availability_zones
  }
}

#### sns ####

data "aws_vpc_endpoint_service" "sns" {
  count   = var.aft_vpc_endpoints ? 1 : 0
  service = "sns"
}

data "aws_subnets" "sns" {
  count = var.aft_vpc_endpoints ? 1 : 0
  filter {
    name   = "vpc-id"
    values = [aws_vpc.aft_vpc.id]
  }

  filter {
    name   = "subnet-id"
    values = [aws_subnet.aft_vpc_private_subnet_01.id, aws_subnet.aft_vpc_private_subnet_02.id]
  }

  filter {
    name   = "availability-zone"
    values = data.aws_vpc_endpoint_service.sns[0].availability_zones
  }
}

#### sqs ####

data "aws_vpc_endpoint_service" "sqs" {
  count   = var.aft_vpc_endpoints ? 1 : 0
  service = "sqs"
}

data "aws_subnets" "sqs" {
  count = var.aft_vpc_endpoints ? 1 : 0
  filter {
    name   = "vpc-id"
    values = [aws_vpc.aft_vpc.id]
  }

  filter {
    name   = "subnet-id"
    values = [aws_subnet.aft_vpc_private_subnet_01.id, aws_subnet.aft_vpc_private_subnet_02.id]
  }

  filter {
    name   = "availability-zone"
    values = data.aws_vpc_endpoint_service.sqs[0].availability_zones
  }
}

#### sts ####

data "aws_vpc_endpoint_service" "sts" {
  count   = var.aft_vpc_endpoints ? 1 : 0
  service = "sts"
}

data "aws_subnets" "sts" {
  count = var.aft_vpc_endpoints ? 1 : 0
  filter {
    name   = "vpc-id"
    values = [aws_vpc.aft_vpc.id]
  }

  filter {
    name   = "subnet-id"
    values = [aws_subnet.aft_vpc_private_subnet_01.id, aws_subnet.aft_vpc_private_subnet_02.id]
  }

  filter {
    name   = "availability-zone"
    values = data.aws_vpc_endpoint_service.sts[0].availability_zones
  }
}
