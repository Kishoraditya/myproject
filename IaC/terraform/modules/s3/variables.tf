variable "environment" {
  description = "The environment (dev, test, pre-prod, prod)"
  type        = string
}

variable "bucket_name" {
  description = "The name of the S3 bucket"
  type        = string
  default     = "wagtail-static"
}

variable "cors_allowed_origins" {
  description = "List of allowed origins for CORS"
  type        = list(string)
  default     = ["*"]
}

variable "create_cloudfront_distribution" {
  description = "Whether to create a CloudFront distribution"
  type        = bool
  default     = false
} 