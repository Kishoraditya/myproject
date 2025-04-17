provider "aws" {
  region = "us-east-1"
}

resource "aws_iam_openid_connect_provider" "github_actions" {
  url             = "https://token.actions.githubusercontent.com"
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = ["6938fd4d98bab03faadb97b34396831e3780aea1"]
  
  lifecycle {
    ignore_changes = [thumbprint_list]
  }
}

output "oidc_provider_arn" {
  value = aws_iam_openid_connect_provider.github_actions.arn
}
