"""
Rotas para análises básicas e avançadas
"""

from flask import Blueprint, request
import sys
import os

# Adicionar src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from api.utils.response import APIResponse, APIError
from basic_analyzer import BasicAnalyzer
from advanced_analyzer import AdvancedAnalyzer

analysis_bp = Blueprint('analysis', __name__)

@analysis_bp.route('/basic/stats', methods=['GET'])
def get_basic_stats():
    """GET /api/analysis/basic/stats - Estatísticas básicas do banco"""
    try:
        analyzer = BasicAnalyzer()
        stats = analyzer.get_database_stats()
        
        return APIResponse.success(stats, "Estatísticas básicas")
        
    except Exception as e:
        return APIResponse.error(f"Erro ao buscar estatísticas: {str(e)}")

@analysis_bp.route('/basic/best-deals', methods=['GET'])
def get_best_deals():
    """GET /api/analysis/basic/best-deals - Melhores oportunidades"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        if limit > 50:
            limit = 50
            
        analyzer = BasicAnalyzer()
        deals_df = analyzer.get_best_deals(limit=limit)
        
        # Converter DataFrame para lista de dicionários
        deals_list = []
        for _, row in deals_df.iterrows():
            deals_list.append({
                'game_name': row['Jogo'],
                'current_price': float(row['Preço_Atual'].replace('R$ ', '').replace(',', '.')),
                'min_price': float(row['Preço_Mínimo'].replace('R$ ', '').replace(',', '.')),
                'avg_price': float(row['Preço_Médio'].replace('R$ ', '').replace(',', '.')),
                'opportunity_score': row['Score_Oportunidade'],
                'recommendation': row['Recomendação'],
                'current_price_formatted': row['Preço_Atual'],
                'min_price_formatted': row['Preço_Mínimo'],
                'avg_price_formatted': row['Preço_Médio']
            })
        
        return APIResponse.success(deals_list, f"Top {len(deals_list)} oportunidades")
        
    except Exception as e:
        return APIResponse.error(f"Erro ao buscar oportunidades: {str(e)}")

@analysis_bp.route('/advanced/seasonal', methods=['GET'])
def get_seasonal_analysis():
    """GET /api/analysis/advanced/seasonal - Análise sazonal"""
    try:
        analyzer = AdvancedAnalyzer()
        seasonal_data = analyzer.seasonal_analysis()
        
        # Converter dados sazonais para formato API
        monthly_stats = seasonal_data['monthly_stats']
        
        seasonal_result = {
            'monthly_averages': [
                {
                    'month': int(month),
                    'month_name': [
                        'Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
                        'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'
                    ][int(month) - 1],
                    'avg_price': float(data['mean']),
                    'price_std': float(data['std'])
                }
                for month, data in monthly_stats.iterrows()
            ],
            'best_months': seasonal_data['best_promotion_months'],
            'insights': {
                'cheapest_month': int(monthly_stats['mean'].idxmin()),
                'most_expensive_month': int(monthly_stats['mean'].idxmax()),
                'most_volatile_month': int(monthly_stats['std'].idxmax())
            }
        }
        
        return APIResponse.success(seasonal_result, "Análise sazonal completa")
        
    except Exception as e:
        return APIResponse.error(f"Erro na análise sazonal: {str(e)}")

@analysis_bp.route('/advanced/anomalies', methods=['GET'])
def get_anomalies():
    """GET /api/analysis/advanced/anomalies - Detecção de anomalias"""
    try:
        limit = request.args.get('limit', 20, type=int)
        
        analyzer = AdvancedAnalyzer()
        anomalies = analyzer.detect_anomalies(limit=limit)
        
        # Converter anomalias para formato API
        anomalies_list = []
        for anomaly in anomalies:
            anomalies_list.append({
                'game_name': anomaly['game'],
                'price': float(anomaly['price']),
                'price_formatted': f"R$ {anomaly['price']:.2f}",
                'date': anomaly['date'].isoformat() if hasattr(anomaly['date'], 'isoformat') else str(anomaly['date']),
                'type': anomaly['type'],
                'severity': anomaly.get('severity', 'medium')
            })
        
        return APIResponse.success(anomalies_list, f"Encontradas {len(anomalies_list)} anomalias")
        
    except Exception as e:
        return APIResponse.error(f"Erro na detecção de anomalias: {str(e)}")

@analysis_bp.route('/game/<steam_id>/detailed', methods=['GET'])
def get_game_detailed_analysis(steam_id):
    """GET /api/analysis/game/{steam_id}/detailed - Análise detalhada de um jogo"""
    try:
        analyzer = BasicAnalyzer()
        
        # Análise específica do jogo
        game_analysis = analyzer.analyze_specific_game(steam_id)
        
        if not game_analysis:
            raise APIError(f"Jogo {steam_id} não encontrado", 404)
        
        return APIResponse.success(game_analysis, f"Análise detalhada do jogo")
        
    except APIError:
        raise
    except Exception as e:
        return APIResponse.error(f"Erro na análise do jogo: {str(e)}")
