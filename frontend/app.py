import streamlit as st
import time
from datetime import datetime
from typing import Optional, List

try:
    from graphql_client import graphql_client, User, Chat, Message
    from config import config
except ImportError as e:
    st.error(f"Erro ao importar módulos: {e}")
    st.stop()


def init_session_state():
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'current_chat' not in st.session_state:
        st.session_state.current_chat = None
    if 'chats' not in st.session_state:
        st.session_state.chats = []
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'user_email' not in st.session_state:
        st.session_state.user_email = ""
    if 'show_welcome' not in st.session_state:
        st.session_state.show_welcome = True


def check_configuration():
    if not config.is_configured():
        st.error("⚠️ Configurações AWS não definidas!")
        st.markdown("""
        **Para usar o chatbot, defina as seguintes variáveis de ambiente:**
        - `URL_API_ID`: ID da API AppSync
        - `REGION`: Região AWS (ex: us-east-1)
        - `API_KEY`: Chave da API AppSync
        """)
        return False
    return True


def create_user_form():
    if st.session_state.show_welcome:
        st.info("� Bem-vindo! Para começar, precisamos do seu email.")
    
    with st.form("user_form"):
        email = st.text_input(
            "Email:",
            value=st.session_state.user_email,
            placeholder="seu@email.com"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            create_user = st.form_submit_button("Criar Usuário", type="primary")
        
        with col2:
            use_email = st.form_submit_button("Usar Email Existente")
        
        if create_user and email:
            try:
                with st.spinner("Criando usuário..."):
                    user = graphql_client.create_user(email)
                st.session_state.user = user
                st.session_state.user_email = email
                st.session_state.show_welcome = False
                st.success(f"✅ Bem-vindo, {user.name}!")
                time.sleep(1)  # Pequena pausa para mostrar a mensagem
                st.rerun()
            except Exception as e:
                st.error(f"❌ Erro ao criar usuário: {e}")
        
        elif use_email and email:
            st.session_state.user_email = email
            st.session_state.user = User(
                id="user_" + email.replace("@", "_").replace(".", "_"),
                name=email.split("@")[0],
                email=email,
                created_at=datetime.now().isoformat()
            )
            st.session_state.show_welcome = False
            st.success(f"✅ Bem-vindo de volta!")
            time.sleep(1)
            st.rerun()


def sidebar_chat_management():
    st.sidebar.header("💬 Histórico de Chats")
    
    if st.sidebar.button("➕ Novo Chat", type="primary"):
        st.session_state.current_chat = None
        st.session_state.messages = []
        st.rerun()
    
    if st.session_state.user:
        load_chats()
        
        if st.session_state.chats:
            st.sidebar.subheader("Conversas Anteriores:")
            
            for chat in st.session_state.chats:
                is_current = (
                    st.session_state.current_chat and 
                    st.session_state.current_chat.id == chat.id
                )
                
                if is_current:
                    st.sidebar.markdown(f"**📍 {chat.title}**")
                else:
                    if st.sidebar.button(f"💬 {chat.title}", key=f"chat_{chat.id}"):
                        st.session_state.current_chat = chat
                        load_messages()
                        st.rerun()
                
                if st.sidebar.button(f"🗑️", key=f"delete_{chat.id}", help="Deletar chat"):
                    try:
                        graphql_client.delete_chat(chat.id)
                        if is_current:
                            st.session_state.current_chat = None
                            st.session_state.messages = []
                        load_chats()
                        st.success("Chat deletado!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao deletar chat: {e}")
        else:
            st.sidebar.info("Histórico vazio. Inicie uma conversa!")


def load_chats():
    if st.session_state.user:
        try:
            chats = graphql_client.list_chats_by_user(st.session_state.user.id)
            st.session_state.chats = sorted(chats, key=lambda x: x.created_at, reverse=True)
        except Exception as e:
            st.error(f"Erro ao carregar chats: {e}")


def load_messages():
    if st.session_state.current_chat:
        try:
            messages = graphql_client.list_messages(st.session_state.current_chat.id)
            st.session_state.messages = sorted(messages, key=lambda x: x.created_at)
        except Exception as e:
            st.error(f"Erro ao carregar mensagens: {e}")


def chat_interface():
    chat_title = ""
    if st.session_state.current_chat:
        chat_title = f" - {st.session_state.current_chat.title}"
    
    st.header(f"🤖 Chatbot{chat_title}")
    
    messages_container = st.container()
    
    with messages_container:
        if st.session_state.current_chat:
            if not st.session_state.messages:
                load_messages()
            
            for message in st.session_state.messages:
                if message.role == "user":
                    with st.chat_message("user"):
                        st.write(message.content)
                        st.caption(f"📅 {format_datetime(message.created_at)}")
                else:
                    with st.chat_message("assistant"):
                        st.write(message.content)
                        st.caption(f"🤖 {format_datetime(message.created_at)}")
        else:
            with st.chat_message("assistant"):
                st.write("👋 Olá! Sou seu assistente virtual. Digite sua primeira mensagem para começarmos uma nova conversa!")
                st.info("💡 **Dica**: Quando você enviar sua primeira mensagem, um novo chat será criado automaticamente.")
    
    with st.form("message_form", clear_on_submit=True):
        user_input = st.text_area(
            "Sua mensagem:",
            placeholder="Digite sua mensagem aqui...",
            height=100
        )
        
        send_button = st.form_submit_button("Enviar 📤", type="primary")
        
        if send_button and user_input.strip():
            try:
                if not st.session_state.current_chat:
                    with st.spinner("Iniciando conversa..."):
                        new_chat = create_auto_chat(user_input.strip())
                        st.session_state.current_chat = new_chat
                        st.session_state.messages = []
                        load_chats()
                
                with st.spinner("Enviando mensagem..."):
                    message = graphql_client.send_message(
                        chat_id=st.session_state.current_chat.id,
                        content=user_input.strip()
                    )
                
                load_messages()
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Erro ao enviar mensagem: {e}")


def create_auto_chat(user_input: str) -> Chat:
    title_words = user_input.split()[:4]
    title = " ".join(title_words)
    if len(user_input) > 30:
        title += "..."
    
    if len(title.strip()) < 3:
        title = f"Chat {datetime.now().strftime('%H:%M')}"
    
    return graphql_client.create_chat(
        title=title,
        user_id=st.session_state.user.id
    )


def format_datetime(date_str: str) -> str:
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime("%d/%m/%Y %H:%M")
    except:
        return date_str


def main():
    st.set_page_config(
        page_title="🤖 Chatbot AWS",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🤖 Chatbot Serverless AWS")
    
    init_session_state()
    
    if not check_configuration():
        return
    
    if not st.session_state.user:
        create_user_form()
        return
    
    st.sidebar.success(f"👤 {st.session_state.user.name}")
    
    if st.sidebar.button("🚪 Sair"):
        for key in ['user', 'current_chat', 'chats', 'messages', 'show_welcome']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
    
    sidebar_chat_management()
    
    chat_interface()


if __name__ == "__main__":
    main()
