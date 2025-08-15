variable "project_name" {
  description = "The name of the project"
  type        = string
}

variable "users_table_arn" {
  description = "ARN of the users DynamoDB table"
  type        = string
}

variable "chats_table_arn" {
  description = "ARN of the chats DynamoDB table"
  type        = string
}

variable "messages_table_arn" {
  description = "ARN of the messages DynamoDB table"
  type        = string
}

variable "lambda_arn" {
  description = "ARN of the Lambda function"
  type        = string
}

variable "appsync_api_arn" {
  description = "ARN of the AppSync API"
  type        = string
}
