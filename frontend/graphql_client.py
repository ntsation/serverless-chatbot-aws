import json
import asyncio
import websockets
import requests
import base64
import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

from config import config


@dataclass
class User:
    id: str
    name: str
    email: str
    created_at: str


@dataclass
class Chat:
    id: str
    user_id: str
    title: str
    created_at: str


@dataclass
class Message:
    id: str
    chat_id: str
    user_id: str
    role: str
    content: str
    created_at: str


class GraphQLClient:
    
    def __init__(self):
        self.config = config
    
    def _make_request(self, query: str, variables: Dict[str, Any] = None) -> Dict[str, Any]:
        if not self.config.is_configured():
            raise ValueError("Configurações AWS não definidas. Verifique as variáveis de ambiente.")
        
        payload = {
            'query': query,
            'variables': variables or {}
        }
        
        response = requests.post(
            self.config.graphql_url,
            headers=self.config.headers,
            json=payload
        )
        
        if response.status_code != 200:
            raise Exception(f"Erro na requisição: {response.status_code} - {response.text}")
        
        result = response.json()
        
        if 'errors' in result:
            raise Exception(f"Erro GraphQL: {result['errors']}")
        
        return result.get('data', {})
    
    def create_user(self, email: str) -> User:
        mutation = """
        mutation CreateUser($email: String!) {
          createUser(email: $email) {
            id
            name
            email
            createdAt
          }
        }
        """
        
        variables = {'email': email}
        data = self._make_request(mutation, variables)
        
        user_data = data['createUser']
        return User(
            id=user_data['id'],
            name=user_data['name'],
            email=user_data['email'],
            created_at=user_data['createdAt']
        )
    
    def create_chat(self, title: str, user_id: str) -> Chat:
        mutation = """
        mutation CreateChat($title: String!, $userId: ID!) {
          createChat(title: $title, userId: $userId) {
            id
            userId
            title
            createdAt
          }
        }
        """
        
        variables = {'title': title, 'userId': user_id}
        data = self._make_request(mutation, variables)
        
        chat_data = data['createChat']
        return Chat(
            id=chat_data['id'],
            user_id=chat_data['userId'],
            title=chat_data['title'],
            created_at=chat_data['createdAt']
        )
    
    def list_chats_by_user(self, user_id: str, limit: int = 20) -> List[Chat]:
        query = """
        query ListChatsByUser($userId: ID!, $limit: Int) {
          listChatsByUser(userId: $userId, limit: $limit) {
            id
            userId
            title
            createdAt
          }
        }
        """
        
        variables = {'userId': user_id, 'limit': limit}
        data = self._make_request(query, variables)
        
        chats_data = data['listChatsByUser']
        return [
            Chat(
                id=chat['id'],
                user_id=chat['userId'],
                title=chat['title'],
                created_at=chat['createdAt']
            )
            for chat in chats_data
        ]
    
    def list_messages(self, chat_id: str, limit: int = 50) -> List[Message]:
        query = """
        query ListMessages($chatId: ID!, $limit: Int) {
          listMessages(chatId: $chatId, limit: $limit) {
            items {
              id
              chatId
              userId
              role
              content
              createdAt
            }
          }
        }
        """
        
        variables = {'chatId': chat_id, 'limit': limit}
        data = self._make_request(query, variables)
        
        messages_data = data['listMessages']['items']
        return [
            Message(
                id=msg['id'],
                chat_id=msg['chatId'],
                user_id=msg['userId'],
                role=msg['role'],
                content=msg['content'],
                created_at=msg['createdAt']
            )
            for msg in messages_data
        ]
    
    def send_message(self, chat_id: str, content: str) -> Message:
        mutation = """
        mutation SendMessage($chatId: ID!, $content: String!) {
          sendMessage(chatId: $chatId, content: $content) {
            id
            chatId
            userId
            role
            content
            createdAt
          }
        }
        """
        
        variables = {'chatId': chat_id, 'content': content}
        data = self._make_request(mutation, variables)
        
        msg_data = data['sendMessage']
        return Message(
            id=msg_data['id'],
            chat_id=msg_data['chatId'],
            user_id=msg_data['userId'],
            role=msg_data['role'],
            content=msg_data['content'],
            created_at=msg_data['createdAt']
        )
    
    def delete_chat(self, chat_id: str) -> bool:
        mutation = """
        mutation DeleteChat($id: ID!) {
          deleteChat(id: $id)
        }
        """
        
        variables = {'id': chat_id}
        data = self._make_request(mutation, variables)
        
        return data['deleteChat']


graphql_client = GraphQLClient()
