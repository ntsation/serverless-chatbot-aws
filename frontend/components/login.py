import streamlit as st
import time
from ..services import (
    authenticate_user,
    create_cognito_user,
    create_user_in_dynamodb,
    get_user_info
)
from ..utils import get_custom_css, check_configuration
from ..config import APPSYNC_URL, COGNITO_USER_POOL_ID, COGNITO_USER_POOL_CLIENT_ID


def render_login_page():
    st.markdown(get_custom_css(), unsafe_allow_html=True)
    
    st.markdown("""
    <div class="main-header">
        <h1>AWS Serverless Chatbot</h1>
        <p>Converse com IA usando tecnologia serverless da AWS</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not check_configuration(APPSYNC_URL, COGNITO_USER_POOL_ID, COGNITO_USER_POOL_CLIENT_ID):
        st.error("**Configuração incompleta!**")
        st.markdown("""
        ### Como configurar:
        
        1. **Configure o ambiente AWS:**
        ```bash
        cd tests
        ./setup_env.sh
        ```
        
        2. **Execute a aplicação:**
        ```bash
        ./run_streamlit.sh
        ```
        """)
        return
    
    _render_system_info()
    
    tab1, tab2 = st.tabs(["Login", "Criar Conta"])
    
    with tab1:
        _render_login_tab()
    
    with tab2:
        _render_register_tab()


def _render_system_info():
    with st.expander("ℹSobre o Sistema", expanded=False):
        st.markdown("""
        <div class="feature-box">
            <h4>Tecnologias Utilizadas</h4>
            <ul>
                <li><strong>AWS Cognito</strong> - Autenticação e autorização</li>
                <li><strong>AWS AppSync</strong> - API GraphQL</li>
                <li><strong>AWS Lambda</strong> - Processamento serverless</li>
                <li><strong>AWS DynamoDB</strong> - Banco de dados NoSQL</li>
                <li><strong>Streamlit</strong> - Interface web</li>
            </ul>
        </div>
        
        <div class="feature-box">
            <h4>Recursos</h4>
            <ul>
                <li>Autenticação segura com JWT tokens</li>
                <li>Conversas em tempo real</li>
                <li>Histórico persistente</li>
                <li>Interface responsiva</li>
                <li>Escalabilidade automática</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)


def _render_login_tab():
    st.markdown("### Entre com sua conta")
    
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            email = st.text_input(
                "Email", 
                key="login_email",
                placeholder="seu.email@example.com"
            )
            password = st.text_input(
                "Senha", 
                type="password", 
                key="login_password",
                placeholder="Sua senha"
            )
            
            st.write("")
            
            if st.button("Entrar", key="login_button", type="primary", use_container_width=True):
                if email and password:
                    _handle_login(email, password)
                else:
                    st.warning("Por favor, preencha todos os campos")


def _render_register_tab():
    st.markdown("### Crie sua conta gratuita")
    
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            new_name = st.text_input(
                "Nome completo", 
                key="register_name",
                placeholder="Seu nome completo"
            )
            new_email = st.text_input(
                "Email", 
                key="register_email",
                placeholder="seu.email@example.com"
            )
            new_password = st.text_input(
                "Senha", 
                type="password", 
                key="register_password",
                placeholder="Mínimo 8 caracteres",
                help="A senha deve ter pelo menos 8 caracteres"
            )
            confirm_password = st.text_input(
                "Confirmar senha", 
                type="password", 
                key="confirm_password",
                placeholder="Digite a senha novamente"
            )
            
            _validate_password_fields(new_password, confirm_password)
            
            st.write("")
            
            if st.button("Criar Conta", key="register_button", type="primary", use_container_width=True):
                if new_name and new_email and new_password and confirm_password:
                    _handle_register(new_name, new_email, new_password, confirm_password)
                else:
                    st.warning("Por favor, preencha todos os campos")


def _validate_password_fields(new_password, confirm_password):
    if new_password:
        if len(new_password) >= 8:
            st.success("Senha válida")
        else:
            st.error("Senha deve ter pelo menos 8 caracteres")
    
    if confirm_password and new_password:
        if new_password == confirm_password:
            st.success("Senhas coincidem")
        else:
            st.error("Senhas não coincidem")


def _handle_login(email, password):
    with st.spinner("Autenticando..."):
        auth_result = authenticate_user(email, password)
        
    if auth_result['success']:
        st.session_state.authenticated = True
        st.session_state.id_token = auth_result['id_token']
        st.session_state.access_token = auth_result['access_token']
        
        with st.spinner("Carregando perfil..."):
            user_info = get_user_info(auth_result['id_token'])
        
        if user_info['success']:
            st.session_state.user = user_info['user']
            st.success("Login realizado com sucesso!")
            time.sleep(1)
            st.rerun()
        else:
            st.error("Erro ao obter informações do usuário")
    else:
        st.error(f"Erro no login: {auth_result['error']}")


def _handle_register(new_name, new_email, new_password, confirm_password):
    if new_password != confirm_password:
        st.error("As senhas não coincidem")
        return
    
    if len(new_password) < 8:
        st.error("A senha deve ter pelo menos 8 caracteres")
        return
    
    with st.spinner("Criando conta..."):
        cognito_result = create_cognito_user(new_email, new_password, new_name)
        
        if cognito_result['success']:
            with st.spinner("Autenticando..."):
                auth_result = authenticate_user(new_email, new_password)
            
            if auth_result['success']:
                with st.spinner("Configurando perfil..."):
                    db_result = create_user_in_dynamodb(new_email, new_name, auth_result['id_token'])
                
                if db_result['success']:
                    st.session_state.authenticated = True
                    st.session_state.id_token = auth_result['id_token']
                    st.session_state.access_token = auth_result['access_token']
                    st.session_state.user = db_result['user']
                    st.success("Conta criada com sucesso!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"Erro ao criar perfil: {db_result['error']}")
            else:
                st.error(f"Erro na autenticação: {auth_result['error']}")
        else:
            error_msg = cognito_result['error']
            if "UsernameExistsException" in error_msg:
                st.error("Este email já está em uso. Tente fazer login.")
            else:
                st.error(f"Erro ao criar conta: {error_msg}")
