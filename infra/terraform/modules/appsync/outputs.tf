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

output "api_key" {
  description = "API Key for the AppSync API"
  value       = aws_appsync_api_key.api_key.key
  sensitive   = true
}

output "realtime_url" {
  description = "Real-time WebSocket URL of the AppSync API"
  value       = aws_appsync_graphql_api.api.uris["REALTIME"]
}