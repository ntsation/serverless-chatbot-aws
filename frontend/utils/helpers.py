import streamlit as st
from datetime import datetime


def check_configuration(appsync_url, cognito_user_pool_id, cognito_user_pool_client_id):
    return all([appsync_url, cognito_user_pool_id, cognito_user_pool_client_id])


def generate_chat_title():
    return f"Chat {datetime.now().strftime('%d/%m %H:%M')}"


def clear_session_state():
    keys_to_clear = ['authenticated', 'id_token', 'access_token', 'user', 'current_chat']
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]


def init_session_state():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
