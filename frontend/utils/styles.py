def get_custom_css():
    return """
    <style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .feature-box {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    </style>
    """

def get_message_style(role, content, timestamp):
    if role == 'user':
        return f"""
        <div style="background-color: #e3f2fd; padding: 10px; border-radius: 10px; margin: 5px 0; border-left: 4px solid #2196f3;">
            <strong>Você</strong> <small style="color: #666;">({timestamp})</small><br>
            {content}
        </div>
        """
    else:
        return f"""
        <div style="background-color: #f3e5f5; padding: 10px; border-radius: 10px; margin: 5px 0; border-left: 4px solid #9c27b0;">
            <strong>Assistente</strong> <small style="color: #666;">({timestamp})</small><br>
            {content}
        </div>
        """
