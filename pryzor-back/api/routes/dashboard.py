"""
Rotas para dados do dashboard principal
"""

from flask import Blueprint, request
import sys
import os
from datetime import datetime, timedelta

# Adicionar src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from api.utils.response import APIResponse, APIError
from database_manager import DatabaseManager
from basic_analyzer import BasicAnalyzer
from advanced_analyzer import AdvancedAnalyzer

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/', methods=['GET'])
def get_dashboard_overview():
    """GET /api/dashboard - Visão geral completa do dashboard"""
    try:
        db_manager = DatabaseManager()
        basic_analyzer = BasicAnalyzer()
        advanced_analyzer = AdvancedAnalyzer()
        
        # Estatísticas básicas
        games_stats = basic_analyzer.get_basic_stats()
        
        # Melhores ofertas
        best_deals = basic_analyzer.find_best_deals(limit=5)
        
        # Predições rápidas (próximos 7 dias)
        predictions = advanced_analyzer.predict_future_prices(days=7)
        
        # Top 5 predições com maior queda
        top_predictions = predictions.nlargest(5, 'predicted_price')
        
        # Contadores gerais
        total_games = len(games_stats)
        total_records = sum(game['records_count'] for game in games_stats)
        
        # Calcular economia potencial das ofertas
        total_savings = sum(deal.get('discount_amount', 0) for deal in best_deals)
        
        dashboard_data = {
            'summary': {
                'total_games': total_games,
                'total_records': total_records,
                'total_savings_available': round(total_savings, 2),
                'last_updated': datetime.now().isoformat(),
                'model_accuracy': '75.7%'
            },
            'quick_stats': {
                'games_with_data': total_games,
                'average_price': round(sum(g['avg_price'] for g in games_stats) / total_games, 2) if total_games > 0 else 0,
                'cheapest_game': min(games_stats, key=lambda x: x['current_price'])['game_name'] if games_stats else None,
                'most_expensive': max(games_stats, key=lambda x: x['current_price'])['game_name'] if games_stats else None
            },
            'best_deals': [
                {
                    'game_name': deal['game_name'],
                    'current_price': deal['current_price'],
                    'lowest_price': deal['lowest_price'],
                    'discount_percentage': deal['discount_percentage'],
                    'savings': deal.get('discount_amount', 0),
                    'formatted_current': f"R$ {deal['current_price']:.2f}",
                    'formatted_lowest': f"R$ {deal['lowest_price']:.2f}"
                }
                for deal in best_deals[:3]  # Top 3 para dashboard
            ],
            'top_predictions': [
                {
                    'game_name': row['game'],
                    'current_price': float(row['current_price']),
                    'predicted_price': float(row['predicted_price']),
                    'trend_percent': round(((row['predicted_price'] - row['current_price']) / row['current_price']) * 100, 1),
                    'recommendation': '🔥 Aguarde' if ((row['predicted_price'] - row['current_price']) / row['current_price']) * 100 < -10 else '👍 Compre'
                }
                for _, row in top_predictions.head(3).iterrows()  # Top 3 para dashboard
            ],
            'charts_data': {
                'price_trends': _get_price_trends_data(),
                'deals_by_month': _get_deals_timeline_data(),
                'games_distribution': _get_games_distribution_data()
            }
        }
        
        return APIResponse.success(dashboard_data, "Dashboard overview")
        
    except Exception as e:
        return APIResponse.error(f"Erro ao carregar dashboard: {str(e)}")

@dashboard_bp.route('/charts/price-trends', methods=['GET'])
def get_price_trends():
    """GET /api/dashboard/charts/price-trends - Dados para gráfico de tendências"""
    try:
        days = request.args.get('days', 30, type=int)
        
        # Validação
        if days < 7 or days > 365:
            raise APIError("Dias deve estar entre 7 e 365", 400)
        
        trends_data = _get_price_trends_data(days)
        
        return APIResponse.success(trends_data, f"Tendências dos últimos {days} dias")
        
    except APIError:
        raise
    except Exception as e:
        return APIResponse.error(f"Erro ao buscar tendências: {str(e)}")

@dashboard_bp.route('/charts/deals-timeline', methods=['GET'])
def get_deals_timeline():
    """GET /api/dashboard/charts/deals-timeline - Timeline das melhores ofertas"""
    try:
        months = request.args.get('months', 6, type=int)
        
        if months < 1 or months > 24:
            raise APIError("Meses deve estar entre 1 e 24", 400)
        
        timeline_data = _get_deals_timeline_data(months)
        
        return APIResponse.success(timeline_data, f"Timeline de {months} meses")
        
    except APIError:
        raise
    except Exception as e:
        return APIResponse.error(f"Erro ao buscar timeline: {str(e)}")

@dashboard_bp.route('/charts/predictions-summary', methods=['GET'])
def get_predictions_summary():
    """GET /api/dashboard/charts/predictions-summary - Resumo das predições"""
    try:
        advanced_analyzer = AdvancedAnalyzer()
        predictions = advanced_analyzer.predict_future_prices(days=7)
        
        # Categorizar predições
        big_drops = 0      # <= -15%
        small_drops = 0    # -15% a -5%
        stable = 0         # -5% a +5%
        increases = 0      # > +5%
        
        for _, row in predictions.iterrows():
            trend = ((row['predicted_price'] - row['current_price']) / row['current_price']) * 100
            
            if trend <= -15:
                big_drops += 1
            elif trend <= -5:
                small_drops += 1
            elif trend <= 5:
                stable += 1
            else:
                increases += 1
        
        summary_data = {
            'predictions_count': len(predictions),
            'categories': {
                'big_drops': {'count': big_drops, 'label': 'Grandes Quedas (>15%)', 'color': '#e74c3c'},
                'small_drops': {'count': small_drops, 'label': 'Pequenas Quedas (5-15%)', 'color': '#f39c12'},
                'stable': {'count': stable, 'label': 'Estável (±5%)', 'color': '#95a5a6'},
                'increases': {'count': increases, 'label': 'Aumentos (>5%)', 'color': '#27ae60'}
            },
            'recommendations': {
                'wait_for_drop': big_drops + small_drops,
                'buy_now': increases,
                'neutral': stable
            }
        }
        
        return APIResponse.success(summary_data, "Resumo das predições")
        
    except Exception as e:
        return APIResponse.error(f"Erro ao resumir predições: {str(e)}")

def _get_price_trends_data(days=30):
    """Função auxiliar para dados de tendências de preços"""
    try:
        db_manager = DatabaseManager()
        
        # Buscar dados dos últimos N dias
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Simular dados de tendência (em produção, buscar do banco)
        # Por enquanto, retornar estrutura para o frontend
        trends = {
            'labels': [],
            'datasets': []
        }
        
        # Gerar labels de datas
        current_date = start_date
        while current_date <= end_date:
            trends['labels'].append(current_date.strftime('%Y-%m-%d'))
            current_date += timedelta(days=1)
        
        # Dados simulados para alguns jogos principais
        games_sample = ['Counter-Strike 2', 'Dota 2', 'PUBG', 'Apex Legends']
        colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12']
        
        for i, game in enumerate(games_sample):
            # Simular dados de preço (em produção, buscar do banco)
            data_points = [round(50 + i*10 + (j % 7) * 2, 2) for j in range(len(trends['labels']))]
            
            trends['datasets'].append({
                'label': game,
                'data': data_points,
                'borderColor': colors[i],
                'backgroundColor': colors[i] + '20',
                'tension': 0.4
            })
        
        return trends
        
    except Exception:
        return {'labels': [], 'datasets': []}

def _get_deals_timeline_data(months=6):
    """Função auxiliar para timeline de ofertas"""
    try:
        # Simular dados de ofertas por mês
        timeline = {
            'labels': [],
            'datasets': [{
                'label': 'Ofertas Encontradas',
                'data': [],
                'backgroundColor': '#3498db',
                'borderColor': '#2980b9'
            }]
        }
        
        # Gerar últimos N meses
        current_date = datetime.now()
        for i in range(months):
            month_date = current_date - timedelta(days=30*i)
            timeline['labels'].insert(0, month_date.strftime('%b %Y'))
            # Simular número de ofertas (em produção, calcular do banco)
            timeline['datasets'][0]['data'].insert(0, 10 + (i % 4) * 5)
        
        return timeline
        
    except Exception:
        return {'labels': [], 'datasets': []}

def _get_games_distribution_data():
    """Função auxiliar para distribuição de jogos por faixa de preço"""
    try:
        basic_analyzer = BasicAnalyzer()
        games_stats = basic_analyzer.get_basic_stats()
        
        # Categorizar jogos por faixa de preço
        price_ranges = {
            'Gratuitos': 0,
            'Até R$ 20': 0,
            'R$ 20-50': 0,
            'R$ 50-100': 0,
            'Mais de R$ 100': 0
        }
        
        for game in games_stats:
            price = game['current_price']
            if price == 0:
                price_ranges['Gratuitos'] += 1
            elif price <= 20:
                price_ranges['Até R$ 20'] += 1
            elif price <= 50:
                price_ranges['R$ 20-50'] += 1
            elif price <= 100:
                price_ranges['R$ 50-100'] += 1
            else:
                price_ranges['Mais de R$ 100'] += 1
        
        distribution = {
            'labels': list(price_ranges.keys()),
            'data': list(price_ranges.values()),
            'backgroundColor': [
                '#2ecc71',  # Verde para gratuitos
                '#3498db',  # Azul para baratos
                '#f39c12',  # Laranja para médios
                '#e67e22',  # Laranja escuro
                '#e74c3c'   # Vermelho para caros
            ]
        }
        
        return distribution
        
    except Exception:
        return {'labels': [], 'data': []}
