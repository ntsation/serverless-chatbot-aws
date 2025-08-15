import requests
from ..config import APPSYNC_URL


def create_chat(title, id_token):
    try:
        mutation = """
        mutation CreateChat($title: String!) {
            createChat(title: $title) {
                id
                userId
                title
                createdAt
            }
        }
        """
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {id_token}'
        }
        
        payload = {
            'query': mutation,
            'variables': {'title': title}
        }
        
        response = requests.post(APPSYNC_URL, headers=headers, json=payload)
        result = response.json()
        
        if 'data' in result and result['data'] and result['data']['createChat']:
            return {'success': True, 'chat': result['data']['createChat']}
        else:
            error_msg = result.get('errors', 'Erro ao criar chat')
            print(f"DEBUG: Error creating chat = {error_msg}")
            return {'success': False, 'error': error_msg}
    except Exception as e:
        print(f"DEBUG: Exception creating chat = {str(e)}")
        return {'success': False, 'error': str(e)}


def get_user_chats(user_id, id_token):
    try:
        query = """
        query ListChatsByUser($userId: ID!) {
            listChatsByUser(userId: $userId) {
                id
                title
                createdAt
            }
        }
        """
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {id_token}'
        }
        
        payload = {
            'query': query,
            'variables': {'userId': user_id}
        }
        
        response = requests.post(APPSYNC_URL, headers=headers, json=payload)
        result = response.json()
        
        if 'data' in result:
            return {'success': True, 'chats': result['data']['listChatsByUser']}
        else:
            return {'success': False, 'error': result.get('errors', 'Erro ao obter chats')}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def delete_chat(chat_id, id_token):
    try:
        mutation = """
        mutation DeleteChat($id: ID!) {
            deleteChat(id: $id)
        }
        """
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {id_token}'
        }
        
        payload = {
            'query': mutation,
            'variables': {'id': chat_id}
        }
        
        response = requests.post(APPSYNC_URL, headers=headers, json=payload)
        result = response.json()
        
        if 'data' in result and result['data']['deleteChat']:
            return {'success': True}
        elif 'errors' in result:
            error_details = []
            for error in result['errors']:
                error_msg = error.get('message', 'Erro desconhecido')
                error_details.append(error_msg)
            return {'success': False, 'error': f"GraphQL Errors: {'; '.join(error_details)}"}
        else:
            return {'success': False, 'error': f'Erro ao excluir chat: {result}'}
    except Exception as e:
        return {'success': False, 'error': f'Exception: {str(e)}'}
