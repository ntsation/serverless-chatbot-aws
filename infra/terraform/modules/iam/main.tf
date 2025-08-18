data "aws_iam_policy_document" "appsync_role_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["appsync.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "appsync_role" {
  name               = "${var.project_name}-appsync-role"
  assume_role_policy = data.aws_iam_policy_document.appsync_role_assume.json

  tags = {
    Name = "${var.project_name}-appsync-role"
  }
}

resource "aws_iam_policy" "appsync_policy" {
  name = "${var.project_name}-appsync-policy"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect : "Allow",
        Action : [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:Query",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem"
        ],
        Resource : [
          var.users_table_arn,
          var.chats_table_arn,
          var.messages_table_arn,
          "${var.chats_table_arn}/index/*"
        ]
      },
      {
        Effect : "Allow",
        Action : ["lambda:InvokeFunction"],
        Resource : var.lambda_arn
      }
    ]
  })

  tags = {
    Name = "${var.project_name}-appsync-policy"
  }
}

resource "aws_iam_role_policy_attachment" "appsync_attach" {
  role       = aws_iam_role.appsync_role.name
  policy_arn = aws_iam_policy.appsync_policy.arn
}

data "aws_iam_policy_document" "lambda_role_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "lambda_role" {
  name               = "${var.project_name}-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_role_assume.json

  tags = {
    Name = "${var.project_name}-lambda-role"
  }
}

resource "aws_iam_policy" "lambda_policy" {
  name = "${var.project_name}-lambda-policy"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Resource = "*"
      },
      {
        Effect = "Allow",
        Action = ["appsync:GraphQL"],
        Resource = [
          var.appsync_api_arn,
          "${var.appsync_api_arn}/*"
        ]
      }
    ]
  })

  tags = {
    Name = "${var.project_name}-lambda-policy"
  }
}

resource "aws_iam_role_policy_attachment" "lambda_attach" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}
