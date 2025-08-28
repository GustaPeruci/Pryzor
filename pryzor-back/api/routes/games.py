"""
Rotas para gerenciamento de jogos
"""

from flask import Blueprint, request
import sys
import os

# Adicionar src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from api.utils.response import APIResponse, APIError
from database_manager import DatabaseManager

games_bp = Blueprint('games', __name__)

@games_bp.route('/', methods=['GET'])
def get_all_games():
    """GET /api/games - Lista todos os jogos"""
    try:
        db = DatabaseManager()
        
        # Parâmetros de paginação
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Validação
        if per_page > 100:
            per_page = 100
            
        # Buscar dados
        games_data = db.get_current_prices()
        
        if games_data.empty:
            return APIResponse.success([], "Nenhum jogo encontrado")
        
        # Converter para formato da API
        games_list = []
        for _, row in games_data.iterrows():
            games_list.append({
                'name': row['name'],
                'steam_id': row['steam_id'],
                'current_price': float(row['price']),
                'current_price_formatted': f"R$ {row['price']:.2f}",
                'last_updated': row['date'].isoformat() if hasattr(row['date'], 'isoformat') else str(row['date'])
            })
        
        # Paginação simples
        total = len(games_list)
        start = (page - 1) * per_page
        end = start + per_page
        paginated_games = games_list[start:end]
        
        return APIResponse.paginated(
            data=paginated_games,
            page=page,
            per_page=per_page,
            total=total,
            message=f"Encontrados {total} jogos"
        )
        
    except Exception as e:
        return APIResponse.error(f"Erro ao buscar jogos: {str(e)}")

@games_bp.route('/<steam_id>', methods=['GET'])
def get_game_by_id(steam_id):
    """GET /api/games/{steam_id} - Busca jogo específico"""
    try:
        db = DatabaseManager()
        
        # Buscar preços históricos do jogo
        historical_data = db.get_price_data(steam_ids=[steam_id])
        
        if historical_data.empty:
            raise APIError(f"Jogo com Steam ID {steam_id} não encontrado", 404)
        
        # Dados do jogo
        game_data = historical_data.iloc[0]
        
        # Estatísticas do jogo
        prices = historical_data['price'].tolist()
        
        game_info = {
            'steam_id': steam_id,
            'name': game_data['name'],
            'current_price': float(historical_data['price'].iloc[-1]),
            'current_price_formatted': f"R$ {historical_data['price'].iloc[-1]:.2f}",
            'statistics': {
                'min_price': float(min(prices)),
                'max_price': float(max(prices)),
                'avg_price': float(sum(prices) / len(prices)),
                'price_count': len(prices)
            },
            'price_history': [
                {
                    'date': row['date'].isoformat() if hasattr(row['date'], 'isoformat') else str(row['date']),
                    'price': float(row['price']),
                    'price_formatted': f"R$ {row['price']:.2f}"
                }
                for _, row in historical_data.iterrows()
            ]
        }
        
        return APIResponse.success(game_info, f"Dados do jogo {game_data['name']}")
        
    except APIError:
        raise
    except Exception as e:
        return APIResponse.error(f"Erro ao buscar jogo: {str(e)}")

@games_bp.route('/search', methods=['GET'])
def search_games():
    """GET /api/games/search?q=termo - Busca jogos por nome"""
    try:
        query = request.args.get('q', '').strip()
        
        if not query:
            raise APIError("Parâmetro 'q' é obrigatório", 400)
        
        if len(query) < 2:
            raise APIError("Query deve ter pelo menos 2 caracteres", 400)
        
        db = DatabaseManager()
        games_data = db.get_current_prices()
        
        # Filtrar por nome (case insensitive)
        filtered_games = games_data[
            games_data['name'].str.contains(query, case=False, na=False)
        ]
        
        if filtered_games.empty:
            return APIResponse.success([], f"Nenhum jogo encontrado para '{query}'")
        
        # Converter resultado
        games_list = []
        for _, row in filtered_games.iterrows():
            games_list.append({
                'name': row['name'],
                'steam_id': row['steam_id'],
                'current_price': float(row['price']),
                'current_price_formatted': f"R$ {row['price']:.2f}",
                'last_updated': row['date'].isoformat() if hasattr(row['date'], 'isoformat') else str(row['date'])
            })
        
        return APIResponse.success(
            games_list, 
            f"Encontrados {len(games_list)} jogos para '{query}'"
        )
        
    except APIError:
        raise
    except Exception as e:
        return APIResponse.error(f"Erro na busca: {str(e)}")
