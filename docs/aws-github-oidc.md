# Setting up AWS OIDC Authentication for GitHub Actions

This document provides step-by-step instructions for setting up OIDC (OpenID Connect) authentication between GitHub Actions and AWS, which allows GitHub Actions to assume IAM roles without storing AWS credentials as GitHub secrets.

## 1. Create an OIDC Identity Provider in AWS

1. Sign in to the AWS Management Console
2. Navigate to IAM → Identity providers → Add provider
3. Select "OpenID Connect" as the provider type
4. Enter `token.actions.githubusercontent.com` as the provider URL
5. Enter `sts.amazonaws.com` as the audience
6. Click "Add provider"

## 2. Create an IAM Role for GitHub Actions

1. Go to IAM → Roles → Create role
2. Select "Web identity" as the trusted entity type
3. For Identity Provider, select `token.actions.githubusercontent.com`
4. For Audience, select `sts.amazonaws.com`
5. Add a condition to restrict access to your specific repository:
   - Condition: `StringLike`
   - Key: `token.actions.githubusercontent.com:sub`
   - Value: `repo:your-org/shoshin_0304:*` (replace with your GitHub org/user and repo name)
6. Click "Next"

## 3. Attach Permissions to the IAM Role

Instead of attaching multiple managed policies that may exceed the limit, create a custom policy:

1. In the role creation process, select "Create policy"
2. Use the JSON editor and paste the following policy:

{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ecr:GetAuthorizationToken",
                "ecr:BatchCheckLayerAvailability",
                "ecr:GetDownloadUrlForLayer",
                "ecr:BatchGetImage",
                "ecr:InitiateLayerUpload",
                "ecr:UploadLayerPart",
                "ecr:CompleteLayerUpload",
                "ecr:PutImage",
                "ecr:CreateRepository",
                "ecr:DescribeRepositories",
                "ecr:DeleteRepository",
                "ecr:TagResource",
                "ecr:ListTagsForResource",
                "ecr:UntagResource",
                "ecr:GetLifecyclePolicy",
                "ecr:PutLifecyclePolicy"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "ecs:DescribeServices",
                "ecs:UpdateService",
                "ecs:CreateService",
                "ecs:DeleteService",
                "ecs:RegisterTaskDefinition",
                "ecs:DeregisterTaskDefinition",
                "ecs:DescribeTaskDefinition",
                "ecs:DescribeClusters",
                "ecs:CreateCluster",
                "ecs:DeleteCluster",
                "ecs:TagResource",
                "ecs:UntagResource",
                "ecs:ListTagsForResource"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket",
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:CreateBucket",
                "s3:PutBucketVersioning",
                "s3:PutEncryptionConfiguration",
                "s3:PutBucketPublicAccessBlock",
                "s3:GetEncryptionConfiguration",
                "s3:GetBucketVersioning",
                "s3:GetBucketPolicy",
                "s3:PutBucketPolicy",
                "s3:GetBucketPolicyStatus",
                "s3:GetBucketTagging",
                "s3:PutBucketTagging",
                "s3:ListBucketVersions",
                "s3:GetBucketAcl",
                "s3:PutBucketAcl",
                "s3:GetBucketCors",
                "s3:PutBucketCors",
                "s3:GetBucketLogging",
                "s3:PutBucketLogging",
                "s3:GetBucketRequestPayment",
                "s3:PutBucketRequestPayment",
                "s3:GetBucketWebsite",
                "s3:PutBucketWebsite",
                "s3:GetAccelerateConfiguration",
                "s3:PutAccelerateConfiguration",
                "s3:GetLifecycleConfiguration",
                "s3:PutLifecycleConfiguration"
            ],
            "Resource": [
                "arn:aws:s3:::terraform-state-myproject-*",
                "arn:aws:s3:::*-wagtail-app-static",
                "arn:aws:s3:::terraform-state-myproject-*/*",
                "arn:aws:s3:::*-wagtail-app-static/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "cloudfront:CreateDistribution",
                "cloudfront:GetDistribution",
                "cloudfront:UpdateDistribution",
                "cloudfront:DeleteDistribution",
                "cloudfront:TagResource",
                "cloudfront:UntagResource",
                "cloudfront:ListTagsForResource",
                "cloudfront:CreateInvalidation"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "rds:CreateDBInstance",
                "rds:DeleteDBInstance",
                "rds:ModifyDBInstance",
                "rds:DescribeDBInstances",
                "rds:CreateDBSubnetGroup",
                "rds:DeleteDBSubnetGroup",
                "rds:DescribeDBSubnetGroups",
                "rds:CreateDBParameterGroup",
                "rds:DeleteDBParameterGroup",
                "rds:ModifyDBParameterGroup",
                "rds:DescribeDBParameterGroups",
                "rds:AddTagsToResource",
                "rds:RemoveTagsFromResource",
                "rds:ListTagsForResource"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeVpcs",
                "ec2:DescribeSubnets",
                "ec2:DescribeSecurityGroups",
                "ec2:DescribeAddresses",
                "ec2:DescribeAddressesAttribute",
                "ec2:DescribeNetworkInterfaces",
                "ec2:DescribeRouteTables",
                "ec2:DescribeInternetGateways",
                "ec2:CreateSecurityGroup",
                "ec2:DeleteSecurityGroup",
                "ec2:AuthorizeSecurityGroupIngress",
                "ec2:RevokeSecurityGroupIngress",
                "ec2:CreateVpc",
                "ec2:DeleteVpc",
                "ec2:CreateSubnet",
                "ec2:DeleteSubnet",
                "ec2:CreateRoute",
                "ec2:DeleteRoute",
                "ec2:CreateRouteTable",
                "ec2:DeleteRouteTable",
                "ec2:AssociateRouteTable",
                "ec2:DisassociateRouteTable",
                "ec2:CreateInternetGateway",
                "ec2:DeleteInternetGateway",
                "ec2:AttachInternetGateway",
                "ec2:DetachInternetGateway",
                "ec2:AllocateAddress",
                "ec2:ReleaseAddress",
                "ec2:CreateTags",
                "ec2:DeleteTags",
                "ec2:ModifyVpcAttribute",
                "ec2:DescribeVpcAttribute",
                "ec2:DescribeNetworkAcls",
                "ec2:DescribeVpcPeeringConnections",
                "ec2:DescribeVpcEndpointServices",
                "ec2:DescribeVpcEndpoints",
                "ec2:DescribeVpcClassicLink",
                "ec2:DescribeVpcClassicLinkDnsSupport"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "elasticloadbalancing:CreateLoadBalancer",
                "elasticloadbalancing:DeleteLoadBalancer",
                "elasticloadbalancing:DescribeLoadBalancers",
                "elasticloadbalancing:DescribeLoadBalancerAttributes",
                "elasticloadbalancing:ModifyLoadBalancerAttributes",
                "elasticloadbalancing:CreateTargetGroup",
                "elasticloadbalancing:DeleteTargetGroup",
                "elasticloadbalancing:DescribeTargetGroups",
                "elasticloadbalancing:DescribeTargetGroupAttributes",
                "elasticloadbalancing:CreateRule",
                "elasticloadbalancing:DeleteRule",
                "elasticloadbalancing:CreateListener",
                "elasticloadbalancing:DeleteListener",
                "elasticloadbalancing:AddTags",
                "elasticloadbalancing:RemoveTags",
                "elasticloadbalancing:DescribeTags"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:DeleteLogGroup",
                "logs:PutRetentionPolicy",
                "logs:DescribeLogGroups",
                "logs:TagResource",
                "logs:UntagResource",
                "logs:ListTagsLogGroup",
                "logs:ListTagsForResource"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "acm:RequestCertificate",
                "acm:DeleteCertificate",
                "acm:DescribeCertificate",
                "acm:AddTagsToCertificate",
                "acm:RemoveTagsFromCertificate",
                "acm:ListTagsForCertificate"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "iam:CreateRole",
                "iam:DeleteRole",
                "iam:GetRole",
                "iam:ListRolePolicies",
                "iam:GetRolePolicy",
                "iam:AttachRolePolicy",
                "iam:DetachRolePolicy",
                "iam:PutRolePolicy",
                "iam:DeleteRolePolicy",
                "iam:TagRole",
                "iam:UntagRole",
                "iam:ListRoleTags"
            ],
            "Resource": "arn:aws:iam::*:role/*"
        },
        {
            "Effect": "Allow",
            "Action": "iam:PassRole",
            "Resource": "arn:aws:iam::*:role/*",
            "Condition": {
                "StringEquals": {
                    "iam:PassedToService": [
                        "ecs.amazonaws.com",
                        "ecs-tasks.amazonaws.com",
                        "rds.amazonaws.com",
                        "ec2.amazonaws.com",
                        "elasticloadbalancing.amazonaws.com",
                        "logs.amazonaws.com"
                    ]
                }
            }
        },
        {
            "Effect": "Allow",
            "Action": [
                "secretsmanager:CreateSecret",
                "secretsmanager:DeleteSecret",
                "secretsmanager:GetSecretValue",
                "secretsmanager:PutSecretValue",
                "secretsmanager:UpdateSecret",
                "secretsmanager:TagResource",
                "secretsmanager:UntagResource",
                "secretsmanager:DescribeSecret",
                "secretsmanager:GetResourcePolicy",
                "secretsmanager:PutResourcePolicy",
                "secretsmanager:DeleteResourcePolicy",
                "secretsmanager:ListSecrets",
                "secretsmanager:ListSecretVersionIds"
            ],
            "Resource": "*"
        }
    ]
}

3. Name the policy (e.g., "GitHubActionsDeploymentPolicy") and create it
4. Go back to the role creation process and attach the newly created policy
5. Complete the role creation by naming it (e.g., "GitHubActionsRole")

## 4. Get the Role ARN

1. After the role is created, go to the role summary page
2. Copy the Role ARN, which looks like: `arn:aws:iam::123456789012:role/GitHubActionsRole`

## 5. Configure GitHub Repository Secrets

1. Go to your GitHub repository
2. Navigate to Settings → Environments
3. Select or create an environment (e.g., "production")
4. Add a new secret:
   - Name: `AWS_ROLE_TO_ASSUME`
   - Value: The Role ARN you copied in step 4
5. Save the secret

## 6. Update GitHub Actions Workflow File

Our CD workflow file already has the correct configuration:

```yaml
permissions:
  id-token: write
  contents: read

steps:
  - name: Configure AWS credentials
    uses: aws-actions/configure-aws-credentials@v4
    with:
      role-to-assume: ${{ secrets.AWS_ROLE_TO_ASSUME }}
      aws-region: us-east-1
      audience: sts.amazonaws.com
```

## 7. Troubleshooting

If you still encounter issues:

1. Verify that the IAM role's trust policy contains the correct GitHub repository name
2. Check that the role has the necessary permissions for your deployment
3. Ensure the OIDC provider is correctly configured in AWS
4. Confirm that the `id-token: write` permission is set in the workflow file

## 8. Security Best Practices

1. Limit the IAM role permissions to only what's needed
2. Use branch or environment conditions in the role's trust policy
3. Regularly audit and update the permissions
4. Consider using separate roles for different environments

## 9. Managing IAM Policies with Terraform

For better control and versioning of IAM policies, consider managing them through Terraform:

1. Create a Terraform configuration file for IAM:

```hcl
# iam.tf
resource "aws_iam_role" "github_actions" {
  name = "GitHubActionsRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRoleWithWebIdentity"
        Effect = "Allow"
        Principal = {
          Federated = "arn:aws:iam::${var.aws_account_id}:oidc-provider/token.actions.githubusercontent.com"
        }
        Condition = {
          StringLike = {
            "token.actions.githubusercontent.com:sub" = "repo:${var.github_org}/${var.github_repo}:*"
          }
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "github_actions" {
  name = "GitHubActionsDeploymentPolicy"
  role = aws_iam_role.github_actions.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      # ECR permissions
      {
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload",
          "ecr:PutImage",
          "ecr:CreateRepository",
          "ecr:DescribeRepositories",
          "ecr:DeleteRepository",
          "ecr:TagResource",
          "ecr:ListTagsForResource",
          "ecr:UntagResource"
        ]
        Resource = "*"
      },
      # S3 permissions
      {
        Effect = "Allow"
        Action = [
          "s3:ListBucket",
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:CreateBucket",
          "s3:PutBucketVersioning",
          "s3:PutBucketEncryption",
          "s3:PutBucketPublicAccessBlock",
          "s3:GetEncryptionConfiguration",
          "s3:GetBucketVersioning",
          "s3:GetBucketPolicy",
          "s3:PutBucketPolicy",
          "s3:GetBucketPolicyStatus",
          "s3:GetBucketTagging",
          "s3:PutBucketTagging",
          "s3:ListBucketVersions",
          "s3:GetBucketAcl",
          "s3:PutBucketAcl"
        ]
        Resource = [
          "arn:aws:s3:::terraform-state-myproject-*",
          "arn:aws:s3:::terraform-state-myproject-*/*",
          "arn:aws:s3:::*-wagtail-app-static",
          "arn:aws:s3:::*-wagtail-app-static/*"
        ]
      },
      # EC2 permissions
      {
        Effect = "Allow"
        Action = [
          "ec2:DescribeVpcs",
          "ec2:DescribeSubnets",
          "ec2:DescribeSecurityGroups",
          "ec2:DescribeAddresses",
          "ec2:DescribeNetworkInterfaces",
          "ec2:DescribeRouteTables",
          "ec2:DescribeInternetGateways",
          "ec2:CreateSecurityGroup",
          "ec2:DeleteSecurityGroup",
          "ec2:AuthorizeSecurityGroupIngress",
          "ec2:RevokeSecurityGroupIngress",
          "ec2:CreateVpc",
          "ec2:DeleteVpc",
          "ec2:CreateSubnet",
          "ec2:DeleteSubnet",
          "ec2:CreateRoute",
          "ec2:DeleteRoute",
          "ec2:CreateRouteTable",
          "ec2:DeleteRouteTable",
          "ec2:AssociateRouteTable",
          "ec2:DisassociateRouteTable",
          "ec2:CreateInternetGateway",
          "ec2:DeleteInternetGateway",
          "ec2:AttachInternetGateway",
          "ec2:DetachInternetGateway",
          "ec2:AllocateAddress",
          "ec2:ReleaseAddress",
          "ec2:CreateTags",
          "ec2:DeleteTags",
          "ec2:ModifyVpcAttribute",
          "ec2:DescribeVpcAttribute",
          "ec2:DescribeAddressesAttribute"
        ]
        Resource = "*"
      },
      # Secrets Manager permissions
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:CreateSecret",
          "secretsmanager:DeleteSecret",
          "secretsmanager:GetSecretValue",
          "secretsmanager:PutSecretValue",
          "secretsmanager:UpdateSecret",
          "secretsmanager:TagResource",
          "secretsmanager:UntagResource",
          "secretsmanager:DescribeSecret",
          "secretsmanager:GetResourcePolicy",
          "secretsmanager:PutResourcePolicy",
          "secretsmanager:DeleteResourcePolicy"
        ]
        Resource = "*"
      }
      # Add other permission blocks as needed
    ]
  })
}
```

2. Use variables for environment-specific values:

```hcl
# variables.tf
variable "aws_account_id" {
  description = "AWS Account ID"
  type        = string
}

variable "github_org" {
  description = "GitHub organization or username"
  type        = string
}

variable "github_repo" {
  description = "GitHub repository name"
  type        = string
}
```

3. Apply the Terraform configuration:

```bash
terraform init
terraform plan
terraform apply
```

This approach provides several benefits:
- Version control for your IAM policies
- Consistent policy application across environments
- Easier policy updates and rollbacks
- Better security through least privilege principles 