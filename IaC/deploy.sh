#!/bin/bash

set -e

# ANSI color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default environment
ENV="development"

# Help message
function show_help {
  echo -e "${BLUE}Wagtail Project Deployment Script${NC}"
  echo ""
  echo "Usage: ./deploy.sh [OPTIONS]"
  echo ""
  echo "Options:"
  echo "  -e, --environment ENV   Specify environment (development, testing, preproduction, production)"
  echo "  -h, --help              Show this help message"
  echo ""
  echo "Example:"
  echo "  ./deploy.sh --environment production"
}

# Parse arguments
while [[ "$#" -gt 0 ]]; do
  case $1 in
    -e|--environment) ENV="$2"; shift ;;
    -h|--help) show_help; exit 0 ;;
    *) echo "Unknown parameter: $1"; show_help; exit 1 ;;
  esac
  shift
done

# Validate environment
if [[ ! "$ENV" =~ ^(development|testing|preproduction|production)$ ]]; then
  echo -e "${RED}Error: Invalid environment. Must be development, testing, preproduction or production.${NC}"
  exit 1
fi

# Map environment to terraform workspace
case $ENV in
  development) TF_ENV="development" ;;
  testing) TF_ENV="testing" ;;
  preproduction) TF_ENV="preproduction" ;;
  production) TF_ENV="production" ;;
esac

# Check if credentials file exists
if [ ! -f "credentials.env" ]; then
  echo -e "${RED}Error: credentials.env file not found.${NC}"
  echo -e "Please create one using the template in credentials-example.env"
  exit 1
fi

# Load credentials
echo -e "${BLUE}Loading credentials...${NC}"
source credentials.env

# Check for AWS CLI
if ! command -v aws &> /dev/null; then
  echo -e "${RED}Error: AWS CLI not found. Please install it first.${NC}"
  exit 1
fi

# Check for Terraform
if ! command -v terraform &> /dev/null; then
  echo -e "${RED}Error: Terraform not found. Please install it first.${NC}"
  exit 1
fi

# Configure AWS credentials
echo -e "${BLUE}Configuring AWS credentials...${NC}"
aws configure set aws_access_key_id $AWS_ACCESS_KEY_ID
aws configure set aws_secret_access_key $AWS_SECRET_ACCESS_KEY
aws configure set region $AWS_REGION

# Check if S3 bucket for Terraform state exists
BUCKET_NAME="terraform-state-myproject-${TF_ENV:0:4}"
if ! aws s3api head-bucket --bucket $BUCKET_NAME 2>/dev/null; then
  echo -e "${YELLOW}Creating S3 bucket for Terraform state...${NC}"
  aws s3api create-bucket --bucket $BUCKET_NAME --region $AWS_REGION
  aws s3api put-bucket-versioning --bucket $BUCKET_NAME --versioning-configuration Status=Enabled
  aws s3api put-bucket-encryption --bucket $BUCKET_NAME --server-side-encryption-configuration '{"Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]}'
fi

# Navigate to the correct Terraform directory
cd terraform/environments/$TF_ENV

# Create tfvars file
echo -e "${BLUE}Creating terraform.tfvars file...${NC}"
cat > terraform.tfvars <<EOF
aws_region             = "$AWS_REGION"
app_name               = "wagtail-app"
app_image_tag          = "latest"
db_username            = "$DB_USERNAME"
db_password            = "$DB_PASSWORD"
secret_key             = "$DJANGO_SECRET_KEY"
aws_access_key_id      = "$S3_ACCESS_KEY_ID"
aws_secret_access_key  = "$S3_SECRET_ACCESS_KEY"
domain_name            = "$DOMAIN_NAME"
cloudflare_api_token   = "$CLOUDFLARE_API_TOKEN"
cloudflare_zone_id     = "$CLOUDFLARE_ZONE_ID"
EOF

# Initialize Terraform
echo -e "${BLUE}Initializing Terraform...${NC}"
terraform init

# Create execution plan
echo -e "${BLUE}Creating Terraform plan...${NC}"
terraform plan -out=tfplan

# Confirm before applying
read -p "Do you want to apply this plan? (yes/no): " confirm
if [[ $confirm != "yes" ]]; then
  echo -e "${YELLOW}Deployment cancelled.${NC}"
  exit 0
fi

# Apply Terraform plan
echo -e "${BLUE}Applying Terraform plan...${NC}"
terraform apply -auto-approve tfplan

# Display outputs
echo -e "${GREEN}Deployment complete!${NC}"
echo -e "${BLUE}Terraform outputs:${NC}"
terraform output

echo -e "${GREEN}Your Wagtail application is now being deployed to the $ENV environment.${NC}"
echo -e "The deployment may take a few minutes to complete as ECS tasks are updated."
echo -e "You can check the status of your ECS service in the AWS console."

if [ "$ENV" = "production" ]; then
  echo -e "${YELLOW}IMPORTANT: This is a production deployment. Please verify everything is working correctly.${NC}"
fi 