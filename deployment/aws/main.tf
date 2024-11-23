terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # If you want to use Terraform Cloud, uncomment this block
  # backend "remote" {
  #   organization = "your-org-name"
  #   workspaces {
  #     name = "your-workspace-name"
  #   }
  # }
}

provider "aws" {
  region = var.aws_region
}

# VPC
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = merge(
    local.common_tags,
    {
      Name = "${var.project_name}-${var.environment}-vpc"
    }
  )
}

# Public Subnet
resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  map_public_ip_on_launch = true
  availability_zone       = "${var.aws_region}a"

  tags = merge(
    local.common_tags,
    {
      Name = "${var.project_name}-${var.environment}-public"
    }
  )
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = merge(
    local.common_tags,
    {
      Name = "${var.project_name}-${var.environment}-igw"
    }
  )
}

# Route Table
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = merge(
    local.common_tags,
    {
      Name = "${var.project_name}-${var.environment}-rt"
    }
  )
}

# Route Table Association
resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

# Security Group
resource "aws_security_group" "web" {
  name        = "${var.project_name}-${var.environment}-sg"
  description = "Security group for web application"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    local.common_tags,
    {
      Name = "${var.project_name}-${var.environment}-sg"
    }
  )
}

# SSH Key Pair
resource "aws_key_pair" "deployer" {
  key_name   = "${var.project_name}-${var.environment}-deployer"
  public_key = file("~/.ssh/aws_deployer.pub")

  tags = local.common_tags
}

# EC2 Instance
resource "aws_instance" "web" {
  ami           = var.instance_ami
  instance_type = var.instance_type

  subnet_id                   = aws_subnet.public.id
  vpc_security_group_ids      = [aws_security_group.web.id]
  associate_public_ip_address = true
  key_name                   = aws_key_pair.deployer.key_name

  root_block_device {
    volume_size = 8
    volume_type = "gp2"
    encrypted   = true

    tags = merge(
      local.common_tags,
      {
        Name = "${var.project_name}-${var.environment}-root-volume"
      }
    )
  }

  tags = merge(
    local.common_tags,
    {
      Name = "${var.project_name}-${var.environment}-instance"
    }
  )
}
