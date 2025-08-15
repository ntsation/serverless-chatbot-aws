resource "aws_cloudwatch_log_group" "appsync" {
  name              = "/aws/appsync/apis/${var.api_id}"
  retention_in_days = 7

  tags = {
    Name = "${var.project_name}-appsync-logs"
  }
}

resource "aws_iam_role" "appsync_logs" {
  name = "${var.project_name}-appsync-logs-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "appsync.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name = "${var.project_name}-appsync-logs-role"
  }
}

resource "aws_iam_role_policy" "appsync_logs" {
  name = "${var.project_name}-appsync-logs-policy"
  role = aws_iam_role.appsync_logs.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "${aws_cloudwatch_log_group.appsync.arn}:*"
      }
    ]
  })
}
