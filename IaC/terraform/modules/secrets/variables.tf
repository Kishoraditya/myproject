variable "environment" {
  description = "The environment (dev, test, pre-prod, prod)"
  type        = string
}

variable "app_name" {
  description = "The name of the application"
  type        = string
  default     = "wagtail-app"
}

variable "secret_key" {
  description = "Django SECRET_KEY"
  type        = string
  sensitive   = true
}

variable "db_username" {
  description = "Database username"
  type        = string
  sensitive   = true
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

variable "aws_access_key_id" {
  description = "AWS access key ID for S3 access"
  type        = string
  sensitive   = true
}

variable "aws_secret_access_key" {
  description = "AWS secret access key for S3 access"
  type        = string
  sensitive   = true
} 