output "appsync_role_arn" {
  description = "ARN of the AppSync IAM role"
  value       = aws_iam_role.appsync_role.arn
}

output "lambda_role_arn" {
  description = "ARN of the Lambda IAM role"
  value       = aws_iam_role.lambda_role.arn
}
