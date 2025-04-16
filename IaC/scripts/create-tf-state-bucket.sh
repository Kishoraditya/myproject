#!/bin/bash

# Script to create an S3 bucket for Terraform state if it doesn't exist
# Usage: ./create-tf-state-bucket.sh -b bucket-name -r region

# Exit on command errors, but allow specific commands to fail
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
  
  # Try to enable versioning, but continue if it fails
  echo "Attempting to enable versioning..."
  if aws s3api put-bucket-versioning --bucket "$BUCKET_NAME" --versioning-configuration Status=Enabled; then
    echo "Versioning enabled."
  else
    echo "Warning: Could not enable versioning. This may be due to IAM permissions."
    echo "Continuing without enabling versioning..."
  fi
  
  # Try to enable encryption, but continue if it fails
  echo "Attempting to enable encryption..."
  if aws s3api put-bucket-encryption --bucket "$BUCKET_NAME" --server-side-encryption-configuration '{
    "Rules": [
      {
        "ApplyServerSideEncryptionByDefault": {
          "SSEAlgorithm": "AES256"
        }
      }
    ]
  }'; then
    echo "Encryption enabled."
  else
    echo "Warning: Could not enable encryption. This may be due to IAM permissions."
    echo "Continuing without enabling encryption..."
  fi
  
  # Try to block public access, but continue if it fails
  echo "Attempting to block public access..."
  if aws s3api put-public-access-block --bucket "$BUCKET_NAME" --public-access-block-configuration '{
    "BlockPublicAcls": true,
    "IgnorePublicAcls": true,
    "BlockPublicPolicy": true,
    "RestrictPublicBuckets": true
  }'; then
    echo "Public access blocked."
  else
    echo "Warning: Could not block public access. This may be due to IAM permissions."
    echo "Continuing without blocking public access..."
  fi
  
  echo "Bucket created with best-effort security settings."
fi

echo "S3 bucket setup complete: $BUCKET_NAME"
echo "NOTE: If any warnings appeared above, you may need to manually configure some bucket settings."
echo "      or update the IAM permissions for this role." 