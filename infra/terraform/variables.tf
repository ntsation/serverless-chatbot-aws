variable "region" {
  type        = string
  default     = "us-east-1"
  description = "The AWS region to deploy the resources"
}

variable "project_name" {
  type        = string
  default     = "chatbot"
  description = "The name of the project"
}

variable "callback_urls" {
  type        = list(string)
  default     = ["http://localhost:3000/callback", "https://localhost:3000/callback"]
  description = "List of allowed callback URLs for the Cognito User Pool Client"
}

variable "logout_urls" {
  type        = list(string)
  default     = ["http://localhost:3000/", "https://localhost:3000/"]
  description = "List of allowed logout URLs for the Cognito User Pool Client"
}

variable "bedrock_model" {
  type        = string
  default     = "amazon.nova-micro-v1:0"
  description = "The Bedrock model ID to use for the chatbot"
}

variable "bedrock_region" {
  type        = string
  default     = "us-east-1"
  description = "The AWS region for Bedrock"
}