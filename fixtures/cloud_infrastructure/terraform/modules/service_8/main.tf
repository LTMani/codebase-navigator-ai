# Terraform Cluster Infrastructure Configuration 8
terraform {
  required_version = ">= 1.7.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.40"
    }
  }
}

resource "aws_security_group" "cluster_sg_8" {
  name        = "navigator-cluster-sg-8"
  description = "Security group for microservice cluster 8"
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
    Name = "navigator-cluster-sg-8"
    Environment = var.environment
  }
}

resource "aws_ecs_task_definition" "task_def_8" {
  family                   = "navigator-task-8"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "1024"
  memory                   = "2048"
  container_definitions    = jsonencode([
    {
      name      = "service-container-8"
      image     = "123456789012.dkr.ecr.us-east-1.amazonaws.com/navigator/service-8:latest"
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
