output "vpc_id" {
  value       = aws_vpc.main.id
  description = "The ID of the VPC"
}

output "public_subnet_ids" {
  value       = aws_subnet.public[*].id
  description = "List of public subnet IDs"
}

output "private_subnet_ids" {
  value       = aws_subnet.private[*].id
  description = "List of private subnet IDs"
}

output "alb_security_group_id" {
  value       = aws_security_group.alb.id
  description = "Security group ID for the ALB"
}

output "ecs_security_group_id" {
  value       = aws_security_group.ecs.id
  description = "Security group ID for ECS tasks"
}

output "rds_security_group_id" {
  value       = aws_security_group.rds.id
  description = "Security group ID for RDS"
} 