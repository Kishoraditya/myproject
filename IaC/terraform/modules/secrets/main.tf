resource "random_string" "secret_suffix" {
  length  = 6
  special = false
  upper   = false
}

resource "time_sleep" "wait_for_secret_replacement" {
  depends_on = [aws_secretsmanager_secret.app_secrets]
  create_duration = "10s"
}

resource "aws_secretsmanager_secret" "app_secrets" {
  name        = "${var.environment}/${var.app_name}/secrets_"
  description = "Secrets for the ${var.app_name} application in ${var.environment} environment"
  recovery_window_in_days = 0
  depends_on = [time_sleep.wait_for_secret_replacement]
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