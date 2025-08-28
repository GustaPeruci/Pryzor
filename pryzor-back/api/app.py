"""
PRYZOR Backend API
Sistema de análise preditiva de preços de jogos
"""

from flask import Flask
from flask_cors import CORS
import os
import sys

# Adicionar src ao path para importar módulos existentes
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from api.middleware.cors import setup_cors
from api.middleware.error_handler import setup_error_handlers
from api.utils.response import APIResponse

def create_app(config_name='development'):
    """Factory para criar app Flask"""
    app = Flask(__name__)
    
    # Carregar configuração
    from api.config import config
    app.config.from_object(config[config_name])
    
    # Configurações
    app.config['SECRET_KEY'] = 'pryzor-secret-key-change-in-production'
    app.config['JSON_SORT_KEYS'] = False
    
    # Setup CORS
    setup_cors(app)
    
    # Setup Error Handlers
    setup_error_handlers(app)
    
    # Registrar Blueprints (rotas)
    from api.routes.games import games_bp
    from api.routes.analysis import analysis_bp
    from api.routes.predictions import predictions_bp
    from api.routes.alerts import alerts_bp
    from api.routes.dashboard import dashboard_bp
    
    app.register_blueprint(games_bp, url_prefix='/api/games')
    app.register_blueprint(analysis_bp, url_prefix='/api/analysis')
    app.register_blueprint(predictions_bp, url_prefix='/api/predictions')
    app.register_blueprint(alerts_bp, url_prefix='/api/alerts')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    
    # Rota raiz da API
    @app.route('/api')
    def api_info():
        return APIResponse.success({
            'message': 'Pryzor API v1.0',
            'description': 'Sistema de análise preditiva de preços de jogos',
            'endpoints': {
                'games': '/api/games - Gestão de jogos',
                'analysis': '/api/analysis - Análises básicas e avançadas',
                'predictions': '/api/predictions - Predições de preços',
                'alerts': '/api/alerts - Sistema de alertas',
                'dashboard': '/api/dashboard - Dashboard executivo'
            },
            'status': 'online'
        })
    
    # Health check
    @app.route('/api/health')
    def health_check():
        try:
            # Teste básico de conexão com banco
            from database_manager import DatabaseManager
            db = DatabaseManager()
            stats = db.get_database_stats()
            
            return APIResponse.success({
                'status': 'healthy',
                'database': 'connected',
                'games_count': stats.get('total_games', 0),
                'records_count': stats.get('total_price_records', 0)
            })
        except Exception as e:
            return APIResponse.error(f'Health check failed: {str(e)}', 503)
    
    return app

# Para desenvolvimento
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
