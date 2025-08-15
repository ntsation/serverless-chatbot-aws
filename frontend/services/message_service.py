import requests
from ..config import APPSYNC_URL


def get_chat_messages(chat_id, id_token):
    try:
        query = """
        query ListMessages($chatId: ID!) {
            listMessages(chatId: $chatId) {
                items {
                    id
                    role
                    content
                    createdAt
                }
            }
        }
        """
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {id_token}'
        }
        
        payload = {
            'query': query,
            'variables': {'chatId': chat_id}
        }
        
        response = requests.post(APPSYNC_URL, headers=headers, json=payload)
        result = response.json()
        
        if 'data' in result and result['data']['listMessages']:
            return {'success': True, 'messages': result['data']['listMessages']['items']}
        else:
            return {'success': False, 'error': result.get('errors', 'Erro ao obter mensagens')}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def send_message(chat_id, content, id_token):
    try:
        mutation = """
        mutation SendMessage($chatId: ID!, $content: String!) {
            sendMessage(chatId: $chatId, content: $content) {
                id
                role
                content
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
            'variables': {'chatId': chat_id, 'content': content}
        }
         
        response = requests.post(APPSYNC_URL, headers=headers, json=payload)
        
        if response.status_code != 200:
            return {'success': False, 'error': f'HTTP {response.status_code}: {response.text}'}
        
        result = response.json()
        
        if 'data' in result and result['data']['sendMessage']:
            return {'success': True, 'message': result['data']['sendMessage']}
        elif 'errors' in result:
            error_details = []
            for error in result['errors']:
                error_msg = error.get('message', 'Erro desconhecido')
                error_details.append(error_msg)
            return {'success': False, 'error': f"GraphQL Errors: {'; '.join(error_details)}"}
        else:
            return {'success': False, 'error': f'Resposta inesperada: {result}'}
    except Exception as e:
        print(f"Debug - Exception: {str(e)}")
        return {'success': False, 'error': f'Exception: {str(e)}'}
