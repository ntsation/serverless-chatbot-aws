resource "aws_lambda_function" "orchestrator" {
  function_name = "${var.project_name}-orchestrator"
  role          = var.lambda_role_arn
  package_type  = "Image"
  image_uri     = "${var.ecr_repository_url}:latest"
  timeout       = 60

  environment {
    variables = {
      APPSYNC_URL     = var.appsync_url
      APPSYNC_API_KEY = var.appsync_api_key
    }
  }

  tags = {
    Name = "${var.project_name}-orchestrator"
  }
}
