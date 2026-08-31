# Terraform Cluster Infrastructure Configuration 20
terraform {
  required_version = ">= 1.7.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.40"
    }
  }
}

resource "aws_security_group" "cluster_sg_20" {
  name        = "navigator-cluster-sg-20"
  description = "Security group for microservice cluster 20"
  vpc_id      = var.vpc_id

  ingress {
    description = "TLS HTTPS Ingress"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "navigator-cluster-sg-20"
    Environment = var.environment
  }
}

resource "aws_ecs_task_definition" "task_def_20" {
  family                   = "navigator-task-20"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "1024"
  memory                   = "2048"
  container_definitions    = jsonencode([
    {
      name      = "service-container-20"
      image     = "123456789012.dkr.ecr.us-east-1.amazonaws.com/navigator/service-20:latest"
      essential = true
      portMappings = [
        {
          containerPort = 8080
          hostPort      = 8080
        }
      ]
    }
  ])
}
