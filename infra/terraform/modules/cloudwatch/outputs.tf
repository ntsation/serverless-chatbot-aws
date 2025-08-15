output "logs_role_arn" {
  description = "ARN of the CloudWatch logs role for AppSync"
  value       = aws_iam_role.appsync_logs.arn
}

output "log_group_arn" {
  description = "ARN of the CloudWatch log group"
  value       = aws_cloudwatch_log_group.appsync.arn
}