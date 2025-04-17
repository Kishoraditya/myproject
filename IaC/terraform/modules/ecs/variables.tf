variable "environment" {
  description = "The environment (dev, test, pre-prod, prod)"
  type        = string
}

variable "app_name" {
  description = "The name of the application"
  type        = string
  default     = "wagtail-app"
}

variable "aws_region" {
  description = "The AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "vpc_id" {
  description = "The ID of the VPC"
  type        = string
}

variable "private_subnet_ids" {
  description = "List of private subnet IDs"
  type        = list(string)
}

variable "public_subnet_ids" {
  description = "List of public subnet IDs"
  type        = list(string)
}

variable "ecs_security_group_id" {
  description = "The security group ID for ECS tasks"
  type        = string
}

variable "alb_security_group_id" {
  description = "The security group ID for ALB"
  type        = string
}

variable "ecr_repository_url" {
  description = "The URL of the ECR repository"
  type        = string
}

variable "app_image_tag" {
  description = "The tag of the application image"
  type        = string
  default     = "latest"
}

variable "container_port" {
  description = "Port exposed by the container"
  type        = number
  default     = 8000
}

variable "fargate_cpu" {
  description = "Fargate instance CPU units to provision (1 vCPU = 1024 CPU units)"
  type        = number
  default     = 256
}

variable "fargate_memory" {
  description = "Fargate instance memory to provision (in MiB)"
  type        = number
  default     = 512
}

variable "app_count" {
  description = "Number of application containers to run"
  type        = number
  default     = 1
}

variable "db_host" {
  description = "The database host"
  type        = string
}

variable "db_port" {
  description = "The database port"
  type        = number
  default     = 5432
}

variable "db_name" {
  description = "The database name"
  type        = string
}

variable "secrets_arn" {
  description = "The ARN of the secrets manager secret"
  type        = string
}

variable "s3_bucket_name" {
  description = "The name of the S3 bucket for static files"
  type        = string
}

variable "domain_name" {
  description = "The domain name for the application"
  type        = string
}

variable "allowed_hosts" {
  description = "Comma-separated list of allowed hosts"
  type        = string
  default     = "localhost,127.0.0.1"
} 

variable "acm_certificate_arn" {
  description = "The ARN of the ACM certificate covering dev.shoshin.world"
  type        = string
}

variable "superuser_username" {
  description = "Username for the Django superuser"
  type        = string
  default     = ""
}

variable "superuser_email" {
  description = "Email for the Django superuser"
  type        = string
  default     = ""
}

variable "superuser_password" {
  description = "Password for the Django superuser"
  type        = string
  default     = ""
  sensitive   = true
}


