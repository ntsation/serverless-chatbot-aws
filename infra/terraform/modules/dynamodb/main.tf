resource "aws_dynamodb_table" "users" {
  name         = "${var.project_name}-users"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id"

  attribute {
    name = "id"
    type = "S"
  }

  tags = {
    Name        = "${var.project_name}-users"
  }
}

resource "aws_dynamodb_table" "chats" {
  name         = "${var.project_name}-chats"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id"

  attribute {
    name = "id"
    type = "S"
  }
  attribute {
    name = "userId"
    type = "S"
  }
  attribute {
    name = "createdAt"
    type = "S"
  }

  global_secondary_index {
    name               = "GSI1"
    hash_key           = "userId"
    range_key          = "createdAt"
    projection_type    = "ALL"
  }

  tags = {
    Name        = "${var.project_name}-chats"
  }
}

resource "aws_dynamodb_table" "messages" {
  name         = "${var.project_name}-messages"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "chatId"
  range_key    = "sk"

  attribute {
    name = "chatId"
    type = "S"
  }
  attribute {
    name = "sk"
    type = "S"
  }

  tags = {
    Name        = "${var.project_name}-messages"
  }
}