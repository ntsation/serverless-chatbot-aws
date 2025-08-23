import os
import sys
sys.path.append('/home/ntsation/repo/serverless-chatbot-aws/frontend')

from graphql_client import graphql_client
from config import config

def main():
    print("🚀 Demonstração da API GraphQL do Chatbot")
    print("=" * 50)
    
    if not config.is_configured():
        print("❌ Configurações AWS não definidas!")
        print("Configure as variáveis de ambiente:")
        print("export URL_API_ID='sua-api-id'")
        print("export REGION='us-east-1'")
        print("export API_KEY='sua-api-key'")
        return
    
    print(f"✅ Conectado à API: {config.URL_API_ID}")
    print(f"📍 Região: {config.REGION}")
    print()
    
    try:
        print("1️⃣ Criando usuário...")
        email = "demo@exemplo.com"
        user = graphql_client.create_user(email)
        print(f"✅ Usuário criado:")
        print(f"   ID: {user.id}")
        print(f"   Nome: {user.name}")
        print(f"   Email: {user.email}")
        print()
        
        print("2️⃣ Criando chat...")
        chat_title = "Chat de Demonstração"
        chat = graphql_client.create_chat(chat_title, user.id)
        print(f"✅ Chat criado:")
        print(f"   ID: {chat.id}")
        print(f"   Título: {chat.title}")
        print(f"   Usuário: {chat.user_id}")
        print()
        
        print("3️⃣ Listando chats do usuário...")
        chats = graphql_client.list_chats_by_user(user.id)
        print(f"✅ Encontrados {len(chats)} chats:")
        for i, c in enumerate(chats, 1):
            print(f"   {i}. {c.title} (ID: {c.id})")
        print()
        
        print("4️⃣ Enviando mensagem...")
        message_content = "Olá! Esta é uma mensagem de teste."
        message = graphql_client.send_message(chat.id, message_content)
        print(f"✅ Mensagem enviada:")
        print(f"   ID: {message.id}")
        print(f"   Conteúdo: {message.content}")
        print(f"   Role: {message.role}")
        print()
        
        print("5️⃣ Listando mensagens do chat...")
        messages = graphql_client.list_messages(chat.id)
        print(f"✅ Encontradas {len(messages)} mensagens:")
        for i, msg in enumerate(messages, 1):
            print(f"   {i}. [{msg.role}] {msg.content}")
        print()
        
        print("6️⃣ Deletando chat...")
        deleted = graphql_client.delete_chat(chat.id)
        if deleted:
            print("✅ Chat deletado com sucesso!")
        else:
            print("❌ Erro ao deletar chat")
        
        print()
        print("🎉 Demonstração concluída com sucesso!")
        print("💡 Agora você pode executar o frontend Streamlit:")
        print("   cd frontend && streamlit run app.py")
        
    except Exception as e:
        print(f"❌ Erro na demonstração: {e}")
        print("🔧 Verifique se:")
        print("   - A infraestrutura AWS está deployada")
        print("   - As credenciais estão corretas")
        print("   - O AppSync está funcionando")


if __name__ == "__main__":
    main()
