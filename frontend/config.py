import os
from dotenv import load_dotenv

load_dotenv()

APPSYNC_URL = os.getenv('APPSYNC_URL')
COGNITO_USER_POOL_ID = os.getenv('COGNITO_USER_POOL_ID')
COGNITO_USER_POOL_CLIENT_ID = os.getenv('COGNITO_USER_POOL_CLIENT_ID')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')

APP_CONFIG = {
    'page_title': "AWS Serverless Chatbot",
    'layout': "wide",
    'initial_sidebar_state': "expanded"
}
