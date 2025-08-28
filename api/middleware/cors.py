"""
Configuração de CORS para permitir comunicação com frontend
"""

from flask_cors import CORS

def setup_cors(app):
    """Configura CORS para a aplicação"""
    
    # Configuração de CORS
    cors_config = {
        "origins": [
            "http://localhost:3000",  # React dev server
            "http://localhost:4200",  # Angular dev server
            "http://127.0.0.1:3000",
            "http://127.0.0.1:4200"
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": [
            "Content-Type",
            "Authorization", 
            "Access-Control-Allow-Credentials"
        ],
        "supports_credentials": True
    }
    
    # Aplicar CORS
    CORS(app, **cors_config)
    
    # Headers adicionais
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
