output "ecs_cluster_id" {
  value       = aws_ecs_cluster.main.id
  description = "The ID of the ECS cluster"
}

output "ecs_service_name" {
  value       = aws_ecs_service.main.name
  description = "The name of the ECS service"
}

output "task_definition_arn" {
  value       = aws_ecs_task_definition.app.arn
  description = "The ARN of the task definition"
}

output "alb_dns_name" {
  value       = aws_alb.main.dns_name
  description = "The DNS name of the load balancer"
}

output "alb_zone_id" {
  value       = aws_alb.main.zone_id
  description = "The canonical hosted zone ID of the load balancer"
}

output "certificate_validation_domain" {
  value       = { for dvo in aws_acm_certificate.cert.domain_validation_options : dvo.domain_name => { name = dvo.resource_record_name, record = dvo.resource_record_value, type = dvo.resource_record_type } }
  description = "Domain validation options for certificate"
} 