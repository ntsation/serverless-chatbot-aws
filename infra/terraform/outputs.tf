output "cognito_user_pool_id" {
  description = "ID of the Cognito User Pool"
  value       = module.cognito.user_pool_id
}

output "cognito_user_pool_client_id" {
  description = "ID of the Cognito User Pool Client"
  value       = module.cognito.user_pool_client_id
}

output "cognito_domain" {
  description = "Domain of the Cognito User Pool"
  value       = module.cognito.user_pool_domain
}

output "cognito_login_url" {
  description = "Cognito Hosted UI Login URL"
  value       = module.cognito.hosted_ui_login_url
}

output "cognito_logout_url" {
  description = "Cognito Hosted UI Logout URL"
  value       = module.cognito.hosted_ui_logout_url
}

output "appsync_url" {
  description = "AppSync GraphQL URL"
  value       = module.appsync.api_url
}

output "appsync_api_key" {
  description = "AppSync API Key"
  value       = module.appsync.api_key
  sensitive   = true
}

output "appsync_realtime_url" {
  description = "AppSync Real-time WebSocket URL"
  value       = module.appsync.realtime_url
}

output "users_table_name" {
  description = "Name of the Users DynamoDB table"
  value       = module.dynamodb.users_table_name
}

output "chats_table_name" {
  description = "Name of the Chats DynamoDB table"
  value       = module.dynamodb.chats_table_name
}

output "messages_table_name" {
  description = "Name of the Messages DynamoDB table"
  value       = module.dynamodb.messages_table_name
}

output "ecr_repository_url" {
  description = "URL of the ECR repository"
  value       = module.ecr.orchestrator_repository_url
}
