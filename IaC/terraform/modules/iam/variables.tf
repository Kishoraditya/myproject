variable "environment" {
  description = "Environment name (e.g., dev, prod)"
  type        = string
}

variable "github_org" {
  description = "GitHub organization or username"
  type        = string
  default     = "Kishoraditya"
}

variable "github_repo" {
  description = "GitHub repository name"
  type        = string
  default     = "myproject"
}
