provider "aws" {
  region = var.aws_region
}

terraform {
  required_version = ">= 1.0.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 4.0"
    }
  }
  
  backend "s3" {
    bucket = "terraform-state-myproject-prod"
    key    = "terraform.tfstate"
    region = "us-east-1"
  }
}

provider "cloudflare" {
  api_token = var.cloudflare_api_token
}

# Networking
module "networking" {
  source = "../../modules/networking"
  
  environment          = "prod"
  vpc_cidr             = var.vpc_cidr
  public_subnets       = var.public_subnets
  private_subnets      = var.private_subnets
  availability_zones   = var.availability_zones
  create_nat_gateway   = true  # For production workloads
}

# ECR Repository
module "ecr" {
  source = "../../modules/ecr"
  
  environment     = "prod"
  repository_name = var.app_name
}

# S3 Bucket for Static Files
module "s3" {
  source = "../../modules/s3"
  
  environment                  = "prod"
  bucket_name                  = "${var.app_name}-static"
  cors_allowed_origins         = [var.domain_name, "*.${var.domain_name}"]
  create_cloudfront_distribution = true  # Use CloudFront in production
}

# Secrets Manager
module "secrets" {
  source = "../../modules/secrets"
  
  environment           = "prod"
  app_name              = var.app_name
  secret_key            = var.secret_key
  db_username           = var.db_username
  db_password           = var.db_password
  aws_access_key_id     = var.aws_access_key_id
  aws_secret_access_key = var.aws_secret_access_key
}

# RDS Database
module "rds" {
  source = "../../modules/rds"
  
  environment          = "prod"
  private_subnet_ids   = module.networking.private_subnet_ids
  rds_security_group_id = module.networking.rds_security_group_id
  db_name              = var.db_name
  db_username          = var.db_username
  db_password          = var.db_password
  db_master_password   = var.db_password
  db_instance_class    = "db.t3.small"  # Higher tier for production
  allocated_storage    = 30
  max_allocated_storage = 100
}

# ECS
module "ecs" {
  source = "../../modules/ecs"
  
  environment          = "prod"
  app_name             = var.app_name
  vpc_id               = module.networking.vpc_id
  private_subnet_ids   = module.networking.private_subnet_ids
  public_subnet_ids    = module.networking.public_subnet_ids
  ecs_security_group_id = module.networking.ecs_security_group_id
  alb_security_group_id = module.networking.alb_security_group_id
  ecr_repository_url   = module.ecr.repository_url
  app_image_tag        = var.app_image_tag
  db_host              = module.rds.db_instance_address
  db_name              = var.db_name
  secrets_arn          = module.secrets.secret_arn
  s3_bucket_name       = module.s3.bucket_id
  domain_name          = var.domain_name
  allowed_hosts        = "${var.domain_name},*.${var.domain_name}"
  aws_region           = var.aws_region
  acm_certificate_arn  = var.acm_certificate_arn
  fargate_cpu          = 512  # 0.5 vCPU - Better for production
  fargate_memory       = 1024 # 1GB memory - Better for production
  app_count            = 2    # Multiple instances for redundancy
}

# Cloudflare DNS
resource "cloudflare_record" "site_root" {
  zone_id = var.cloudflare_zone_id
  name    = "@"  # Root domain
  content   = module.ecs.alb_dns_name
  type    = "CNAME"
  ttl     = 1
  proxied = true
}

resource "cloudflare_record" "site_www" {
  zone_id = var.cloudflare_zone_id
  name    = "www"
  content   = module.ecs.alb_dns_name
  type    = "CNAME"
  ttl     = 1
  proxied = true
}

# GitHub Actions IAM Role and Policy
module "github_actions_iam" {
  source = "../../modules/iam"
  
  environment = "prod"
  github_org  = "Kishoraditya"
  github_repo = "myproject"
}

output "github_actions_role_arn" {
  value = module.github_actions_iam.github_actions_role_arn
}

output "github_actions_role_name" {
  value = module.github_actions_iam.github_actions_role_name
}

