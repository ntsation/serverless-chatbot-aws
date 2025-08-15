resource "aws_appsync_graphql_api" "api" {
  authentication_type = "AMAZON_COGNITO_USER_POOLS"
  name                = "${var.project_name}-api"
  schema              = file(var.schema_path)

  user_pool_config {
    aws_region     = var.region
    user_pool_id   = var.cognito_user_pool_id
    default_action = "ALLOW"
  }

  log_config {
    cloudwatch_logs_role_arn = var.cloudwatch_logs_role_arn
    field_log_level          = var.cloudwatch_logs_role_arn != "" ? "ERROR" : "NONE"
  }

  tags = {
    Name = "${var.project_name}-appsync-api"
  }
}

# Data Sources
resource "aws_appsync_datasource" "users_table" {
  api_id           = aws_appsync_graphql_api.api.id
  name             = "UsersTable"
  type             = "AMAZON_DYNAMODB"
  service_role_arn = var.appsync_role_arn

  dynamodb_config {
    table_name = var.users_table
  }
}

resource "aws_appsync_datasource" "chats_table" {
  api_id           = aws_appsync_graphql_api.api.id
  name             = "ChatsTable"
  type             = "AMAZON_DYNAMODB"
  service_role_arn = var.appsync_role_arn

  dynamodb_config {
    table_name = var.chats_table
  }
}

resource "aws_appsync_datasource" "messages_table" {
  api_id           = aws_appsync_graphql_api.api.id
  name             = "MessagesTable"
  type             = "AMAZON_DYNAMODB"
  service_role_arn = var.appsync_role_arn

  dynamodb_config {
    table_name = var.messages_table
  }
}

resource "aws_appsync_datasource" "lambda_orchestrator" {
  api_id           = aws_appsync_graphql_api.api.id
  name             = "LambdaOrchestrator"
  type             = "AWS_LAMBDA"
  service_role_arn = var.appsync_role_arn

  lambda_config {
    function_arn = var.lambda_arn
  }
}

# Resolvers - Basic examples
resource "aws_appsync_resolver" "send_message" {
  api_id      = aws_appsync_graphql_api.api.id
  type        = "Mutation"
  field       = "sendMessage"
  data_source = aws_appsync_datasource.lambda_orchestrator.name

  request_template  = file("${path.module}/resolvers/functions/fn_invoke_lambda.vtl")
  response_template = "$util.toJson($context.result)"
}

resource "aws_appsync_resolver" "create_user" {
  api_id      = aws_appsync_graphql_api.api.id
  type        = "Mutation"
  field       = "createUser"
  data_source = aws_appsync_datasource.users_table.name

  request_template  = file("${path.module}/resolvers/functions/fn_create_user.vtl")
  response_template = "$util.toJson($context.result)"
}

resource "aws_appsync_resolver" "me" {
  api_id      = aws_appsync_graphql_api.api.id
  type        = "Query"
  field       = "me"
  data_source = aws_appsync_datasource.users_table.name

  request_template  = file("${path.module}/resolvers/functions/fn_get_user_by_email.vtl")
  response_template = file("${path.module}/resolvers/functions/fn_get_user_response.vtl")
}
