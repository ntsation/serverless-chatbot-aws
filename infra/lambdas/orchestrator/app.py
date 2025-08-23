import os, json, boto3, threading
from urllib import request as urlreq
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest

APPSYNC_URL = os.environ["APPSYNC_URL"]
APPSYNC_API_KEY = os.environ.get("APPSYNC_API_KEY", "")
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
BEDROCK_MODEL = os.environ.get("BEDROCK_MODEL", "amazon.nova-micro-v1:0")
BEDROCK_REGION = os.environ.get("BEDROCK_REGION", "us-east-1")

def sign_and_post(url, payload: dict):
    try:
        print(f"Environment APPSYNC_API_KEY: {repr(APPSYNC_API_KEY)}")
        print(f"API Key length: {len(APPSYNC_API_KEY) if APPSYNC_API_KEY else 0}")
        print(f"Using API Key: {bool(APPSYNC_API_KEY)}")
        
        data = json.dumps(payload).encode("utf-8")
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        if APPSYNC_API_KEY:
            headers["x-api-key"] = APPSYNC_API_KEY
            
            request = urlreq.Request(
                url, 
                data=data, 
                method="POST",
                headers=headers
            )
        else:
            session = boto3.Session()
            credentials = session.get_credentials()
            
            if not credentials:
                raise RuntimeError("No AWS credentials available")
            
            aws_request = AWSRequest(
                method="POST", 
                url=url, 
                data=data,
                headers=headers
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
        print(f"Using API Key: {bool(APPSYNC_API_KEY)}")
        raise

def call_bedrock(messages):
    try:
        bedrock_runtime = boto3.client(
            service_name='bedrock-runtime',
            region_name=BEDROCK_REGION
        )
        
        is_claude = "anthropic" in BEDROCK_MODEL.lower()
        is_titan = "amazon.titan" in BEDROCK_MODEL.lower()
        is_nova = "amazon.nova" in BEDROCK_MODEL.lower()
        
        if is_claude:
            conversation = []
            system_message = ""
            
            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    conversation.append({
                        "role": msg["role"],
                        "content": [{"text": msg["content"]}]
                    })
            
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4000,
                "temperature": 0.4,
                "messages": conversation
            }
            
            if system_message:
                request_body["system"] = system_message
                
        elif is_nova:
            conversation = []
            system_message = ""
            
            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    conversation.append({
                        "role": msg["role"],
                        "content": [{"text": msg["content"]}]
                    })
            
            request_body = {
                "messages": conversation,
                "inferenceConfig": {
                    "max_new_tokens": 4000,
                    "temperature": 0.4,
                    "top_p": 0.9
                }
            }
            
            if system_message:
                request_body["system"] = [{"text": system_message}]
                
        elif is_titan:
            prompt_text = ""
            for msg in messages:
                if msg["role"] == "system":
                    prompt_text += f"System: {msg['content']}\n\n"
                elif msg["role"] == "user":
                    prompt_text += f"Human: {msg['content']}\n\n"
                elif msg["role"] == "assistant":
                    prompt_text += f"Assistant: {msg['content']}\n\n"
            
            prompt_text += "Assistant:"
            
            request_body = {
                "inputText": prompt_text,
                "textGenerationConfig": {
                    "maxTokenCount": 4000,
                    "temperature": 0.4,
                    "topP": 0.9,
                    "stopSequences": ["Human:", "System:"]
                }
            }
        else:
            raise ValueError(f"Modelo não suportado: {BEDROCK_MODEL}")
        
        response = bedrock_runtime.invoke_model(
            modelId=BEDROCK_MODEL,
            body=json.dumps(request_body)
        )
        
        response_body = json.loads(response['body'].read())
        
        if is_claude:
            if 'content' in response_body and len(response_body['content']) > 0:
                return response_body['content'][0]['text']
        elif is_nova:
            if 'output' in response_body and 'message' in response_body['output']:
                return response_body['output']['message']['content'][0]['text']
        elif is_titan:
            if 'results' in response_body and len(response_body['results']) > 0:
                return response_body['results'][0]['outputText'].strip()
        
        return "Desculpe, não consegui gerar uma resposta."
            
    except Exception as e:
        print(f"Erro ao chamar Bedrock: {str(e)}")
        return f"Erro ao processar sua solicitação: {str(e)}"

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

def save_assistant_message(chat_id, content):
    mutation = """
      mutation AddAssistant($chatId: ID!, $content: String!) {
        addAssistantMessage(chatId: $chatId, content: $content) {
          id
          chatId
          userId
          role
          content
          createdAt
        }
      }
    """
    
    result = sign_and_post(APPSYNC_URL, {
        "query": mutation,
        "variables": {
            "chatId": chat_id,
            "content": content
        }
    })
    
    return result.get("addAssistantMessage")

def handler(event, _ctx):
    print(f"Event received: {json.dumps(event)}")
    
    if event.get("action") == "trigger_subscription":
        assistant_message = event.get("assistantMessage")
        if assistant_message:
            try:
                print(f"Triggerando subscription para mensagem do assistant: {assistant_message['content'][:100]}...")
                result = add_assistant_message(
                    assistant_message["chatId"],
                    assistant_message["userId"],
                    assistant_message["content"]
                )
                print(f"Subscription triggerada com sucesso: {result}")
                return {"success": True, "triggeredSubscription": True}
            except Exception as e:
                print(f"Erro ao triggerar subscription: {str(e)}")
                return {"success": False, "error": str(e)}
        else:
            return {"success": False, "error": "Nenhuma mensagem do assistant fornecida"}
    
    if event.get("action") == "skip":
        return {"success": True, "skipped": True}
    
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
        
        assistant_reply = call_bedrock(history)
        
        print(f"Resposta gerada: {assistant_reply[:100]}...")
        
        result = save_assistant_message(chat_id, assistant_reply)
        
        print(f"Resposta do assistente salva com sucesso")
        
        return {
            "success": True,
            "message": "Resposta do assistente processada com sucesso",
            "assistantMessage": {
                "chatId": chat_id,
                "userId": user_id,
                "content": assistant_reply
            }
        }
        
    except Exception as e:
        error_msg = f"Erro ao processar mensagem: {str(e)}"
        print(error_msg)
        
        return {
            "success": False,
            "error": error_msg
        }
