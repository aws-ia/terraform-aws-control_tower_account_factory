# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
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
  vpc_id            = aws_vpc.aft_vpc.id
  cidr_block        = var.aft_vpc_private_subnet_01_cidr
  availability_zone = element(data.aws_availability_zones.available.names, 0)
  tags = {
    Name = "aft-vpc-private-subnet-01"
  }
}

resource "aws_subnet" "aft_vpc_private_subnet_02" {
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
  vpc_id = aws_vpc.aft_vpc.id
  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.aft-vpc-natgw-01.id
  }
  tags = {
    Name = "aft-vpc-private-subnet-01"
  }
}

resource "aws_route_table" "aft_vpc_private_subnet_02" {
  vpc_id = aws_vpc.aft_vpc.id
  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.aft-vpc-natgw-02.id
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
  subnet_id      = aws_subnet.aft_vpc_private_subnet_01.id
  route_table_id = aws_route_table.aft_vpc_private_subnet_01.id
}

resource "aws_route_table_association" "aft_vpc_private_subnet_02" {
  subnet_id      = aws_subnet.aft_vpc_private_subnet_02.id
  route_table_id = aws_route_table.aft_vpc_private_subnet_02.id
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

  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }
}

resource "aws_security_group" "aft_vpc_endpoint_sg" {
  name        = "aft-endpoint-sg"
  description = "Allow inbound HTTPS traffic and all Outbound"
  vpc_id      = aws_vpc.aft_vpc.id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [var.aft_vpc_cidr]
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.aft_vpc_cidr]
  }

  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
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
  vpc = true
}

resource "aws_eip" "aft-vpc-natgw-02" {
  vpc = true
}

resource "aws_nat_gateway" "aft-vpc-natgw-01" {
  depends_on = [aws_internet_gateway.aft-vpc-igw]

  allocation_id = aws_eip.aft-vpc-natgw-01.id
  subnet_id     = aws_subnet.aft_vpc_public_subnet_01.id

  tags = {
    Name = "aft-vpc-natgw-01"
  }

}

resource "aws_nat_gateway" "aft-vpc-natgw-02" {
  depends_on = [aws_internet_gateway.aft-vpc-igw]

  allocation_id = aws_eip.aft-vpc-natgw-02.id
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
  route_table_ids   = [aws_route_table.aft_vpc_private_subnet_01.id, aws_route_table.aft_vpc_private_subnet_02.id, aws_route_table.aft_vpc_public_subnet_01.id]
}

resource "aws_vpc_endpoint" "dynamodb" {
  count = var.aft_vpc_endpoints ? 1 : 0

  vpc_id            = aws_vpc.aft_vpc.id
  vpc_endpoint_type = "Gateway"
  service_name      = "com.amazonaws.${data.aws_region.aft-management.name}.dynamodb"
  route_table_ids   = [aws_route_table.aft_vpc_private_subnet_01.id, aws_route_table.aft_vpc_private_subnet_02.id, aws_route_table.aft_vpc_public_subnet_01.id]
}

#########################################
# VPC Interface Endpoints
#########################################

resource "aws_vpc_endpoint" "codebuild" {
  count = var.aft_vpc_endpoints ? 1 : 0

  vpc_id            = aws_vpc.aft_vpc.id
  service_name      = data.aws_vpc_endpoint_service.codebuild.service_name
  vpc_endpoint_type = "Interface"
  subnet_ids        = data.aws_subnets.codebuild.ids
  security_group_ids = [
    aws_security_group.aft_vpc_endpoint_sg.id,
  ]

  private_dns_enabled = true
}

resource "aws_vpc_endpoint" "codecommit" {
  count = var.aft_vpc_endpoints ? 1 : 0

  vpc_id            = aws_vpc.aft_vpc.id
  service_name      = data.aws_vpc_endpoint_service.codecommit.service_name
  vpc_endpoint_type = "Interface"
  subnet_ids        = data.aws_subnets.codecommit.ids
  security_group_ids = [
    aws_security_group.aft_vpc_endpoint_sg.id,
  ]

  private_dns_enabled = true
}

resource "aws_vpc_endpoint" "git-codecommit" {
  count = var.aft_vpc_endpoints ? 1 : 0

  vpc_id            = aws_vpc.aft_vpc.id
  service_name      = data.aws_vpc_endpoint_service.git-codecommit.service_name
  vpc_endpoint_type = "Interface"
  subnet_ids        = data.aws_subnets.git-codecommit.ids
  security_group_ids = [
    aws_security_group.aft_vpc_endpoint_sg.id,
  ]

  private_dns_enabled = true
}

resource "aws_vpc_endpoint" "codepipeline" {
  count = var.aft_vpc_endpoints ? 1 : 0

  vpc_id            = aws_vpc.aft_vpc.id
  service_name      = data.aws_vpc_endpoint_service.codepipeline.service_name
  vpc_endpoint_type = "Interface"
  subnet_ids        = data.aws_subnets.codepipeline.ids
  security_group_ids = [
    aws_security_group.aft_vpc_endpoint_sg.id,
  ]

  private_dns_enabled = true
}

resource "aws_vpc_endpoint" "servicecatalog" {
  count = var.aft_vpc_endpoints ? 1 : 0

  vpc_id            = aws_vpc.aft_vpc.id
  service_name      = data.aws_vpc_endpoint_service.servicecatalog.service_name
  vpc_endpoint_type = "Interface"
  subnet_ids        = data.aws_subnets.servicecatalog.ids
  security_group_ids = [
    aws_security_group.aft_vpc_endpoint_sg.id,
  ]

  private_dns_enabled = true
}

resource "aws_vpc_endpoint" "lambda" {
  count = var.aft_vpc_endpoints ? 1 : 0

  vpc_id            = aws_vpc.aft_vpc.id
  service_name      = data.aws_vpc_endpoint_service.lambda.service_name
  vpc_endpoint_type = "Interface"
  subnet_ids        = data.aws_subnets.lambda.ids
  security_group_ids = [
    aws_security_group.aft_vpc_endpoint_sg.id,
  ]

  private_dns_enabled = true
}

resource "aws_vpc_endpoint" "kms" {
  count = var.aft_vpc_endpoints ? 1 : 0

  vpc_id            = aws_vpc.aft_vpc.id
  service_name      = data.aws_vpc_endpoint_service.kms.service_name
  vpc_endpoint_type = "Interface"
  subnet_ids        = data.aws_subnets.kms.ids
  security_group_ids = [
    aws_security_group.aft_vpc_endpoint_sg.id,
  ]

  private_dns_enabled = true
}

resource "aws_vpc_endpoint" "logs" {
  count = var.aft_vpc_endpoints ? 1 : 0

  vpc_id            = aws_vpc.aft_vpc.id
  service_name      = data.aws_vpc_endpoint_service.logs.service_name
  vpc_endpoint_type = "Interface"
  subnet_ids        = data.aws_subnets.logs.ids
  security_group_ids = [
    aws_security_group.aft_vpc_endpoint_sg.id,
  ]

  private_dns_enabled = true
}

resource "aws_vpc_endpoint" "events" {
  count = var.aft_vpc_endpoints ? 1 : 0

  vpc_id            = aws_vpc.aft_vpc.id
  service_name      = data.aws_vpc_endpoint_service.events.service_name
  vpc_endpoint_type = "Interface"
  subnet_ids        = data.aws_subnets.events.ids
  security_group_ids = [
    aws_security_group.aft_vpc_endpoint_sg.id,
  ]

  private_dns_enabled = true
}

resource "aws_vpc_endpoint" "states" {
  count = var.aft_vpc_endpoints ? 1 : 0

  vpc_id            = aws_vpc.aft_vpc.id
  service_name      = data.aws_vpc_endpoint_service.states.service_name
  vpc_endpoint_type = "Interface"
  subnet_ids        = data.aws_subnets.states.ids
  security_group_ids = [
    aws_security_group.aft_vpc_endpoint_sg.id,
  ]

  private_dns_enabled = true
}

resource "aws_vpc_endpoint" "ssm" {
  count = var.aft_vpc_endpoints ? 1 : 0

  vpc_id            = aws_vpc.aft_vpc.id
  service_name      = data.aws_vpc_endpoint_service.ssm.service_name
  vpc_endpoint_type = "Interface"
  subnet_ids        = data.aws_subnets.ssm.ids
  security_group_ids = [
    aws_security_group.aft_vpc_endpoint_sg.id,
  ]

  private_dns_enabled = true
}

resource "aws_vpc_endpoint" "sns" {
  count = var.aft_vpc_endpoints ? 1 : 0

  vpc_id            = aws_vpc.aft_vpc.id
  service_name      = data.aws_vpc_endpoint_service.sns.service_name
  vpc_endpoint_type = "Interface"
  subnet_ids        = data.aws_subnets.sns.ids
  security_group_ids = [
    aws_security_group.aft_vpc_endpoint_sg.id,
  ]

  private_dns_enabled = true
}

resource "aws_vpc_endpoint" "sqs" {
  count = var.aft_vpc_endpoints ? 1 : 0

  vpc_id            = aws_vpc.aft_vpc.id
  service_name      = data.aws_vpc_endpoint_service.sqs.service_name
  vpc_endpoint_type = "Interface"
  subnet_ids        = data.aws_subnets.sqs.ids
  security_group_ids = [
    aws_security_group.aft_vpc_endpoint_sg.id,
  ]

  private_dns_enabled = true
}

resource "aws_vpc_endpoint" "sts" {
  count = var.aft_vpc_endpoints ? 1 : 0

  vpc_id            = aws_vpc.aft_vpc.id
  service_name      = data.aws_vpc_endpoint_service.sts.service_name
  vpc_endpoint_type = "Interface"
  subnet_ids        = data.aws_subnets.sts.ids
  security_group_ids = [
    aws_security_group.aft_vpc_endpoint_sg.id,
  ]

  private_dns_enabled = true
}
