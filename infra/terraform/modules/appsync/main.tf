resource "aws_appsync_graphql_api" "api" {
  authentication_type = "API_KEY"
  name                = "${var.project_name}-api"
  schema              = file(var.schema_path)

  additional_authentication_provider {
    authentication_type = "AMAZON_COGNITO_USER_POOLS"
    user_pool_config {
      aws_region   = var.region
      user_pool_id = var.cognito_user_pool_id
    }
  }

  log_config {
    cloudwatch_logs_role_arn = var.cloudwatch_logs_role_arn
    field_log_level          = var.cloudwatch_logs_role_arn != "" ? "ERROR" : "NONE"
  }

  tags = {
    Name = "${var.project_name}-appsync-api"
  }
}

resource "aws_appsync_api_key" "api_key" {
  api_id      = aws_appsync_graphql_api.api.id
  description = "API Key for ${var.project_name} AppSync API"
  expires     = "2025-12-31T23:59:59Z"
}

resource "aws_appsync_datasource" "none" {
  api_id = aws_appsync_graphql_api.api.id
  name   = "None"
  type   = "NONE"
}

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

resource "aws_appsync_function" "put_user_message" {
  api_id      = aws_appsync_graphql_api.api.id
  data_source = aws_appsync_datasource.messages_table.name
  name        = "PutUserMessage"
  runtime {
    name            = "APPSYNC_JS"
    runtime_version = "1.0.0"
  }
  code = file("${path.module}/functions/fn_put_user_message.js")
}

resource "aws_appsync_function" "invoke_orchestrator" {
  api_id      = aws_appsync_graphql_api.api.id
  data_source = aws_appsync_datasource.lambda_orchestrator.name
  name        = "InvokeOrchestrator"
  runtime {
    name            = "APPSYNC_JS"
    runtime_version = "1.0.0"
  }
  code = file("${path.module}/functions/fn_invoke_lambda.js")
}

resource "aws_appsync_resolver" "send_message" {
  api_id = aws_appsync_graphql_api.api.id
  type   = "Mutation"
  field  = "sendMessage"
  kind   = "PIPELINE"

  pipeline_config {
    functions = [
      aws_appsync_function.put_user_message.function_id,
      aws_appsync_function.invoke_orchestrator.function_id
    ]
  }

  runtime {
    name            = "APPSYNC_JS"
    runtime_version = "1.0.0"
  }

  code = file("${path.module}/functions/fn_send_message_pipeline.js")
}

resource "aws_appsync_resolver" "create_user" {
  api_id      = aws_appsync_graphql_api.api.id
  type        = "Mutation"
  field       = "createUser"
  data_source = aws_appsync_datasource.users_table.name

  runtime {
    name            = "APPSYNC_JS"
    runtime_version = "1.0.0"
  }
  code = file("${path.module}/functions/fn_create_user.js")
}

resource "aws_appsync_resolver" "me" {
  api_id      = aws_appsync_graphql_api.api.id
  type        = "Query"
  field       = "me"
  data_source = aws_appsync_datasource.users_table.name

  runtime {
    name            = "APPSYNC_JS"
    runtime_version = "1.0.0"
  }
  code = file("${path.module}/functions/fn_get_user_by_email.js")
}

resource "aws_appsync_resolver" "create_chat" {
  api_id      = aws_appsync_graphql_api.api.id
  type        = "Mutation"
  field       = "createChat"
  data_source = aws_appsync_datasource.chats_table.name

  runtime {
    name            = "APPSYNC_JS"
    runtime_version = "1.0.0"
  }
  code = file("${path.module}/functions/fn_create_chat.js")
}

resource "aws_appsync_resolver" "list_chats_by_user" {
  api_id      = aws_appsync_graphql_api.api.id
  type        = "Query"
  field       = "listChatsByUser"
  data_source = aws_appsync_datasource.chats_table.name

  runtime {
    name            = "APPSYNC_JS"
    runtime_version = "1.0.0"
  }
  code = file("${path.module}/functions/fn_list_chats.js")
}

resource "aws_appsync_resolver" "list_messages" {
  api_id      = aws_appsync_graphql_api.api.id
  type        = "Query"
  field       = "listMessages"
  data_source = aws_appsync_datasource.messages_table.name

  runtime {
    name            = "APPSYNC_JS"
    runtime_version = "1.0.0"
  }
  code = file("${path.module}/functions/fn_list_messages.js")
}

resource "aws_appsync_resolver" "add_assistant_message" {
  api_id      = aws_appsync_graphql_api.api.id
  type        = "Mutation"
  field       = "addAssistantMessage"
  data_source = aws_appsync_datasource.messages_table.name

  runtime {
    name            = "APPSYNC_JS"
    runtime_version = "1.0.0"
  }
  code = file("${path.module}/functions/fn_add_assistant_message.js")
}

resource "aws_appsync_resolver" "delete_chat" {
  api_id      = aws_appsync_graphql_api.api.id
  type        = "Mutation"
  field       = "deleteChat"
  data_source = aws_appsync_datasource.lambda_orchestrator.name

  runtime {
    name            = "APPSYNC_JS"
    runtime_version = "1.0.0"
  }
  code = file("${path.module}/functions/fn_delete_chat.js")
}

# Subscription resolvers for real-time functionality
resource "aws_appsync_resolver" "on_message_sent" {
  api_id      = aws_appsync_graphql_api.api.id
  type        = "Subscription"
  field       = "onMessageSent"
  data_source = aws_appsync_datasource.none.name

  runtime {
    name            = "APPSYNC_JS"
    runtime_version = "1.0.0"
  }
  code = file("${path.module}/functions/fn_subscription.js")
}
