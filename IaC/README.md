# Infrastructure as Code (IaC)

This directory contains all the infrastructure and deployment code for the Wagtail project, using AWS services and Cloudflare for DNS.

## Contents

- **docker/**: Docker configuration for production
- **terraform/**: Terraform code for provisioning AWS resources
- **cicd/**: CI/CD configuration for GitHub Actions

## Infrastructure Overview

The project is set up to run on AWS with the following components:

- **Compute**: Amazon ECS (Elastic Container Service) with Fargate
- **Database**: Amazon RDS for PostgreSQL
- **Static Files**: Amazon S3 for static file storage
- **Container Registry**: Amazon ECR for Docker images
- **Secrets Management**: AWS Secrets Manager
- **DNS**: Cloudflare (free tier)

## Required Credentials

### AWS

- AWS Access Key ID
- AWS Secret Access Key
- AWS Region (default: us-east-1)

### Cloudflare

- Cloudflare API Token
- Cloudflare Zone ID

## Deployment Environments

1. **Development**: For day-to-day development work
2. **Testing**: For testing new features before pre-production
3. **Pre-production**: Final testing environment that mirrors production
4. **Production**: Live environment for end users

## Quick Start

### Prerequisites

1. [AWS CLI](https://aws.amazon.com/cli/) installed and configured
2. [Terraform](https://www.terraform.io/downloads.html) (>= 1.0.0) installed
3. [Docker](https://docs.docker.com/get-docker/) installed
4. GitHub repository secrets configured for CI/CD

### Local Deployment (Development)

1. Clone the repository
2. Navigate to the project directory:

   ```bash

   cd myproject

   ```

3. Deploy the infrastructure:

   ```bash

   cd IaC/terraform/environments/development
   cp terraform.tfvars.example terraform.tfvars
   # Edit terraform.tfvars with your credentials
   terraform init
   terraform apply
   ```

### CI/CD Workflow

The project is configured with GitHub Actions workflows:

- **CI Pipeline**: Runs on every push to main and develop branches
  - Lint and test code
  - Build and push Docker image to ECR

- **CD Pipeline**: Runs after successful CI pipeline or manually triggered
  - Deploys infrastructure using Terraform
  - Updates ECS service with new Docker image

## Environment Specific Configurations

Each environment (dev, test, pre-prod, prod) has its own:

- Terraform configuration
- ECR repository
- ECS cluster
- RDS database
- S3 bucket for static files

## Using This IaC with an Existing Project

This IaC setup can be easily adapted to an existing Wagtail project. See the detailed instructions in [adapting-to-existing-project.md](adapting-to-existing-project.md) for step-by-step guidance on how to:

1. Copy the IaC folder to your existing project
2. Adapt configuration files to your project's structure
3. Update your Django settings to work with AWS resources
4. Deploy your existing project to AWS using this infrastructure

## Customization

To customize the infrastructure:

1. Update terraform modules in `terraform/modules/`
2. Modify environment-specific configurations in `terraform/environments/`
3. Update Docker configuration in `docker/`
4. Adjust CI/CD workflows in `cicd/github-actions/` \


Adapting IaC to an Existing Wagtail Project - Comprehensive Guide
This guide provides detailed instructions for adapting the Infrastructure as Code (IaC) folder to deploy an existing Wagtail project on AWS with Cloudflare DNS.

Prerequisites
An existing Wagtail project with PostgreSQL database
Docker installed locally
AWS account (free tier eligible)
Cloudflare account (free tier eligible)
Terraform CLI installed
AWS CLI installed and configured
Git installed
Step 1: Copy the IaC Structure
Copy the entire IaC folder to your project root:
cp -r /path/to/myproject/IaC /path/to/your-project/

Copy


Send command to Terminal
Copy CI/CD workflows to your project:
mkdir -p /path/to/your-project/.github/workflows
cp /path/to/myproject/IaC/cicd/github-actions/*.yml /path/to/your-project/.github/workflows/

Copy


Send command to Terminal
Step 2: Update Project-Specific Settings
2.1 Update Application Name
Rename the application in Terraform variable files:
cd /path/to/your-project/IaC/terraform/environments
find . -name "*.tfvars.example" -exec sed -i 's/wagtail-app/your-app-name/g' {} \;

Copy


Send command to Terminal
Create environment-specific variable files from examples:
cd /path/to/your-project/IaC/terraform/environments/development
cp terraform.tfvars.example terraform.tfvars

Copy


Send command to Terminal
cd /path/to/your-project/IaC/terraform/environments/staging
cp terraform.tfvars.example terraform.tfvars

Copy


Send command to Terminal
cd /path/to/your-project/IaC/terraform/environments/production
cp terraform.tfvars.example terraform.tfvars

Copy


Send command to Terminal
Edit each terraform.tfvars file to customize:
AWS region
Application name
Domain names
Instance types
Database parameters
2.2 Update Docker Configuration
Review and update the Dockerfile:
vi /path/to/your-project/IaC/docker/Dockerfile.prod

Copy


Send command to Terminal
Update the Docker Compose file if needed:
vi /path/to/your-project/IaC/docker/docker-compose.prod.yml

Copy


Send command to Terminal
Check that paths match your project structure:
Ensure the COPY commands reference the correct paths
Update the CMD to use your project's WSGI application
Step 3: Configure Django Settings
Update your Django settings.py to support AWS infrastructure:
# Add to your settings.py

import os

# AWS S3 settings for production
if not DEBUG:
    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME', '')
    AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'us-east-1')
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', '')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', '')
    
    # S3 static settings
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    STATIC_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/static/'
    
    # Media settings
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    MEDIA_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/media/'

# Database settings
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'postgres'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'postgres'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Add ALLOWED_HOSTS configuration
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
if not DEBUG:
    ALLOWED_HOSTS.extend([
        os.environ.get('DOMAIN_NAME', ''),
        '.amazonaws.com',  # Allow ECS tasks
    ])

Copy


settings.py
Add a health check endpoint to your urls.py:
from django.http import HttpResponse

def health_check(request):
    return HttpResponse("OK")
    
urlpatterns = [
    # ... your existing URLs
    path('health/', health_check, name='health_check'),
]

Copy


urls.py
Update your requirements.txt:
echo "django-storages" >> /path/to/your-project/requirements.txt
echo "boto3" >> /path/to/your-project/requirements.txt
echo "gunicorn" >> /path/to/your-project/requirements.txt

Copy


Send command to Terminal
Step 4: Set Up Credentials
Create a credentials file from the example:
cp /path/to/your-project/IaC/credentials-example.env /path/to/your-project/IaC/credentials.env

Copy


Send command to Terminal
Edit the credentials file with your actual values:
vi /path/to/your-project/IaC/credentials.env

Copy


Send command to Terminal
Required credentials to configure:
AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY: AWS credentials with admin permissions
TF_VAR_cloudflare_api_token: Cloudflare API token with DNS permissions
TF_VAR_db_password: Strong password for your PostgreSQL database
TF_VAR_django_secret_key: Secret key for Django
DOCKER_USERNAME and DOCKER_PASSWORD: Docker Hub credentials (if using private images)
Step 5: Initialize Terraform
Initialize Terraform for your chosen environment:
cd /path/to/your-project/IaC/terraform/environments/development
source ../../credentials.env
terraform init

Copy


Send command to Terminal
Validate your Terraform configuration:
terraform validate

Copy


Send command to Terminal
Generate and review a Terraform plan:
terraform plan -out=tfplan

Copy


Send command to Terminal
Step 6: Deploy Infrastructure
Use the deployment script for a streamlined deployment:
cd /path/to/your-project/IaC
chmod +x deploy.sh
./deploy.sh --environment development

Copy


Send command to Terminal
Alternatively, deploy manually with Terraform:
cd /path/to/your-project/IaC/terraform/environments/development
source ../../credentials.env
terraform apply tfplan

Copy


Send command to Terminal
After deployment, Terraform will output important information:
Load balancer URL
Database endpoint
S3 bucket names
Cloudflare DNS settings
Step 7: Configure CI/CD
Update GitHub Actions workflow files to match your project:
vi /path/to/your-project/.github/workflows/deploy-to-aws.yml

Copy


Send command to Terminal
Add the following secrets to your GitHub repository:

AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_REGION
ECR_REPOSITORY_NAME (your app name)
CLOUDFLARE_API_TOKEN
DB_PASSWORD
DJANGO_SECRET_KEY
Configure branch protection rules to trigger deployments:

main branch for production
staging branch for staging
develop branch for development
Step 8: Test and Verify Deployment
Test the application by accessing the load balancer URL:
cd /path/to/your-project/IaC/terraform/environments/development
terraform output alb_dns_name

Copy


Send command to Terminal
Check CloudWatch logs for any errors:
aws logs get-log-events --log-group-name "/ecs/your-app-name" --log-stream-name "$(aws logs describe-log-streams --log-group-name "/ecs/your-app-name" --query "logStreams[0].logStreamName" --output text)"

Copy


Send command to Terminal
Verify database connectivity:
aws rds describe-db-instances --db-instance-identifier your-app-name-db

Copy


Send command to Terminal
Step 9: Manage Database Migrations
Run migrations through the ECS task:
aws ecs run-task --cluster your-app-name-cluster --task-definition your-app-name-task --overrides '{"containerOverrides": [{"name": "your-app-name", "command": ["python", "manage.py", "migrate"]}]}'

Copy


Send command to Terminal
Create a superuser:
aws ecs run-task --cluster your-app-name-cluster --task-definition your-app-name-task --overrides '{"containerOverrides": [{"name": "your-app-name", "command": ["python", "manage.py", "createsuperuser", "--noinput", "--username", "admin", "--email", "admin@example.com"]}]}'

Copy


Send command to Terminal
Step 10: Scaling and Maintenance
Update the number of ECS tasks for scaling:
cd /path/to/your-project/IaC/terraform/environments/production
vi terraform.tfvars
# Update the desired_count variable
terraform apply

Copy


Send command to Terminal
Update the application:
cd /path/to/your-project/IaC
./deploy.sh --environment production --skip-terraform

Copy


Send command to Terminal
Troubleshooting
Common Issues and Solutions
Build errors:

Check Docker build logs: docker build -f IaC/docker/Dockerfile.prod .
Ensure all dependencies are properly specified
Database connection issues:

Verify security group rules in AWS console
Check DB_HOST environment variable is correctly set
Test connection with: psql -h <db-endpoint> -U <username> -d <dbname>
Static files not loading:

Verify S3 bucket permissions
Check AWS credentials are correctly set
Run collectstatic manually: aws ecs run-task --cluster your-app-name-cluster --task-definition your-app-name-task --overrides '{"containerOverrides": [{"name": "your-app-name", "command": ["python", "manage.py", "collectstatic", "--noinput"]}]}'
Health check failures:

Verify the /health/ endpoint is accessible
Check ECS task logs for application errors
Ensure the application is binding to 0.0.0.0:8000
DNS issues:

Verify Cloudflare API token has correct permissions
Check DNS records in Cloudflare dashboard
Test DNS resolution: dig your-domain.com
Cleanup
To destroy the infrastructure when no longer needed:

cd /path/to/your-project/IaC/terraform/environments/development
source ../../credentials.env
terraform destroy

Copy


Send command to Terminal
Remember to repeat this process for each environment you've deployed.