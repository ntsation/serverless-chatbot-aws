import streamlit as st
import time
from datetime import datetime
from ..services import create_chat, get_user_chats, delete_chat
from ..utils import clear_session_state, generate_chat_title


def render_sidebar():
    with st.sidebar:
        _render_user_info()
        
        if st.button("Sair", type="secondary", use_container_width=True):
            clear_session_state()
            st.rerun()
        
        st.divider()
        
        _render_chat_management()


def _render_user_info():
    st.subheader("Usuário")
    user_info = st.session_state.user
    st.write(f"**Nome:** {user_info.get('name', 'N/A')}")
    st.write(f"**Email:** {user_info.get('email', 'N/A')}")


def _render_chat_management():
    st.subheader("Seus Chats")
    
    if st.button("Novo Chat", type="primary", use_container_width=True):
        _handle_new_chat()
    
    st.write("---")
    
    _render_chat_list()


def _handle_new_chat():
    chat_title = generate_chat_title()
    with st.spinner("Criando chat..."):
        chat_result = create_chat(chat_title, st.session_state.id_token)
    
    if chat_result['success']:
        st.session_state.current_chat = chat_result['chat']
        st.success("Novo chat criado!")
        time.sleep(0.5)
        st.rerun()
    else:
        st.error("Erro ao criar chat")


def _render_chat_list():
    with st.spinner("Carregando chats..."):
        chats_result = get_user_chats(st.session_state.user['id'], st.session_state.id_token)
    
    if chats_result['success']:
        chats = chats_result['chats']
        if chats:
            for chat in chats:
                _render_chat_item(chat)
        else:
            st.info("Nenhum chat encontrado. Crie seu primeiro chat!")
    else:
        st.error("Erro ao carregar chats")


def _render_chat_item(chat):
    is_current = ('current_chat' in st.session_state and 
                 st.session_state.current_chat['id'] == chat['id'])
    
    chat_container = st.container()
    with chat_container:
        col1, col2 = st.columns([4, 1])
        
        with col1:
            button_type = "primary" if is_current else "secondary"
            if st.button(
                f"{'-' if is_current else '-'} {chat['title']}", 
                key=f"chat_{chat['id']}", 
                type=button_type,
                use_container_width=True
            ):
                st.session_state.current_chat = chat
                st.rerun()
        
        with col2:
            if st.button(
                "Deletar", 
                key=f"delete_{chat['id']}", 
                help=f"Excluir '{chat['title']}'",
                type="secondary"
            ):
                confirm_key = f"confirm_delete_sidebar_{chat['id']}"
                st.session_state[confirm_key] = True
        
        _render_delete_confirmation(chat, is_current)


def _render_delete_confirmation(chat, is_current):
    confirm_key = f"confirm_delete_sidebar_{chat['id']}"
    
    if st.session_state.get(confirm_key, False):
        st.warning(f"Excluir '{chat['title']}'?")
        
        col_yes, col_no = st.columns(2)
        
        with col_yes:
            if st.button("Sim", key=f"yes_{chat['id']}", help="Confirmar exclusão"):
                _handle_chat_deletion(chat, is_current, confirm_key)
        
        with col_no:
            if st.button("Não", key=f"no_{chat['id']}", help="Cancelar"):
                del st.session_state[confirm_key]
                st.rerun()


def _handle_chat_deletion(chat, is_current, confirm_key):
    with st.spinner("Excluindo..."):
        result = delete_chat(chat['id'], st.session_state.id_token)
        
        if result['success']:
            if is_current:
                st.session_state.current_chat = None
            
            del st.session_state[confirm_key]
            st.success("Chat excluído!")
            time.sleep(1)
            st.rerun()
        else:
            st.error(f"Erro: {result['error']}")
            del st.session_state[confirm_key]
            time.sleep(2)
            st.rerun()
