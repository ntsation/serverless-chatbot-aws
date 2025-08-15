output "users_table_name" {
  value = aws_dynamodb_table.users.name
}

output "chats_table_name" {
  value = aws_dynamodb_table.chats.name
}

output "messages_table_name" {
  value = aws_dynamodb_table.messages.name
}

output "all_table_arns" {
  value = [
    aws_dynamodb_table.users.arn,
    aws_dynamodb_table.chats.arn,
    aws_dynamodb_table.messages.arn,
    "${aws_dynamodb_table.chats.arn}/index/*"
  ]
}
