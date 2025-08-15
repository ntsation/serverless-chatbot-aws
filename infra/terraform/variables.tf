variable region {
  type        = string
  default     = "us-east-1"
  description = "The AWS region to deploy the resources"
}

variable "project_name" {
  type        = string
  default     = "chatbot"
  description = "The name of the project"
}