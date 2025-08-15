import boto3
from ..config import COGNITO_USER_POOL_ID, COGNITO_USER_POOL_CLIENT_ID, AWS_REGION


def init_aws_clients():
    return boto3.client('cognito-idp', region_name=AWS_REGION)


def authenticate_user(email, password):
    try:
        cognito_client = init_aws_clients()
        
        response = cognito_client.initiate_auth(
            ClientId=COGNITO_USER_POOL_CLIENT_ID,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': email,
                'PASSWORD': password
            }
        )
        
        return {
            'success': True,
            'id_token': response['AuthenticationResult']['IdToken'],
            'access_token': response['AuthenticationResult']['AccessToken'],
            'refresh_token': response['AuthenticationResult']['RefreshToken']
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}


def create_cognito_user(email, password, name):
    try:
        cognito_client = init_aws_clients()
        
        cognito_client.admin_create_user(
            UserPoolId=COGNITO_USER_POOL_ID,
            Username=email,
            UserAttributes=[
                {'Name': 'email', 'Value': email},
                {'Name': 'email_verified', 'Value': 'true'},
                {'Name': 'name', 'Value': name}
            ],
            TemporaryPassword=password,
            MessageAction='SUPPRESS'
        )
        
        cognito_client.admin_set_user_password(
            UserPoolId=COGNITO_USER_POOL_ID,
            Username=email,
            Password=password,
            Permanent=True
        )
        
        return {'success': True}
    except Exception as e:
        return {'success': False, 'error': str(e)}
