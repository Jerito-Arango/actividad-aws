terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

# 1. Crear un Bucket de S3 (usa un nombre único, ej: anade tu código o iniciales)
resource "aws_s3_bucket" "mi_bucket" {
  bucket = "lab-terraform-bucket-de-gr01-user-10"
}

# 2. Red básica (VPC, Subred y Gateway para la instancia y RDS)
resource "aws_vpc" "mi_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  tags = { Name = "VPC-Lab" }
}

resource "aws_subnet" "mi_subnet_1" {
  vpc_id            = aws_vpc.mi_vpc.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "us-east-1a"
  tags = { Name = "Subnet-1" }
}

resource "aws_subnet" "mi_subnet_2" {
  vpc_id            = aws_subnet.mi_subnet_1.vpc_id # Asegura coexistencia en la VPC
  cidr_block        = "10.0.2.0/24"
  availability_zone = "us-east-1b"
  tags = { Name = "Subnet-2" }
}

resource "aws_internet_gateway" "mi_igw" {
  vpc_id = aws_vpc.mi_vpc.id
  tags   = { Name = "IGW-Lab" }
}

resource "aws_route_table" "mi_rt" {
  vpc_id = aws_vpc.mi_vpc.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.mi_igw.id
  }
  tags = { Name = "RT-Lab" }
}

resource "aws_route_table_association" "rta_1" {
  subnet_id      = aws_subnet.mi_subnet_1.id
  route_table_id = aws_route_table.mi_rt.id
}

# Grupo de seguridad para la EC2
resource "aws_security_group" "sg_ec2" {
  name   = "ec2-lab"
  vpc_id = aws_vpc.mi_vpc.id
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# 3. Instancia EC2
resource "aws_instance" "mi_servidor" {
  ami                         = "ami-0c7217cdde317cfec" # Amazon Linux 2023 en us-east-1 (verifica que sea válida)
  instance_type               = "t2.micro"
  subnet_id                   = aws_subnet.mi_subnet_1.id
  associate_public_ip_address = true
  vpc_security_group_ids      = [aws_security_group.sg_ec2.id]

  tags = { Name = "ServidorTerraform" }
}

# Grupo de subredes para RDS (requiere al menos 2 subredes en distintas AZs)
resource "aws_db_subnet_group" "db_subnet" {
  name       = "db-subnet-group-lab"
  subnet_ids = [aws_subnet.mi_subnet_1.id, aws_subnet.mi_subnet_2.id]
}

# 4. Instancia RDS con contraseña administrada en Secrets Manager
resource "aws_db_instance" "mi_rds" {
  identifier             = "mirdslab"
  engine                 = "mysql"
  engine_version         = "8.0"
  instance_class         = "db.t3.micro"
  allocated_storage      = 20
  db_subnet_group_name   = aws_db_subnet_group.db_subnet.name
  skip_final_snapshot    = true
  
  # Esto cumple con la condición de administrar la contraseña en Secrets Manager automáticamente
  manage_master_user_password = true
  username                    = "adminuser"
}