terraform {
  required_version = ">= 1.7.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.40"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Environment = var.environment
      Project     = "CodebaseNavigatorAI"
      ManagedBy   = "Terraform"
    }
  }
}

module "vpc" {
  source              = "./modules/vpc"
  environment         = var.environment
  vpc_cidr            = var.vpc_cidr
  availability_zones  = var.availability_zones
  public_subnet_cidrs = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
}

module "security_groups" {
  source      = "./modules/security_groups"
  environment = var.environment
  vpc_id      = module.vpc.vpc_id
}

module "rds_postgres" {
  source             = "./modules/rds"
  environment        = var.environment
  vpc_id             = module.vpc.vpc_id
  subnet_ids         = module.vpc.private_subnet_ids
  security_group_id  = module.security_groups.database_sg_id
  db_instance_class  = var.db_instance_class
  allocated_storage  = var.db_allocated_storage
}

module "ecs_cluster" {
  source             = "./modules/ecs"
  environment        = var.environment
  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
  alb_security_group = module.security_groups.alb_sg_id
  ecs_security_group = module.security_groups.ecs_tasks_sg_id
}
