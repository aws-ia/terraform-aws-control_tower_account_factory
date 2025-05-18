# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

# TODO: Remove this tfsec-ignore when VPC flow logs are enabled
#tfsec:ignore:aws-ec2-require-vpc-flow-logs-for-all-vpcs
resource "aws_vpc" "aft_vpc" {
  count                = var.aft_enable_vpc && var.aft_customer_vpc_id == null ? 1 : 0
  cidr_block           = var.aft_vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags = {
    Name = "aft-management-vpc"
  }
}

resource "aws_default_security_group" "aft_vpc_default_sg" {
  # Ensure default SG allows no traffic
  # https://docs.aws.amazon.com/securityhub/latest/userguide/ec2-controls.html#ec2-2
  count  = var.aft_enable_vpc && var.aft_customer_vpc_id == null ? 1 : 0
  vpc_id = aws_vpc.aft_vpc[0].id
  tags = {
    Name = "aft-vpc-default-sg"
  }
}

#########################################
# VPC Subnets
#########################################

resource "aws_subnet" "aft_vpc_private_subnet_01" {
  count             = var.aft_enable_vpc && var.aft_customer_vpc_id == null ? 1 : 0
  vpc_id            = aws_vpc.aft_vpc[0].id
  cidr_block        = var.aft_vpc_private_subnet_01_cidr
  availability_zone = element(data.aws_availability_zones.available.names, 0)
  tags = {
    Name = "aft-vpc-private-subnet-01"
  }
}

resource "aws_subnet" "aft_vpc_private_subnet_02" {
  count             = var.aft_enable_vpc && var.aft_customer_vpc_id == null ? 1 : 0
  vpc_id            = aws_vpc.aft_vpc[0].id
  cidr_block        = var.aft_vpc_private_subnet_02_cidr
  availability_zone = element(data.aws_availability_zones.available.names, 1)
  tags = {
    Name = "aft-vpc-private-subnet-02"
  }
}

resource "aws_subnet" "aft_vpc_public_subnet_01" {
  count             = var.aft_enable_vpc && var.aft_customer_vpc_id == null ? 1 : 0
  vpc_id            = aws_vpc.aft_vpc[0].id
  cidr_block        = var.aft_vpc_public_subnet_01_cidr
  availability_zone = element(data.aws_availability_zones.available.names, 0)
  tags = {
    Name = "aft-vpc-public-subnet-01"
  }
}

resource "aws_subnet" "aft_vpc_public_subnet_02" {
  count             = var.aft_enable_vpc && var.aft_customer_vpc_id == null ? 1 : 0
  vpc_id            = aws_vpc.aft_vpc[0].id
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
  count  = var.aft_enable_vpc && var.aft_customer_vpc_id == null ? 1 : 0
  vpc_id = aws_vpc.aft_vpc[0].id
  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.aft-vpc-natgw-01[0].id
  }
  tags = {
    Name = "aft-vpc-private-subnet-01"
  }
}

resource "aws_route_table" "aft_vpc_private_subnet_02" {
  count  = var.aft_enable_vpc && var.aft_customer_vpc_id == null ? 1 : 0
  vpc_id = aws_vpc.aft_vpc[0].id
  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.aft-vpc-natgw-02[0].id
  }
  tags = {
    Name = "aft-vpc-private-subnet-02"
  }
}

resource "aws_route_table" "aft_vpc_public_subnet_01" {
  count  = var.aft_enable_vpc && var.aft_customer_vpc_id == null ? 1 : 0
  vpc_id = aws_vpc.aft_vpc[0].id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.aft-vpc-igw[0].id
  }
  tags = {
    Name = "aft-vpc-public-subnet-01"
  }
}

resource "aws_route_table_association" "aft_vpc_private_subnet_01" {
  count          = var.aft_enable_vpc && var.aft_customer_vpc_id == null ? 1 : 0
  subnet_id      = aws_subnet.aft_vpc_private_subnet_01[0].id
  route_table_id = aws_route_table.aft_vpc_private_subnet_01[0].id
}

resource "aws_route_table_association" "aft_vpc_private_subnet_02" {
  count          = var.aft_enable_vpc && var.aft_customer_vpc_id == null ? 1 : 0
  subnet_id      = aws_subnet.aft_vpc_private_subnet_02[0].id
  route_table_id = aws_route_table.aft_vpc_private_subnet_02[0].id
}

resource "aws_route_table_association" "aft_vpc_public_subnet_01" {
  count          = var.aft_enable_vpc && var.aft_customer_vpc_id == null ? 1 : 0
  subnet_id      = aws_subnet.aft_vpc_public_subnet_01[0].id
  route_table_id = aws_route_table.aft_vpc_public_subnet_01[0].id
}

resource "aws_route_table_association" "aft_vpc_public_subnet_02" {
  count          = var.aft_enable_vpc && var.aft_customer_vpc_id == null ? 1 : 0
  subnet_id      = aws_subnet.aft_vpc_public_subnet_02[0].id
  route_table_id = aws_route_table.aft_vpc_public_subnet_01[0].id
}


#########################################
# Security Groups
#########################################

resource "aws_security_group" "aft_vpc_default_sg" {
  count       = var.aft_enable_vpc || var.aft_customer_vpc_id != null ? 1 : 0
  name        = "aft-default-sg"
  description = "Allow outbound traffic"
  vpc_id      = local.vpc_id

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
  count       = var.aft_enable_vpc || var.aft_customer_vpc_id != null ? 1 : 0
  name        = "aft-endpoint-sg"
  description = "Allow inbound HTTPS traffic and all Outbound"
  vpc_id      = local.vpc_id

  ingress {
    description = "Allow inbound TLS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [local.vpc_cidr]
  }

  ingress {
    description = "Allow inbound SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [local.vpc_cidr]
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
  count  = var.aft_enable_vpc && var.aft_customer_vpc_id == null ? 1 : 0
  vpc_id = aws_vpc.aft_vpc[0].id

  tags = {
    Name = "aft-vpc-igw"
  }
}

resource "aws_eip" "aft-vpc-natgw-01" {
  count  = var.aft_enable_vpc && var.aft_customer_vpc_id == null ? 1 : 0
  domain = "vpc"
}

resource "aws_eip" "aft-vpc-natgw-02" {
  count  = var.aft_enable_vpc && var.aft_customer_vpc_id == null ? 1 : 0
  domain = "vpc"
}

resource "aws_nat_gateway" "aft-vpc-natgw-01" {
  count      = var.aft_enable_vpc && var.aft_customer_vpc_id == null ? 1 : 0
  depends_on = [aws_internet_gateway.aft-vpc-igw]

  allocation_id = aws_eip.aft-vpc-natgw-01[0].id
  subnet_id     = aws_subnet.aft_vpc_public_subnet_01[0].id

  tags = {
    Name = "aft-vpc-natgw-01"
  }

}

resource "aws_nat_gateway" "aft-vpc-natgw-02" {
  count      = var.aft_enable_vpc && var.aft_customer_vpc_id == null ? 1 : 0
  depends_on = [aws_internet_gateway.aft-vpc-igw]

  allocation_id = aws_eip.aft-vpc-natgw-02[0].id
  subnet_id     = aws_subnet.aft_vpc_public_subnet_02[0].id

  tags = {
    Name = "aft-vpc-natgw-02"
  }

}

#########################################
# VPC Gateway Endpoints
#########################################

resource "aws_vpc_endpoint" "s3" {
  count = local.vpc_deployment && var.aft_vpc_endpoints ? 1 : 0

  vpc_id            = local.vpc_id
  vpc_endpoint_type = "Gateway"
  service_name      = "com.amazonaws.${data.aws_region.aft-management.name}.s3"
  route_table_ids   = local.vpc_route_table_ids
}

resource "aws_vpc_endpoint" "dynamodb" {
  count = local.vpc_deployment && var.aft_vpc_endpoints ? 1 : 0

  vpc_id            = local.vpc_id
  vpc_endpoint_type = "Gateway"
  service_name      = "com.amazonaws.${data.aws_region.aft-management.name}.dynamodb"
  route_table_ids   = local.vpc_route_table_ids
}

#########################################
# VPC Interface Endpoints
#########################################

resource "aws_vpc_endpoint" "codebuild" {
  count = local.vpc_deployment && var.aft_vpc_endpoints ? 1 : 0

  vpc_id            = local.vpc_id
  service_name      = data.aws_vpc_endpoint_service.codebuild[0].service_name
  vpc_endpoint_type = "Interface"
  subnet_ids        = data.aws_subnets.codebuild[0].ids
  security_group_ids = [
    aws_security_group.aft_vpc_endpoint_sg[0].id,
  ]

  private_dns_enabled = true
}

resource "aws_vpc_endpoint" "codecommit" {
  count = local.vpc_deployment && var.aft_vpc_endpoints ? 1 : 0

  vpc_id            = local.vpc_id
  service_name      = data.aws_vpc_endpoint_service.codecommit[0].service_name
  vpc_endpoint_type = "Interface"
  subnet_ids        = data.aws_subnets.codecommit[0].ids
  security_group_ids = [
    aws_security_group.aft_vpc_endpoint_sg[0].id,
  ]

  private_dns_enabled = true
}

resource "aws_vpc_endpoint" "git-codecommit" {
  count = local.vpc_deployment && var.aft_vpc_endpoints ? 1 : 0

  vpc_id            = local.vpc_id
  service_name      = data.aws_vpc_endpoint_service.git-codecommit[0].service_name
  vpc_endpoint_type = "Interface"
  subnet_ids        = data.aws_subnets.git-codecommit[0].ids
  security_group_ids = [
    aws_security_group.aft_vpc_endpoint_sg[0].id,
  ]

  private_dns_enabled = true
}

resource "aws_vpc_endpoint" "codepipeline" {
  count = local.vpc_deployment && var.aft_vpc_endpoints ? 1 : 0

  vpc_id            = local.vpc_id
  service_name      = data.aws_vpc_endpoint_service.codepipeline[0].service_name
  vpc_endpoint_type = "Interface"
  subnet_ids        = data.aws_subnets.codepipeline[0].ids
  security_group_ids = [
    aws_security_group.aft_vpc_endpoint_sg[0].id,
  ]

  private_dns_enabled = true
}

resource "aws_vpc_endpoint" "servicecatalog" {
  count = local.vpc_deployment && var.aft_vpc_endpoints ? 1 : 0

  vpc_id            = local.vpc_id
  service_name      = data.aws_vpc_endpoint_service.servicecatalog[0].service_name
  vpc_endpoint_type = "Interface"
  subnet_ids        = data.aws_subnets.servicecatalog[0].ids
  security_group_ids = [
    aws_security_group.aft_vpc_endpoint_sg[0].id,
  ]

  private_dns_enabled = true
}

resource "aws_vpc_endpoint" "lambda" {
  count = local.vpc_deployment && var.aft_vpc_endpoints ? 1 : 0

  vpc_id            = local.vpc_id
  service_name      = data.aws_vpc_endpoint_service.lambda[0].service_name
  vpc_endpoint_type = "Interface"
  subnet_ids        = data.aws_subnets.lambda[0].ids
  security_group_ids = [
    aws_security_group.aft_vpc_endpoint_sg[0].id,
  ]

  private_dns_enabled = true
}

resource "aws_vpc_endpoint" "kms" {
  count = local.vpc_deployment && var.aft_vpc_endpoints ? 1 : 0

  vpc_id            = local.vpc_id
  service_name      = data.aws_vpc_endpoint_service.kms[0].service_name
  vpc_endpoint_type = "Interface"
  subnet_ids        = data.aws_subnets.kms[0].ids
  security_group_ids = [
    aws_security_group.aft_vpc_endpoint_sg[0].id,
  ]

  private_dns_enabled = true
}

resource "aws_vpc_endpoint" "logs" {
  count = local.vpc_deployment && var.aft_vpc_endpoints ? 1 : 0

  vpc_id            = local.vpc_id
  service_name      = data.aws_vpc_endpoint_service.logs[0].service_name
  vpc_endpoint_type = "Interface"
  subnet_ids        = data.aws_subnets.logs[0].ids
  security_group_ids = [
    aws_security_group.aft_vpc_endpoint_sg[0].id,
  ]

  private_dns_enabled = true
}

resource "aws_vpc_endpoint" "events" {
  count = local.vpc_deployment && var.aft_vpc_endpoints ? 1 : 0

  vpc_id            = local.vpc_id
  service_name      = data.aws_vpc_endpoint_service.events[0].service_name
  vpc_endpoint_type = "Interface"
  subnet_ids        = data.aws_subnets.events[0].ids
  security_group_ids = [
    aws_security_group.aft_vpc_endpoint_sg[0].id,
  ]

  private_dns_enabled = true
}

resource "aws_vpc_endpoint" "organizations" {
  count = local.vpc_deployment && var.aft_vpc_endpoints && local.orgs_endpoint_supported ? 1 : 0

  vpc_id            = local.vpc_id
  service_name      = data.aws_vpc_endpoint_service.organizations[0].service_name
  vpc_endpoint_type = "Interface"
  subnet_ids        = data.aws_subnets.organizations[0].ids
  security_group_ids = [
    aws_security_group.aft_vpc_endpoint_sg[0].id,
  ]

  private_dns_enabled = true
}

resource "aws_vpc_endpoint" "states" {
  count = local.vpc_deployment && var.aft_vpc_endpoints ? 1 : 0

  vpc_id            = local.vpc_id
  service_name      = data.aws_vpc_endpoint_service.states[0].service_name
  vpc_endpoint_type = "Interface"
  subnet_ids        = data.aws_subnets.states[0].ids
  security_group_ids = [
    aws_security_group.aft_vpc_endpoint_sg[0].id,
  ]

  private_dns_enabled = true
}

resource "aws_vpc_endpoint" "ssm" {
  count = local.vpc_deployment && var.aft_vpc_endpoints ? 1 : 0

  vpc_id            = local.vpc_id
  service_name      = data.aws_vpc_endpoint_service.ssm[0].service_name
  vpc_endpoint_type = "Interface"
  subnet_ids        = data.aws_subnets.ssm[0].ids
  security_group_ids = [
    aws_security_group.aft_vpc_endpoint_sg[0].id,
  ]

  private_dns_enabled = true
}

resource "aws_vpc_endpoint" "sns" {
  count = local.vpc_deployment && var.aft_vpc_endpoints ? 1 : 0

  vpc_id            = local.vpc_id
  service_name      = data.aws_vpc_endpoint_service.sns[0].service_name
  vpc_endpoint_type = "Interface"
  subnet_ids        = data.aws_subnets.sns[0].ids
  security_group_ids = [
    aws_security_group.aft_vpc_endpoint_sg[0].id,
  ]

  private_dns_enabled = true
}

resource "aws_vpc_endpoint" "sqs" {
  count = local.vpc_deployment && var.aft_vpc_endpoints ? 1 : 0

  vpc_id            = local.vpc_id
  service_name      = data.aws_vpc_endpoint_service.sqs[0].service_name
  vpc_endpoint_type = "Interface"
  subnet_ids        = data.aws_subnets.sqs[0].ids
  security_group_ids = [
    aws_security_group.aft_vpc_endpoint_sg[0].id,
  ]

  private_dns_enabled = true
}

resource "aws_vpc_endpoint" "sts" {
  count = local.vpc_deployment && var.aft_vpc_endpoints ? 1 : 0

  vpc_id            = local.vpc_id
  service_name      = data.aws_vpc_endpoint_service.sts[0].service_name
  vpc_endpoint_type = "Interface"
  subnet_ids        = data.aws_subnets.sts[0].ids
  security_group_ids = [
    aws_security_group.aft_vpc_endpoint_sg[0].id,
  ]

  private_dns_enabled = true
}
