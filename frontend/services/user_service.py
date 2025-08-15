import requests
from ..config import APPSYNC_URL

def create_user_in_dynamodb(email, name, id_token):
    try:
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
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {id_token}'
        }
        
        payload = {
            'query': mutation,
            'variables': {'email': email}
        }
        
        response = requests.post(APPSYNC_URL, headers=headers, json=payload)
        result = response.json()
        
        if 'data' in result and result['data']['createUser']:
            return {'success': True, 'user': result['data']['createUser']}
        else:
            return {'success': False, 'error': result.get('errors', 'Erro desconhecido')}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def get_user_info(id_token):
    try:
        query = """
        query {
            me {
                id
                name
                email
                createdAt
            }
        }
        """
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {id_token}'
        }
        
        payload = {'query': query}
        response = requests.post(APPSYNC_URL, headers=headers, json=payload)
        result = response.json()
        
        if 'data' in result and result['data']['me']:
            return {'success': True, 'user': result['data']['me']}
        else:
            return {'success': False, 'error': result.get('errors', 'Erro ao obter informações do usuário')}
    except Exception as e:
        return {'success': False, 'error': str(e)}
