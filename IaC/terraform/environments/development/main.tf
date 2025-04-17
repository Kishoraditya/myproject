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
    bucket = "my-demo-aws-bucket-number456"
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
  
  environment          = "dev"
  vpc_cidr             = var.vpc_cidr
  public_subnets       = var.public_subnets
  private_subnets      = var.private_subnets
  availability_zones   = var.availability_zones
  create_nat_gateway   = false  # Save costs in dev
}

# ECR Repository
module "ecr" {
  source = "../../modules/ecr"
  
  environment     = "dev"
  repository_name = var.app_name
}

# S3 Bucket for Static Files
module "s3" {
  source = "../../modules/s3"
  
  environment                  = "dev"
  bucket_name                  = "${var.app_name}-static"
  cors_allowed_origins         = ["*"]
  create_cloudfront_distribution = false  # Save costs in dev
}

# Secrets Manager
module "secrets" {
  source = "../../modules/secrets"
  
  environment           = "dev"
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
  
  environment          = "dev"
  private_subnet_ids   = module.networking.private_subnet_ids
  rds_security_group_id = module.networking.rds_security_group_id
  db_name              = var.db_name
  db_username          = var.db_username
  db_password          = var.db_password
  db_master_password = var.db_password
  db_instance_class    = "db.t3.micro"  # Free tier eligible
  allocated_storage    = 20
  max_allocated_storage = 100
}

# ECS
module "ecs" {
  source = "../../modules/ecs"
  
  environment          = "dev"
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
  acm_certificate_arn = var.acm_certificate_arn
  fargate_cpu          = 256  # 0.25 vCPU - Free tier eligible
  fargate_memory       = 512  # Free tier eligible
}

# Cloudflare DNS
resource "cloudflare_record" "site" {
  zone_id = var.cloudflare_zone_id
  name    = "dev"
  content   = module.ecs.alb_dns_name
  type    = "CNAME"
  ttl     = 1
  proxied = true
} 

resource "cloudflare_record" "apex" {
  zone_id = var.cloudflare_zone_id
  name    = "@"           # This represents the root domain (shoshin.world)
  content = module.ecs.alb_dns_name
  type    = "CNAME"
  ttl     = 1
  proxied = true
}


# GitHub Actions IAM Role and Policy
module "github_actions_iam" {
  source = "../../modules/iam"
  
  environment = "dev"
  github_org  = "Kishoraditya"
  github_repo = "myproject"
}

output "github_actions_role_arn" {
  value = module.github_actions_iam.github_actions_role_arn
}

output "github_actions_role_name" {
  value = module.github_actions_iam.github_actions_role_name
}

