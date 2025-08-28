"""
Script para inicializar e executar a API Flask
"""

import os
import sys
from pathlib import Path

# Adicionar diretório raiz ao Python path
root_dir = Path(__file__).parent
sys.path.append(str(root_dir))
sys.path.append(str(root_dir / 'src'))

from api.app import create_app
from api.config import config

def main():
    """Função principal para executar a API"""
    
    # Determinar ambiente
    env = os.environ.get('FLASK_ENV', 'development')
    
    # Criar aplicação
    app = create_app(config_name=env)
    
    # Configurações de execução
    host = os.environ.get('API_HOST', '127.0.0.1')
    port = int(os.environ.get('API_PORT', 5000))
    debug = env == 'development'
    
    print(f"🚀 Iniciando Pryzor API")
    print(f"📍 Ambiente: {env}")
    print(f"🌐 URL: http://{host}:{port}")
    print(f"📊 Swagger: http://{host}:{port}/api/info")
    print(f"💖 Health: http://{host}:{port}/health")
    print("=" * 50)
    
    try:
        # Executar aplicação
        app.run(
            host=host,
            port=port,
            debug=debug,
            use_reloader=debug,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n🛑 API interrompida pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao executar API: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
