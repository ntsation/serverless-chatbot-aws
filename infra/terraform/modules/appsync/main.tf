resource "aws_appsync_graphql_api" "api" {
  authentication_type = "AMAZON_COGNITO_USER_POOLS"
  name                = "${var.project_name}-api"
  schema              = file(var.schema_path)

  user_pool_config {
    aws_region     = var.region
    user_pool_id   = var.cognito_user_pool_id
    default_action = "ALLOW"
  }

  additional_authentication_provider {
    authentication_type = "AWS_IAM"
  }

  log_config {
    cloudwatch_logs_role_arn = var.cloudwatch_logs_role_arn
    field_log_level          = var.cloudwatch_logs_role_arn != "" ? "ALL" : "NONE"
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

resource "aws_appsync_function" "put_user_message" {
  api_id      = aws_appsync_graphql_api.api.id
  data_source = aws_appsync_datasource.messages_table.name
  name        = "PutUserMessage"

  request_mapping_template  = file("${path.module}/resolvers/functions/fn_put_user_message.vtl")
  response_mapping_template = <<EOF
$util.qr($context.stash.put("userMessage", $context.result))
$util.toJson($context.result)
EOF
}

resource "aws_appsync_function" "invoke_lambda" {
  api_id      = aws_appsync_graphql_api.api.id
  data_source = aws_appsync_datasource.lambda_orchestrator.name
  name        = "InvokeLambda"

  request_mapping_template  = file("${path.module}/resolvers/functions/fn_invoke_lambda.vtl")
  response_mapping_template = "$util.toJson($context.result)"
}

resource "aws_appsync_resolver" "send_message" {
  api_id = aws_appsync_graphql_api.api.id
  type   = "Mutation"
  field  = "sendMessage"

  kind = "PIPELINE"

  pipeline_config {
    functions = [
      aws_appsync_function.put_user_message.function_id,
      aws_appsync_function.invoke_lambda.function_id
    ]
  }

  request_template = <<EOF
{
  "version": "2018-05-29",
  "operation": "PipelineRequest"
}
EOF

  response_template = <<EOF
#if($ctx.stash.userMessage)
  $util.toJson($ctx.stash.userMessage)
#else
  $util.toJson($ctx.result)
#end
EOF
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

resource "aws_appsync_resolver" "list_chats_by_user" {
  api_id      = aws_appsync_graphql_api.api.id
  type        = "Query"
  field       = "listChatsByUser"
  data_source = aws_appsync_datasource.chats_table.name

  request_template  = file("${path.module}/resolvers/functions/fn_list_chats_by_user.vtl")
  response_template = "$util.toJson($context.result.items)"
}

resource "aws_appsync_resolver" "create_chat" {
  api_id      = aws_appsync_graphql_api.api.id
  type        = "Mutation"
  field       = "createChat"
  data_source = aws_appsync_datasource.chats_table.name

  request_template  = file("${path.module}/resolvers/functions/fn_create_chat.vtl")
  response_template = "$util.toJson($context.result)"
}

resource "aws_appsync_resolver" "list_messages" {
  api_id      = aws_appsync_graphql_api.api.id
  type        = "Query"
  field       = "listMessages"
  data_source = aws_appsync_datasource.messages_table.name

  request_template  = file("${path.module}/resolvers/functions/fn_list_messages.vtl")
  response_template = "$util.toJson($context.result)"
}

resource "aws_appsync_resolver" "add_assistant_message" {
  api_id      = aws_appsync_graphql_api.api.id
  type        = "Mutation"
  field       = "addAssistantMessage"
  data_source = aws_appsync_datasource.messages_table.name

  request_template  = file("${path.module}/resolvers/functions/fn_put_assistant_message.vtl")
  response_template = "$util.toJson($context.result)"
}

resource "aws_appsync_resolver" "delete_chat" {
  api_id      = aws_appsync_graphql_api.api.id
  type        = "Mutation"
  field       = "deleteChat"
  data_source = aws_appsync_datasource.lambda_orchestrator.name

  request_template  = file("${path.module}/resolvers/functions/fn_delete_chat_lambda.vtl")
  response_template = <<EOF
#if($context.error)
  $util.error($context.error.message)
#else
  #if($context.result.success)
    true
  #else
    $util.error("Failed to delete chat")
  #end
#end
EOF
}
