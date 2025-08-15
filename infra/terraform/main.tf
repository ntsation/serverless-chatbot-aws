terraform {
  required_providers {
    aws = { source = "hashicorp/aws"}
    archive = { source = "hashicorp/archive"}
  }
}

provider "aws" {
  region = var.region
}

module "dynamodb" {
  source        = "./modules/dynamodb"
  project_name  = var.project_name
}

module "cognito" {
  source        = "./modules/cognito"
  project_name  = var.project_name
  region        = var.region
}

