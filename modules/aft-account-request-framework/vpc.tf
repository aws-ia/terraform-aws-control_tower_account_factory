# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

# TODO: Remove this tfsec-ignore when VPC flow logs are enabled
#tfsec:ignore:aws-ec2-require-vpc-flow-logs-for-all-vpcs
resource "aws_vpc" "aft_vpc" {
  cidr_block           = var.aft_vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags = {
    Name = "aft-management-vpc"
  }
}

#########################################
# VPC Subnets
#########################################

resource "aws_subnet" "aft_vpc_private_subnet_01" {
  count             = var.aft_feature_disable_private_networking ? 0 : 1
  vpc_id            = aws_vpc.aft_vpc.id
  cidr_block        = var.aft_vpc_private_subnet_01_cidr
  availability_zone = element(data.aws_availability_zones.available.names, 0)
  tags = {
    Name = "aft-vpc-private-subnet-01"
  }
}

resource "aws_subnet" "aft_vpc_private_subnet_02" {
  count             = var.aft_feature_disable_private_networking ? 0 : 1
  vpc_id            = aws_vpc.aft_vpc.id
  cidr_block        = var.aft_vpc_private_subnet_02_cidr
  availability_zone = element(data.aws_availability_zones.available.names, 1)
  tags = {
    Name = "aft-vpc-private-subnet-02"
  }
}

resource "aws_subnet" "aft_vpc_public_subnet_01" {
  vpc_id            = aws_vpc.aft_vpc.id
  cidr_block        = var.aft_vpc_public_subnet_01_cidr
  availability_zone = element(data.aws_availability_zones.available.names, 0)
  tags = {
    Name = "aft-vpc-public-subnet-01"
  }
}

resource "aws_subnet" "aft_vpc_public_subnet_02" {
  vpc_id            = aws_vpc.aft_vpc.id
  cidr_block        = var.aft_vpc_public_subnet_02_cidr
  availability_zone = element(data.aws_availability_zones.available.names, 1)
  tags = {
    Name = "aft-vpc-public-subnet-02"
  }
}


#########################################
# Route Tables
#########################################

resource "aws_route_table" "aft_vpc_private_subnet_01" {
  count             = var.aft_feature_disable_private_networking ? 0 : 1
  vpc_id = aws_vpc.aft_vpc.id
  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.aft-vpc-natgw-01[0].id
  }
  tags = {
    Name = "aft-vpc-private-subnet-01"
  }
}

resource "aws_route_table" "aft_vpc_private_subnet_02" {
  count             = var.aft_feature_disable_private_networking ? 0 : 1
  vpc_id = aws_vpc.aft_vpc.id
  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.aft-vpc-natgw-02[0].id
  }
  tags = {
    Name = "aft-vpc-private-subnet-02"
  }
}

resource "aws_route_table" "aft_vpc_public_subnet_01" {
  vpc_id = aws_vpc.aft_vpc.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.aft-vpc-igw.id
  }
  tags = {
    Name = "aft-vpc-public-subnet-01"
  }
}

resource "aws_route_table_association" "aft_vpc_private_subnet_01" {
  count          = var.aft_feature_disable_private_networking ? 0 : 1
  subnet_id      = aws_subnet.aft_vpc_private_subnet_01[0].id
  route_table_id = aws_route_table.aft_vpc_private_subnet_01[0].id
}

resource "aws_route_table_association" "aft_vpc_private_subnet_02" {
  count          = var.aft_feature_disable_private_networking ? 0 : 1
  subnet_id      = aws_subnet.aft_vpc_private_subnet_02[0].id
  route_table_id = aws_route_table.aft_vpc_private_subnet_02[0].id
}

resource "aws_route_table_association" "aft_vpc_public_subnet_01" {
  subnet_id      = aws_subnet.aft_vpc_public_subnet_01.id
  route_table_id = aws_route_table.aft_vpc_public_subnet_01.id
}

resource "aws_route_table_association" "aft_vpc_public_subnet_02" {
  subnet_id      = aws_subnet.aft_vpc_public_subnet_02.id
  route_table_id = aws_route_table.aft_vpc_public_subnet_01.id
}


#########################################
# Security Groups
#########################################

resource "aws_security_group" "aft_vpc_default_sg" {
  name        = "aft-default-sg"
  description = "Allow outbound traffic"
  vpc_id      = aws_vpc.aft_vpc.id

  # Open egress required to download dependencies
  egress {
    description      = "Allow outbound traffic to internet"
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"] #tfsec:ignore:aws-ec2-no-public-egress-sgr
    ipv6_cidr_blocks = ["::/0"]      #tfsec:ignore:aws-ec2-no-public-egress-sgr
  }
}

resource "aws_security_group" "aft_vpc_endpoint_sg" {
  name        = "aft-endpoint-sg"
  description = "Allow inbound HTTPS traffic and all Outbound"
  vpc_id      = aws_vpc.aft_vpc.id

  ingress {
    description = "Allow inbound TLS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [var.aft_vpc_cidr]
  }

  ingress {
    description = "Allow inbound SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.aft_vpc_cidr]
  }

  # Open egress required to download dependencies
  egress {
    description      = "Allow outbound traffic to internet"
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"] #tfsec:ignore:aws-ec2-no-public-egress-sgr
    ipv6_cidr_blocks = ["::/0"]      #tfsec:ignore:aws-ec2-no-public-egress-sgr
  }
}

#########################################
# Internet & NAT GWs
#########################################

resource "aws_internet_gateway" "aft-vpc-igw" {
  vpc_id = aws_vpc.aft_vpc.id

  tags = {
    Name = "aft-vpc-igw"
  }
}

resource "aws_eip" "aft-vpc-natgw-01" {
  count             = var.aft_feature_disable_private_networking ? 0 : 1
  vpc = true
}

resource "aws_eip" "aft-vpc-natgw-02" {
  count             = var.aft_feature_disable_private_networking ? 0 : 1
  vpc = true
}

resource "aws_nat_gateway" "aft-vpc-natgw-01" {
  count             = var.aft_feature_disable_private_networking ? 0 : 1
  depends_on = [aws_internet_gateway.aft-vpc-igw]

  allocation_id = aws_eip.aft-vpc-natgw-01[0].id
  subnet_id     = aws_subnet.aft_vpc_public_subnet_01.id

  tags = {
    Name = "aft-vpc-natgw-01"
  }

}

resource "aws_nat_gateway" "aft-vpc-natgw-02" {
  count             = var.aft_feature_disable_private_networking ? 0 : 1
  depends_on = [aws_internet_gateway.aft-vpc-igw]

  allocation_id = aws_eip.aft-vpc-natgw-02[0].id
  subnet_id     = aws_subnet.aft_vpc_public_subnet_02.id

  tags = {
    Name = "aft-vpc-natgw-02"
  }

}

#########################################
# VPC Gateway Endpoints
#########################################

resource "aws_vpc_endpoint" "s3" {
  count = var.aft_vpc_endpoints ? 1 : 0

  vpc_id            = aws_vpc.aft_vpc.id
  vpc_endpoint_type = "Gateway"
  service_name      = "com.amazonaws.${data.aws_region.aft-management.name}.s3"
  route_table_ids   = [
    aws_route_table.aft_vpc_private_subnet_01[0].id, aws_route_table.aft_vpc_private_subnet_02[0].id,
    aws_route_table.aft_vpc_public_subnet_01.id
  ]
}

resource "aws_vpc_endpoint" "dynamodb" {
  count = var.aft_vpc_endpoints ? 1 : 0

  vpc_id            = aws_vpc.aft_vpc.id
  vpc_endpoint_type = "Gateway"
  service_name      = "com.amazonaws.${data.aws_region.aft-management.name}.dynamodb"
  route_table_ids   = [
    aws_route_table.aft_vpc_private_subnet_01[0].id, aws_route_table.aft_vpc_private_subnet_02[0].id,
    aws_route_table.aft_vpc_public_subnet_01.id
  ]
}

#########################################
# VPC Interface Endpoints
#########################################

resource "aws_vpc_endpoint" "codebuild" {
  count = var.aft_vpc_endpoints ? 1 : 0

  vpc_id             = aws_vpc.aft_vpc.id
  service_name       = data.aws_vpc_endpoint_service.codebuild.service_name
  vpc_endpoint_type  = "Interface"
  subnet_ids         = data.aws_subnets.codebuild.ids
  security_group_ids = [
    aws_security_group.aft_vpc_endpoint_sg.id,
  ]

  private_dns_enabled = true
}

resource "aws_vpc_endpoint" "codecommit" {
  count = var.aft_vpc_endpoints ? 1 : 0

  vpc_id             = aws_vpc.aft_vpc.id
  service_name       = data.aws_vpc_endpoint_service.codecommit.service_name
  vpc_endpoint_type  = "Interface"
  subnet_ids         = data.aws_subnets.codecommit.ids
  security_group_ids = [
    aws_security_group.aft_vpc_endpoint_sg.id,
  ]

  private_dns_enabled = true
}

resource "aws_vpc_endpoint" "git-codecommit" {
  count = var.aft_vpc_endpoints ? 1 : 0

  vpc_id            = aws_vpc.aft_vpc.id
  service_name      = data.aws_vpc_endpoint_service.git-codecommit[0].service_name
  vpc_endpoint_type = "Interface"
  subnet_ids        = data.aws_subnets.git-codecommit[0].ids
  security_group_ids = [
    aws_security_group.aft_vpc_endpoint_sg.id,
  ]

  private_dns_enabled = true
}

resource "aws_vpc_endpoint" "codepipeline" {
  count = var.aft_vpc_endpoints ? 1 : 0

  vpc_id            = aws_vpc.aft_vpc.id
  service_name      = data.aws_vpc_endpoint_service.codepipeline[0].service_name
  vpc_endpoint_type = "Interface"
  subnet_ids        = data.aws_subnets.codepipeline[0].ids
  security_group_ids = [
    aws_security_group.aft_vpc_endpoint_sg.id,
  ]

  private_dns_enabled = true
}

resource "aws_vpc_endpoint" "servicecatalog" {
  count = var.aft_vpc_endpoints ? 1 : 0

  vpc_id            = aws_vpc.aft_vpc.id
  service_name      = data.aws_vpc_endpoint_service.servicecatalog[0].service_name
  vpc_endpoint_type = "Interface"
  subnet_ids        = data.aws_subnets.servicecatalog[0].ids
  security_group_ids = [
    aws_security_group.aft_vpc_endpoint_sg.id,
  ]

  private_dns_enabled = true
}

resource "aws_vpc_endpoint" "lambda" {
  count = var.aft_vpc_endpoints ? 1 : 0

  vpc_id            = aws_vpc.aft_vpc.id
  service_name      = data.aws_vpc_endpoint_service.lambda[0].service_name
  vpc_endpoint_type = "Interface"
  subnet_ids        = data.aws_subnets.lambda[0].ids
  security_group_ids = [
    aws_security_group.aft_vpc_endpoint_sg.id,
  ]

  private_dns_enabled = true
}

resource "aws_vpc_endpoint" "kms" {
  count = var.aft_vpc_endpoints ? 1 : 0

  vpc_id            = aws_vpc.aft_vpc.id
  service_name      = data.aws_vpc_endpoint_service.kms[0].service_name
  vpc_endpoint_type = "Interface"
  subnet_ids        = data.aws_subnets.kms[0].ids
  security_group_ids = [
    aws_security_group.aft_vpc_endpoint_sg.id,
  ]

  private_dns_enabled = true
}

resource "aws_vpc_endpoint" "logs" {
  count = var.aft_vpc_endpoints ? 1 : 0

  vpc_id            = aws_vpc.aft_vpc.id
  service_name      = data.aws_vpc_endpoint_service.logs[0].service_name
  vpc_endpoint_type = "Interface"
  subnet_ids        = data.aws_subnets.logs[0].ids
  security_group_ids = [
    aws_security_group.aft_vpc_endpoint_sg.id,
  ]

  private_dns_enabled = true
}

resource "aws_vpc_endpoint" "events" {
  count = var.aft_vpc_endpoints ? 1 : 0

  vpc_id            = aws_vpc.aft_vpc.id
  service_name      = data.aws_vpc_endpoint_service.events[0].service_name
  vpc_endpoint_type = "Interface"
  subnet_ids        = data.aws_subnets.events[0].ids
  security_group_ids = [
    aws_security_group.aft_vpc_endpoint_sg.id,
  ]

  private_dns_enabled = true
}

resource "aws_vpc_endpoint" "states" {
  count = var.aft_vpc_endpoints ? 1 : 0

  vpc_id            = aws_vpc.aft_vpc.id
  service_name      = data.aws_vpc_endpoint_service.states[0].service_name
  vpc_endpoint_type = "Interface"
  subnet_ids        = data.aws_subnets.states[0].ids
  security_group_ids = [
    aws_security_group.aft_vpc_endpoint_sg.id,
  ]

  private_dns_enabled = true
}

resource "aws_vpc_endpoint" "ssm" {
  count = var.aft_vpc_endpoints ? 1 : 0

  vpc_id            = aws_vpc.aft_vpc.id
  service_name      = data.aws_vpc_endpoint_service.ssm[0].service_name
  vpc_endpoint_type = "Interface"
  subnet_ids        = data.aws_subnets.ssm[0].ids
  security_group_ids = [
    aws_security_group.aft_vpc_endpoint_sg.id,
  ]

  private_dns_enabled = true
}

resource "aws_vpc_endpoint" "sns" {
  count = var.aft_vpc_endpoints ? 1 : 0

  vpc_id            = aws_vpc.aft_vpc.id
  service_name      = data.aws_vpc_endpoint_service.sns[0].service_name
  vpc_endpoint_type = "Interface"
  subnet_ids        = data.aws_subnets.sns[0].ids
  security_group_ids = [
    aws_security_group.aft_vpc_endpoint_sg.id,
  ]

  private_dns_enabled = true
}

resource "aws_vpc_endpoint" "sqs" {
  count = var.aft_vpc_endpoints ? 1 : 0

  vpc_id            = aws_vpc.aft_vpc.id
  service_name      = data.aws_vpc_endpoint_service.sqs[0].service_name
  vpc_endpoint_type = "Interface"
  subnet_ids        = data.aws_subnets.sqs[0].ids
  security_group_ids = [
    aws_security_group.aft_vpc_endpoint_sg.id,
  ]

  private_dns_enabled = true
}

resource "aws_vpc_endpoint" "sts" {
  count = var.aft_vpc_endpoints ? 1 : 0

  vpc_id            = aws_vpc.aft_vpc.id
  service_name      = data.aws_vpc_endpoint_service.sts[0].service_name
  vpc_endpoint_type = "Interface"
  subnet_ids        = data.aws_subnets.sts[0].ids
  security_group_ids = [
    aws_security_group.aft_vpc_endpoint_sg.id,
  ]

  private_dns_enabled = true
}
