# Terraform Cluster Infrastructure Configuration 21
terraform {
  required_version = ">= 1.7.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.40"
    }
  }
}

resource "aws_security_group" "cluster_sg_21" {
  name        = "navigator-cluster-sg-21"
  description = "Security group for microservice cluster 21"
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
    Name = "navigator-cluster-sg-21"
    Environment = var.environment
  }
}

resource "aws_ecs_task_definition" "task_def_21" {
  family                   = "navigator-task-21"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "1024"
  memory                   = "2048"
  container_definitions    = jsonencode([
    {
      name      = "service-container-21"
      image     = "123456789012.dkr.ecr.us-east-1.amazonaws.com/navigator/service-21:latest"
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
