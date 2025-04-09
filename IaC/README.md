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
