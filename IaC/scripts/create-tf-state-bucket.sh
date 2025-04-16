#!/bin/bash

# Script to create an S3 bucket for Terraform state if it doesn't exist
# Usage: ./create-tf-state-bucket.sh -b bucket-name -r region

set -e

# Default values
BUCKET_NAME=""
REGION="us-east-1"

# Parse command line arguments
while getopts ":b:r:" opt; do
  case ${opt} in
    b )
      BUCKET_NAME=$OPTARG
      ;;
    r )
      REGION=$OPTARG
      ;;
    \? )
      echo "Invalid option: $OPTARG" 1>&2
      exit 1
      ;;
    : )
      echo "Option -$OPTARG requires an argument." 1>&2
      exit 1
      ;;
  esac
done

# Check if bucket name is provided
if [ -z "$BUCKET_NAME" ]; then
  echo "Bucket name is required. Usage: ./create-tf-state-bucket.sh -b bucket-name -r region"
  exit 1
fi

echo "Creating S3 bucket for Terraform state if it doesn't exist..."
echo "Bucket name: $BUCKET_NAME"
echo "Region: $REGION"

# Check if bucket exists
if aws s3api head-bucket --bucket "$BUCKET_NAME" 2>/dev/null; then
  echo "Bucket already exists: $BUCKET_NAME"
else
  echo "Creating bucket: $BUCKET_NAME"
  
  # Create bucket (different commands for us-east-1 vs other regions)
  if [ "$REGION" = "us-east-1" ]; then
    aws s3api create-bucket --bucket "$BUCKET_NAME" --region "$REGION"
  else
    aws s3api create-bucket --bucket "$BUCKET_NAME" --region "$REGION" --create-bucket-configuration LocationConstraint="$REGION"
  fi
  
  # Enable versioning
  aws s3api put-bucket-versioning --bucket "$BUCKET_NAME" --versioning-configuration Status=Enabled
  
  # Enable encryption
  aws s3api put-bucket-encryption --bucket "$BUCKET_NAME" --server-side-encryption-configuration '{
    "Rules": [
      {
        "ApplyServerSideEncryptionByDefault": {
          "SSEAlgorithm": "AES256"
        }
      }
    ]
  }'
  
  # Block public access
  aws s3api put-public-access-block --bucket "$BUCKET_NAME" --public-access-block-configuration '{
    "BlockPublicAcls": true,
    "IgnorePublicAcls": true,
    "BlockPublicPolicy": true,
    "RestrictPublicBuckets": true
  }'
  
  echo "Bucket created with versioning, encryption, and public access blocked"
fi

echo "S3 bucket setup complete: $BUCKET_NAME" 