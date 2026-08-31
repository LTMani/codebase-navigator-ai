variable "aws_region" {
  type        = string
  description = "AWS deployment region"
  default     = "us-east-1"
}

variable "environment" {
  type        = string
  description = "Deployment target environment (dev, staging, prod)"
  default     = "production"
}

variable "vpc_cidr" {
  type        = string
  description = "VPC network CIDR block"
  default     = "10.100.0.0/16"
}

variable "availability_zones" {
  type        = list(string)
  description = "Target availability zones"
  default     = ["us-east-1a", "us-east-1b", "us-east-1c"]
}

variable "public_subnet_cidrs" {
  type        = list(string)
  default     = ["10.100.1.0/24", "10.100.2.0/24", "10.100.3.0/24"]
}

variable "private_subnet_cidrs" {
  type        = list(string)
  default     = ["10.100.10.0/24", "10.100.20.0/24", "10.100.30.0/24"]
}

variable "db_instance_class" {
  type        = string
  default     = "db.r6g.xlarge"
}

variable "db_allocated_storage" {
  type        = number
  default     = 100
}
