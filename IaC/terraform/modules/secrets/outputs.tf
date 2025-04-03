output "secret_arn" {
  value       = aws_secretsmanager_secret.app_secrets.arn
  description = "The ARN of the Secrets Manager secret"
}

output "secret_name" {
  value       = aws_secretsmanager_secret.app_secrets.name
  description = "The name of the Secrets Manager secret"
} 