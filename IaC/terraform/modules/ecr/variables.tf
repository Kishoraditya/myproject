variable "environment" {
  description = "The environment (dev, test, pre-prod, prod)"
  type        = string
}

variable "repository_name" {
  description = "The name of the ECR repository"
  type        = string
  default     = "wagtail-app"
} 