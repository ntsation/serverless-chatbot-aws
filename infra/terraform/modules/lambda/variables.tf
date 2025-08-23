variable "project_name" {
  description = "The name of the project."
  type        = string
}

variable "ecr_repository_url" {
  description = "The URL of the ECR repository."
  type        = string
}

variable "region" {
  description = "The AWS region."
  type        = string
}

variable "lambda_role_arn" {
  description = "ARN of the Lambda IAM role"
  type        = string
}

variable "appsync_url" {
  description = "URL of the AppSync API"
  type        = string
}

variable "appsync_api_key" {
  description = "API Key for AppSync"
  type        = string
  sensitive   = true
}