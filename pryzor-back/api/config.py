"""
Configurações da API Flask
"""

import os
from datetime import timedelta

class Config:
    """Configuração base da aplicação"""
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'pryzor-dev-secret-key-2024'
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # CORS
    CORS_ORIGINS = [
        'http://localhost:3000',  # React dev server
        'http://localhost:3001',  # React production
        'http://127.0.0.1:3000',
        'http://127.0.0.1:3001'
    ]
    
    # Database
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'pryzor')
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))
    
    # API Configuration
    API_VERSION = '1.0.0'
    API_TITLE = 'Pryzor API'
    API_DESCRIPTION = 'API para análise de preços de jogos Steam'
    
    # Pagination
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    
    # Cache
    CACHE_TIMEOUT = 300  # 5 minutos
    
    # Rate Limiting (for future use)
    RATELIMIT_ENABLED = False
    RATELIMIT_DEFAULT = "100/hour"
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'api.log')

class DevelopmentConfig(Config):
    """Configuração para desenvolvimento"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Configuração para produção"""
    DEBUG = False
    TESTING = False
    
    # Security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # CORS mais restritivo em produção
    CORS_ORIGINS = [
        'https://pryzor.app',
        'https://www.pryzor.app'
    ]

class TestingConfig(Config):
    """Configuração para testes"""
    TESTING = True
    DEBUG = True
    
    # Database de teste
    MYSQL_DATABASE = 'pryzor_test'

# Dicionário de configurações
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
