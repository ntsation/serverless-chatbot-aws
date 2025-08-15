output "api_id" {
  description = "ID of the AppSync API"
  value       = aws_appsync_graphql_api.api.id
}

output "api_arn" {
  description = "ARN of the AppSync API"
  value       = aws_appsync_graphql_api.api.arn
}

output "api_url" {
  description = "URL of the AppSync API"
  value       = aws_appsync_graphql_api.api.uris["GRAPHQL"]
}