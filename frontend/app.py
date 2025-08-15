import streamlit as st
from frontend.config import APP_CONFIG
from frontend.components import render_login_page, render_sidebar, render_chat_page
from frontend.utils import init_session_state


def configure_page():
    st.set_page_config(
        page_title=APP_CONFIG['page_title'],
        page_icon=APP_CONFIG['page_icon'],
        layout=APP_CONFIG['layout'],
        initial_sidebar_state=APP_CONFIG['initial_sidebar_state']
    )


def main():
    configure_page()
    
    init_session_state()
    
    if not st.session_state.authenticated:
        render_login_page()
    else:
        st.title("AWS Serverless Chatbot")
        
        render_sidebar()
        
        render_chat_page()


if __name__ == "__main__":
    main()
