resource "aws_secretsmanager_secret" "app_secrets" {
  name        = "${var.environment}/${var.app_name}/secrets"
  description = "Secrets for the ${var.app_name} application in ${var.environment} environment"
  
  tags = {
    Environment = var.environment
    Application = var.app_name
  }
}

resource "aws_secretsmanager_secret_version" "app_secrets" {
  secret_id     = aws_secretsmanager_secret.app_secrets.id
  secret_string = jsonencode({
    SECRET_KEY            = var.secret_key
    DB_USER               = var.db_username
    DB_PASSWORD           = var.db_password
    AWS_ACCESS_KEY_ID     = var.aws_access_key_id
    AWS_SECRET_ACCESS_KEY = var.aws_secret_access_key
  })
}