import asyncio
import websockets
import json
import base64
import uuid
from typing import Dict, Any, Callable, Optional
import threading

from config import config


class WebSocketSubscriptionClient:    
    def __init__(self):
        self.config = config
        self.websocket = None
        self.is_connected = False
        self.message_handlers = {}
        
    def _get_websocket_url(self) -> str:
        headers = {
            'host': f"{self.config.URL_API_ID}.appsync-api.{self.config.REGION}.amazonaws.com",
            'x-api-key': self.config.API_KEY,
        }
        
        header_b64 = base64.b64encode(json.dumps(headers).encode()).decode()
        payload_b64 = base64.b64encode(json.dumps({}).encode()).decode()
        
        return f"{self.config.websocket_url}?header={header_b64}&payload={payload_b64}"
    
    async def connect(self):
        if not self.config.is_configured():
            raise ValueError("Configurações AWS não definidas")
        
        try:
            url = self._get_websocket_url()
            self.websocket = await websockets.connect(url, subprotocols=['graphql-ws'])
            self.is_connected = True
            
            await self.websocket.send(json.dumps({'type': 'connection_init'}))
            
            while True:
                message = await self.websocket.recv()
                data = json.loads(message)
                
                if data.get('type') == 'connection_ack':
                    break
                elif data.get('type') == 'connection_error':
                    raise Exception(f"Erro de conexão: {data}")
            
            return True
            
        except Exception as e:
            self.is_connected = False
            raise Exception(f"Erro ao conectar WebSocket: {e}")
    
    async def subscribe_to_messages(self, chat_id: str, callback: Callable[[Dict[str, Any]], None]):
        if not self.is_connected:
            await self.connect()
        
        subscription_id = str(uuid.uuid4())
        
        subscription = """
        subscription OnMessageSent($chatId: ID!) {
          onMessageSent(chatId: $chatId) {
            id
            chatId
            userId
            role
            content
            createdAt
          }
        }
        """
        
        start_message = {
            'id': subscription_id,
            'type': 'start',
            'payload': {
                'data': json.dumps({
                    'query': subscription,
                    'variables': {'chatId': chat_id}
                }),
                'extensions': {
                    'authorization': {
                        'host': f"{self.config.URL_API_ID}.appsync-api.{self.config.REGION}.amazonaws.com",
                        'x-api-key': self.config.API_KEY,
                    }
                }
            }
        }
        
        await self.websocket.send(json.dumps(start_message))
        self.message_handlers[subscription_id] = callback
        
        return subscription_id
    
    async def listen(self):
        if not self.websocket:
            raise Exception("WebSocket não conectado")
        
        try:
            async for message in self.websocket:
                data = json.loads(message)
                
                if data.get('type') == 'data':
                    subscription_id = data.get('id')
                    payload = data.get('payload', {})
                    
                    if 'data' in payload and 'onMessageSent' in payload['data']:
                        message_data = payload['data']['onMessageSent']
                        
                        if subscription_id in self.message_handlers:
                            self.message_handlers[subscription_id](message_data)
                
                elif data.get('type') == 'error':
                    print(f"Erro na subscription: {data}")
                
                elif data.get('type') == 'complete':
                    subscription_id = data.get('id')
                    if subscription_id in self.message_handlers:
                        del self.message_handlers[subscription_id]
        
        except websockets.exceptions.ConnectionClosed:
            self.is_connected = False
            print("Conexão WebSocket fechada")
        except Exception as e:
            print(f"Erro ao escutar WebSocket: {e}")
    
    async def unsubscribe(self, subscription_id: str):
        if self.websocket and subscription_id:
            stop_message = {
                'id': subscription_id,
                'type': 'stop'
            }
            await self.websocket.send(json.dumps(stop_message))
            
            if subscription_id in self.message_handlers:
                del self.message_handlers[subscription_id]
    
    async def disconnect(self):
        if self.websocket:
            await self.websocket.close()
            self.is_connected = False
            self.message_handlers.clear()


class StreamlitWebSocketManager:
    
    def __init__(self):
        self.client = WebSocketSubscriptionClient()
        self.running = False
        self.thread = None
    
    def start_listening(self, chat_id: str, message_callback: Callable[[Dict[str, Any]], None]):
        if self.running:
            return
        
        def run_websocket():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            async def websocket_handler():
                try:
                    await self.client.connect()
                    await self.client.subscribe_to_messages(chat_id, message_callback)
                    await self.client.listen()
                except Exception as e:
                    print(f"Erro no WebSocket: {e}")
            
            loop.run_until_complete(websocket_handler())
        
        self.running = True
        self.thread = threading.Thread(target=run_websocket, daemon=True)
        self.thread.start()
    
    def stop_listening(self):
        if self.running and self.client.websocket:
            asyncio.run(self.client.disconnect())
            self.running = False


# Exemplo de uso em Streamlit (comentado para referência)
"""
import streamlit as st

# No início da sua aplicação Streamlit
if 'websocket_manager' not in st.session_state:
    st.session_state.websocket_manager = StreamlitWebSocketManager()

# Quando um chat for selecionado
def on_new_message(message_data):
    # Adiciona nova mensagem ao estado da sessão
    new_message = Message(
        id=message_data['id'],
        chat_id=message_data['chatId'],
        user_id=message_data['userId'],
        role=message_data['role'],
        content=message_data['content'],
        created_at=message_data['createdAt']
    )
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    st.session_state.messages.append(new_message)
    st.rerun()

# Iniciar escuta para o chat atual
if st.session_state.current_chat:
    st.session_state.websocket_manager.start_listening(
        st.session_state.current_chat.id,
        on_new_message
    )
"""
