output "vpc_id" {
  value       = module.networking.vpc_id
  description = "The ID of the VPC"
}

output "ecr_repository_url" {
  value       = module.ecr.repository_url
  description = "The URL of the ECR repository"
}

output "s3_bucket_name" {
  value       = module.s3.bucket_id
  description = "The name of the S3 bucket"
}

output "rds_endpoint" {
  value       = module.rds.db_instance_endpoint
  description = "The endpoint of the RDS instance"
  sensitive   = true
}

output "alb_dns_name" {
  value       = module.ecs.alb_dns_name
  description = "The DNS name of the load balancer"
}

output "domain_name" {
  value       = var.domain_name
  description = "The domain name for the application"
} 