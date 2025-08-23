import os
from typing import Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class Config:
    URL_API_ID: str = os.getenv('URL_API_ID', '')
    REGION: str = os.getenv('REGION', 'us-east-1')
    API_KEY: str = os.getenv('API_KEY', '')
    
    @property
    def graphql_url(self) -> str:
        return f"https://{self.URL_API_ID}.appsync-api.{self.REGION}.amazonaws.com/graphql"
    
    @property
    def websocket_url(self) -> str:
        return f"wss://{self.URL_API_ID}.appsync-realtime-api.{self.REGION}.amazonaws.com/graphql"
    
    @property
    def headers(self) -> dict:
        return {
            'Content-Type': 'application/json',
            'x-api-key': self.API_KEY,
        }
    
    def is_configured(self) -> bool:
        return bool(self.URL_API_ID and self.REGION and self.API_KEY)

config = Config()
