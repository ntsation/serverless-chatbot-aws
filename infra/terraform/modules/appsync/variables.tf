variable "project_name" {
  description = "The name of the project"
  type        = string
}

variable "region" {
  description = "AWS region"
  type        = string
}

variable "schema_path" {
  description = "Path to the GraphQL schema file"
  type        = string
}

variable "cognito_user_pool_id" {
  description = "Cognito User Pool ID"
  type        = string
}

variable "users_table" {
  description = "Name of the users DynamoDB table"
  type        = string
}

variable "chats_table" {
  description = "Name of the chats DynamoDB table"
  type        = string
}

variable "messages_table" {
  description = "Name of the messages DynamoDB table"
  type        = string
}

variable "lambda_arn" {
  description = "ARN of the Lambda orchestrator function"
  type        = string
}

variable "appsync_role_arn" {
  description = "ARN of the AppSync IAM role"
  type        = string
}

variable "cloudwatch_logs_role_arn" {
  description = "ARN of the CloudWatch logs role for AppSync"
  type        = string
}