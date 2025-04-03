# Deployment Guide

This guide explains how to deploy your Wagtail application to AWS using the IaC (Infrastructure as Code) setup provided in this repository.

## Quick Reference

- **Development Environment**: For day-to-day development work
- **Testing Environment**: For testing new features before pre-production
- **Pre-production Environment**: Final testing environment that mirrors production
- **Production Environment**: Live environment for end users

## Prerequisites

Before you start, make sure you have:

1. An AWS account (free tier eligible)
2. A Cloudflare account (free tier)
3. The following tools installed:
   - AWS CLI
   - Terraform (>= 1.0.0)
   - Docker
   - Git

## Step 1: Clone the Repository

```bash
git clone https://github.com/your-username/myproject.git
cd myproject
```

## Step 2: Set Up Credentials

1. Copy the example credentials file:
   ```bash
   cp IaC/credentials-example.env IaC/credentials.env
   ```

2. Edit the `IaC/credentials.env` file with your actual credentials:
   - AWS credentials
   - Cloudflare credentials
   - Database credentials
   - Django secret key

## Step 3: Deploy Infrastructure

There are two ways to deploy:

### Option 1: Using the deploy script (Recommended)

```bash
# Make the script executable (Linux/Mac)
chmod +x IaC/deploy.sh

# Deploy to development environment
./IaC/deploy.sh --environment development

# Or deploy to production
./IaC/deploy.sh --environment production
```

### Option 2: Manually using Terraform

```bash
# For development
cd IaC/terraform/environments/development
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your actual values
terraform init
terraform plan -out=tfplan
terraform apply tfplan

# Similar steps for other environments (testing, preproduction, production)
```

## Step 4: Connect to Your Application

After deployment completes, you can access your application at:

- Development: `dev.example.com` (or whatever domain you configured)
- Testing: `test.example.com`
- Pre-production: `preprod.example.com`
- Production: `example.com` and `www.example.com`

## Step 5: CI/CD Setup (For GitHub)

1. Add the required secrets to your GitHub repository:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_REGION`
   - `DB_USERNAME`
   - `DB_PASSWORD`
   - `DJANGO_SECRET_KEY`
   - `S3_ACCESS_KEY_ID`
   - `S3_SECRET_ACCESS_KEY`
   - `DOMAIN_NAME`
   - `CLOUDFLARE_API_TOKEN`
   - `CLOUDFLARE_ZONE_ID`

2. Push to the repository to trigger the CI/CD pipeline:
   - Pushing to `develop` branch deploys to development
   - Pushing to `main` branch deploys to production

## Resource Management

### AWS Resources Created

- **VPC** with public and private subnets
- **ECS Cluster** with Fargate for running containers
- **RDS PostgreSQL** database
- **S3 Bucket** for static file storage
- **ECR Repository** for Docker images
- **Secrets Manager** for sensitive information
- **Load Balancer** for traffic management

### Cloudflare Resources

- DNS records pointing to your AWS load balancer
- Automatic SSL/TLS encryption
- DDoS protection

## Cost Management

This setup uses AWS Free Tier eligible resources where possible:

- t3.micro instances for RDS
- Fargate with minimal CPU/memory for development
- S3 with lifecycle policies to minimize storage costs

To further reduce costs, you can:
- Destroy development/testing environments when not in use
- Use the `terraform destroy` command to remove all resources
- Monitor your AWS billing dashboard regularly

## Troubleshooting

If you encounter issues:

1. Check CloudWatch Logs for application errors
2. Verify correct values in terraform.tfvars
3. Ensure proper DNS configuration in Cloudflare
4. Check GitHub Actions logs for CI/CD errors

For more information, see the full documentation in the `IaC/README.md` file. 