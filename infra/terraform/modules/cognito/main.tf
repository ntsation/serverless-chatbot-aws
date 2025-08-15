resource "aws_cognito_user_pool" "pool" {
  name = "${var.project_name}-user-pool"
  auto_verified_attributes = ["email"]
  username_attributes      = ["email"]
  password_policy {
    minimum_length    = 8
    require_lowercase = true
    require_uppercase = true
    require_numbers   = true
    require_symbols   = false
  }
}

resource "aws_cognito_user_pool_client" "client" {
  name                         = "${var.project_name}-client"
  user_pool_id                 = aws_cognito_user_pool.pool.id
  generate_secret              = false
  explicit_auth_flows          = ["ALLOW_USER_PASSWORD_AUTH","ALLOW_USER_SRP_AUTH","ALLOW_REFRESH_TOKEN_AUTH"]
  supported_identity_providers = ["COGNITO"]
  prevent_user_existence_errors = "ENABLED"
}