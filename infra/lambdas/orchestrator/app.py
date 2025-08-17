import os, json, boto3
from urllib import request as urlreq
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest

APPSYNC_URL = os.environ["APPSYNC_URL"]
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

def sign_and_post(url, payload: dict):

    try:
        session = boto3.Session()
        credentials = session.get_credentials()
        
        if not credentials:
            raise RuntimeError("No AWS credentials available")
        
        data = json.dumps(payload).encode("utf-8")
        
        aws_request = AWSRequest(
            method="POST", 
            url=url, 
            data=data,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
        )
        
        SigV4Auth(credentials, "appsync", AWS_REGION).add_auth(aws_request)
        
        request = urlreq.Request(
            url, 
            data=data, 
            method="POST"
        )
        
        for header_name, header_value in aws_request.headers.items():
            request.add_header(header_name, header_value)
        
        with urlreq.urlopen(request, timeout=30) as response:
            response_data = response.read().decode('utf-8')
            result = json.loads(response_data)
        
        if "errors" in result:
            print(f"GraphQL errors: {result['errors']}")
            raise RuntimeError(f"GraphQL errors: {result['errors']}")
        
        return result.get("data", result)
        
    except Exception as e:
        print(f"Error in sign_and_post: {str(e)}")
        print(f"URL: {url}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        raise

def call_openai(messages):
    if not OPENAI_API_KEY:
        return "Mensagem de teste: a função OpenAI está funcionando corretamente!"
    
    cleaned_messages = []
    for msg in messages:
        cleaned_msg = {"role": msg["role"], "content": msg["content"]}
        cleaned_messages.append(cleaned_msg)
    
    api = "https://api.openai.com/v1/chat/completions"
    body = json.dumps({
        "model": OPENAI_MODEL,
        "messages": cleaned_messages,
        "temperature": 0.4,
    }).encode("utf-8")
    req = urlreq.Request(api, data=body, method="POST",
                         headers={"Content-Type": "application/json",
                                  "Authorization": f"Bearer {OPENAI_API_KEY}"})
    with urlreq.urlopen(req, timeout=60) as resp:
        r = json.loads(resp.read())
    return r["choices"][0]["message"]["content"]

def get_chat_history(chat_id):
    query = """
      query GetMessages($chatId: ID!, $limit: Int) {
        listMessages(chatId: $chatId, limit: $limit) {
          items {
            role
            content
            createdAt
          }
        }
      }
    """
    
    result = sign_and_post(APPSYNC_URL, {
        "query": query,
        "variables": {
            "chatId": chat_id,
            "limit": 50
        }
    })
    
    messages = result.get("listMessages", {}).get("items", [])
    
    history = []
    for msg in messages:
        history.append({
            "role": msg["role"],
            "content": msg["content"]
        })
    
    return history

def save_assistant_message(chat_id, content, user_id):
    mutation = """
      mutation AddAssistant($chatId: ID!, $content: String!, $userId: ID!) {
        addAssistantMessage(chatId: $chatId, content: $content, userId: $userId) {
          id
          chatId
          role
          content
          createdAt
        }
      }
    """
    
    return sign_and_post(APPSYNC_URL, {
        "query": mutation,
        "variables": {
            "chatId": chat_id,
            "content": content,
            "userId": user_id
        }
    })

def handler(event, _ctx):
    print(f"Event received: {json.dumps(event)}")
    
    try:
        args = event.get("arguments", {})
        identity = event.get("identity", {})
        
        chat_id = args.get("chatId")
        user_input = args.get("content")
        user_id = identity.get("sub")
        
        if not chat_id:
            raise ValueError("chatId é obrigatório")
        if not user_input:
            raise ValueError("content é obrigatório")
        if not user_id:
            raise ValueError("User ID é obrigatório para autenticação")
        
        print(f"Processando mensagem para chat {chat_id} do usuário {user_id}")
        
        history = get_chat_history(chat_id)
        history.append({"role": "user", "content": user_input})
        
        print(f"Histórico construído com {len(history)} mensagens")
        
        assistant_reply = call_openai(history)
        
        print(f"Resposta gerada: {assistant_reply[:100]}...")
        
        result = save_assistant_message(chat_id, assistant_reply, user_id)
        
        print(f"Resposta do assistente salva com sucesso")
        
        return {
            "success": True,
            "message": "Resposta do assistente processada com sucesso",
            "assistantMessage": result.get("addAssistantMessage")
        }
        
    except Exception as e:
        error_msg = f"Erro ao processar mensagem: {str(e)}"
        print(error_msg)
        
        return {
            "success": False,
            "error": error_msg
        }
