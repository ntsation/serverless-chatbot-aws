import streamlit as st
import time
from ..services import get_chat_messages, send_message, delete_chat, get_user_info, get_user_chats
from ..utils import get_message_style


def render_chat_page():
    if 'current_chat' not in st.session_state or st.session_state.current_chat is None:
        _render_welcome_message()
    else:
        _render_active_chat()


def _render_welcome_message():
    st.markdown("""
    ### 👋 Bem-vindo ao AWS Serverless Chatbot!
    
    Para começar a conversar:
    1. Clique em **"Novo Chat"** na barra lateral
    2. Ou selecione um chat existente
    
    **Recursos disponíveis:**
    - Conversas com IA
    - Histórico salvo automaticamente
    - Autenticação segura
    - Powered by AWS
    """)


def _render_active_chat():
    current_chat = st.session_state.current_chat
    
    _render_chat_header(current_chat)
    
    _render_chat_messages(current_chat)
    
    _render_message_input(current_chat)


def _render_chat_header(current_chat):
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader(f"{current_chat['title']}")
    
    with col2:
        if st.button("Excluir Chat", help="Excluir este chat", type="secondary"):
            if 'confirm_delete' not in st.session_state:
                st.session_state.confirm_delete = False
            
            st.session_state.confirm_delete = True
        
        if st.session_state.get('confirm_delete', False):
            _render_main_delete_confirmation(current_chat)


def _render_main_delete_confirmation(current_chat):
    st.warning("**Tem certeza que deseja excluir este chat?**")
    st.write(f"Chat: **{current_chat['title']}**")
    st.write("Esta ação não pode ser desfeita!")
    
    col_confirm, col_cancel = st.columns(2)
    
    with col_confirm:
        if st.button("Sim, excluir", type="primary"):
            _handle_main_chat_deletion(current_chat)
    
    with col_cancel:
        if st.button("Cancelar"):
            st.session_state.confirm_delete = False
            st.rerun()


def _handle_main_chat_deletion(current_chat):
    with st.spinner("Excluindo chat..."):
        result = delete_chat(current_chat['id'], st.session_state.id_token)
        
        if result['success']:
            st.success("Chat excluído com sucesso!")
            st.session_state.current_chat = None
            st.session_state.confirm_delete = False
            
            user_info = get_user_info(st.session_state.id_token)
            if user_info['success']:
                chats_result = get_user_chats(user_info['user']['id'], st.session_state.id_token)
                if chats_result['success']:
                    st.session_state.user_chats = chats_result['chats']
            
            time.sleep(1)
            st.rerun()
        else:
            st.error(f"Erro ao excluir chat: {result['error']}")
            st.session_state.confirm_delete = False
            time.sleep(2)
            st.rerun()


def _render_chat_messages(current_chat):
    chat_container = st.container()
    
    with chat_container:
        with st.spinner("Carregando mensagens..."):
            messages_result = get_chat_messages(current_chat['id'], st.session_state.id_token)
        
        if messages_result['success']:
            messages = messages_result['messages']
            
            if messages:
                for message in messages:
                    role = message['role']
                    content = message['content']
                    timestamp = message.get('createdAt', '')
                    
                    message_html = get_message_style(role, content, timestamp)
                    st.markdown(message_html, unsafe_allow_html=True)
            else:
                st.info("Este é um novo chat! Envie sua primeira mensagem abaixo.")
        else:
            st.error("Erro ao carregar mensagens")


def _render_message_input(current_chat):
    st.markdown("---")
    
    with st.form("message_form", clear_on_submit=True):
        col1, col2 = st.columns([4, 1])
        
        with col1:
            user_message = st.text_area(
                "Digite sua mensagem:", 
                height=100, 
                placeholder="Digite sua pergunta aqui...",
                label_visibility="collapsed"
            )
        
        with col2:
            st.write("")
            st.write("")
            submitted = st.form_submit_button("Enviar", type="primary", use_container_width=True)
        
        if submitted and user_message.strip():
            _handle_send_message(current_chat, user_message.strip())
        elif submitted:
            st.warning("Por favor, digite uma mensagem antes de enviar.")


def _handle_send_message(current_chat, user_message):
    with st.spinner("Enviando mensagem e aguardando resposta..."):
        send_result = send_message(current_chat['id'], user_message, st.session_state.id_token)
        
        if send_result['success']:
            st.success("Mensagem enviada com sucesso!")
            time.sleep(3)
            st.rerun()
        else:
            st.error(f"Erro ao enviar mensagem: {send_result['error']}")
