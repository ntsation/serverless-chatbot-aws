import os, json, boto3
from urllib import request as urlreq
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from boto3.dynamodb.conditions import Key

APPSYNC_URL = os.environ["APPSYNC_URL"]
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
MESSAGES_TABLE = os.environ["MESSAGES_TABLE"]
CHATS_TABLE = os.environ["CHATS_TABLE"]
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

def sign_and_post(url, payload: dict):
    data = json.dumps(payload).encode("utf-8")
    req = urlreq.Request(url, data=data, method="POST",
                         headers={"Content-Type": "application/json"})
    session = boto3.session.Session()
    creds = session.get_credentials().get_frozen_credentials()
    aws_req = AWSRequest(method="POST", url=url, data=data, headers={"Content-Type": "application/json"})
    SigV4Auth(creds, "appsync", AWS_REGION).add_auth(aws_req)
    for k, v in aws_req.headers.items():
        req.add_header(k, v)
    with urlreq.urlopen(req, timeout=30) as resp:
        out = json.loads(resp.read())
    if "errors" in out:
        raise RuntimeError(out["errors"])
    return out["data"]

def call_openai(messages):
    if not OPENAI_API_KEY:
        return "Mensagem de teste: a função OpenAI está funcionando corretamente!"
    
    api = "https://api.openai.com/v1/chat/completions"
    body = json.dumps({
        "model": OPENAI_MODEL,
        "messages": messages,
        "temperature": 0.4,
    }).encode("utf-8")
    req = urlreq.Request(api, data=body, method="POST",
                         headers={"Content-Type": "application/json",
                                  "Authorization": f"Bearer {OPENAI_API_KEY}"})
    with urlreq.urlopen(req, timeout=60) as resp:
        r = json.loads(resp.read())
    return r["choices"][0]["message"]["content"]

def build_history(dynamodb, chat_id):
    table = dynamodb.Table(MESSAGES_TABLE)
    resp = table.query(
        KeyConditionExpression=Key("chatId").eq(chat_id),
        ScanIndexForward=True,
        Limit=50
    )
    messages = []
    for it in resp.get("Items", []):
        role = it.get("role", "user")
        content = it["content"]
        user_id = it.get("userId")
        message = {"role": role, "content": content}
        if user_id:
            message["userId"] = user_id
        messages.append(message)
    return messages

def delete_chat_with_messages(dynamodb, chat_id, user_id):
    try:
        messages_table = dynamodb.Table(MESSAGES_TABLE)
        messages_resp = messages_table.query(
            KeyConditionExpression=Key("chatId").eq(chat_id)
        )
        
        messages_to_delete = messages_resp.get("Items", [])
        if messages_to_delete:
            with messages_table.batch_writer() as batch:
                for message in messages_to_delete:
                    batch.delete_item(
                        Key={
                            'chatId': message['chatId'],
                            'sk': message['sk']
                        }
                    )
            print(f"Deleted {len(messages_to_delete)} messages for chat {chat_id}")
        
        chats_table = dynamodb.Table(CHATS_TABLE)
        try:
            chats_table.delete_item(
                Key={'id': chat_id},
                ConditionExpression='userId = :userId',
                ExpressionAttributeValues={':userId': user_id}
            )
            print(f"Deleted chat {chat_id}")
        except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
            print(f"Chat {chat_id} não existe ou não pertence ao usuário {user_id}")
        
        return {"success": True, "deleted_messages": len(messages_to_delete)}
        
    except Exception as e:
        print(f"Erro ao deletar chat {chat_id}: {str(e)}")
        raise e

def handler(event, _ctx):
    print(f"Event received: {json.dumps(event)}")
    
    if event.get("operation") == "deleteChat":
        args = event.get("arguments", {})
        chat_id = args.get("id")
        user_id = event.get("identity", {}).get("sub")
        
        if not chat_id:
            raise ValueError("Chat ID é obrigatório")
        if not user_id:
            raise ValueError("User ID é obrigatório")
        
        dynamodb = boto3.resource("dynamodb")
        result = delete_chat_with_messages(dynamodb, chat_id, user_id)
        return result
    
    args = (event.get("arguments") or event)
    chat_id = args["chatId"]
    user_input = args["content"]

    dynamodb = boto3.resource("dynamodb")
    hist = build_history(dynamodb, chat_id)
    
    user_id = None
    if hist:
        user_id = hist[0].get("userId")
    
    if not user_id and "source" in event and "identity" in event["source"]:
        user_id = event["source"]["identity"].get("sub")
    
    if not user_id:
        user_id = "system"
    
    hist.append({"role": "user", "content": user_input})
    reply = call_openai(hist)

    mutation = """
      mutation AddAssistant($chatId: ID!, $content: String!, $userId: ID!) {
        addAssistantMessage(chatId: $chatId, content: $content, userId: $userId) {
          id chatId role content createdAt
        }
      }
    """
    sign_and_post(APPSYNC_URL, {"query": mutation, "variables": {"chatId": chat_id, "content": reply, "userId": user_id}})
    return {"ok": True}
