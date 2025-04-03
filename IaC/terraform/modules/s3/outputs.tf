output "bucket_id" {
  value       = aws_s3_bucket.static.id
  description = "The name of the bucket"
}

output "bucket_arn" {
  value       = aws_s3_bucket.static.arn
  description = "The ARN of the bucket"
}

output "bucket_regional_domain_name" {
  value       = aws_s3_bucket.static.bucket_regional_domain_name
  description = "The regional domain name of the bucket"
}

output "cloudfront_domain_name" {
  value       = var.create_cloudfront_distribution ? aws_cloudfront_distribution.s3_distribution[0].domain_name : null
  description = "The domain name of the CloudFront distribution"
} 