"""
Rotas para predições de preços usando ML
"""

from flask import Blueprint, request
import sys
import os

# Adicionar src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from api.utils.response import APIResponse, APIError
from advanced_analyzer import AdvancedAnalyzer

predictions_bp = Blueprint('predictions', __name__)

@predictions_bp.route('/', methods=['GET'])
def get_predictions():
    """GET /api/predictions?days=7 - Predições para todos os jogos"""
    try:
        days = request.args.get('days', 7, type=int)
        
        # Validação
        if days < 1 or days > 30:
            raise APIError("Dias deve estar entre 1 e 30", 400)
        
        analyzer = AdvancedAnalyzer()
        predictions = analyzer.predict_future_prices(days=days)
        
        # Converter predições para formato API
        predictions_list = []
        for _, row in predictions.iterrows():
            trend_percent = ((row['predicted_price'] - row['current_price']) / row['current_price']) * 100
            
            # Determinar recomendação baseada na tendência
            if trend_percent <= -15:
                recommendation = "🔥 AGUARDE! Grande queda prevista"
                recommendation_type = "wait_big_drop"
            elif trend_percent <= -5:
                recommendation = "⏳ Espere, possível queda"
                recommendation_type = "wait_small_drop"
            elif trend_percent >= 10:
                recommendation = "👍 Compre agora, alta prevista"
                recommendation_type = "buy_now"
            else:
                recommendation = "🤔 Preço estável"
                recommendation_type = "stable"
            
            predictions_list.append({
                'game_name': row['game'],
                'steam_id': row.get('steam_id', 'unknown'),
                'current_price': float(row['current_price']),
                'predicted_price': float(row['predicted_price']),
                'trend_percent': round(trend_percent, 1),
                'days_ahead': days,
                'recommendation': recommendation,
                'recommendation_type': recommendation_type,
                'confidence': row.get('confidence', 'medium'),
                'current_price_formatted': f"R$ {row['current_price']:.2f}",
                'predicted_price_formatted': f"R$ {row['predicted_price']:.2f}"
            })
        
        # Ordenar por maior impacto (maior queda primeiro)
        predictions_list.sort(key=lambda x: x['trend_percent'])
        
        return APIResponse.success(
            predictions_list, 
            f"Predições para {days} dias de {len(predictions_list)} jogos"
        )
        
    except APIError:
        raise
    except Exception as e:
        return APIResponse.error(f"Erro ao gerar predições: {str(e)}")

@predictions_bp.route('/<steam_id>', methods=['GET'])
def get_game_prediction(steam_id):
    """GET /api/predictions/{steam_id}?days=7 - Predição específica de um jogo"""
    try:
        days = request.args.get('days', 7, type=int)
        
        # Validação
        if days < 1 or days > 30:
            raise APIError("Dias deve estar entre 1 e 30", 400)
        
        analyzer = AdvancedAnalyzer()
        
        # Buscar predição específica do jogo
        all_predictions = analyzer.predict_future_prices(days=days)
        game_prediction = all_predictions[all_predictions['steam_id'] == steam_id]
        
        if game_prediction.empty:
            raise APIError(f"Jogo {steam_id} não encontrado", 404)
        
        row = game_prediction.iloc[0]
        trend_percent = ((row['predicted_price'] - row['current_price']) / row['current_price']) * 100
        
        # Recomendação detalhada
        if trend_percent <= -15:
            recommendation = "🔥 AGUARDE! Grande queda prevista"
            recommendation_type = "wait_big_drop"
            advice = "Este é um ótimo momento para aguardar. O modelo prevê uma queda significativa."
        elif trend_percent <= -5:
            recommendation = "⏳ Espere, possível queda"
            recommendation_type = "wait_small_drop"
            advice = "Pode valer a pena aguardar alguns dias para uma possível queda de preço."
        elif trend_percent >= 10:
            recommendation = "👍 Compre agora, alta prevista"
            recommendation_type = "buy_now"
            advice = "O preço atual está bom e pode subir. Considere comprar agora."
        else:
            recommendation = "🤔 Preço estável"
            recommendation_type = "stable"
            advice = "O preço deve permanecer estável. Decisão baseada em preferência pessoal."
        
        prediction_result = {
            'game_name': row['game'],
            'steam_id': steam_id,
            'current_price': float(row['current_price']),
            'predicted_price': float(row['predicted_price']),
            'price_change': float(row['predicted_price'] - row['current_price']),
            'trend_percent': round(trend_percent, 1),
            'days_ahead': days,
            'recommendation': recommendation,
            'recommendation_type': recommendation_type,
            'advice': advice,
            'confidence': row.get('confidence', 'medium'),
            'model_accuracy': "75.7%",
            'formatted_prices': {
                'current': f"R$ {row['current_price']:.2f}",
                'predicted': f"R$ {row['predicted_price']:.2f}",
                'change': f"R$ {row['predicted_price'] - row['current_price']:+.2f}"
            }
        }
        
        return APIResponse.success(
            prediction_result, 
            f"Predição para {row['game']} em {days} dias"
        )
        
    except APIError:
        raise
    except Exception as e:
        return APIResponse.error(f"Erro ao gerar predição: {str(e)}")

@predictions_bp.route('/model/info', methods=['GET'])
def get_model_info():
    """GET /api/predictions/model/info - Informações do modelo ML"""
    try:
        analyzer = AdvancedAnalyzer()
        
        # Obter métricas do modelo (simuladas por enquanto)
        model_info = {
            'model_type': 'Random Forest Regressor',
            'accuracy': {
                'r2_score': 0.757,
                'mean_absolute_error': 15.06,
                'accuracy_percentage': '75.7%'
            },
            'features': [
                {'name': 'price_ma_7', 'importance': 52.9, 'description': 'Média móvel 7 dias'},
                {'name': 'price_ma_30', 'importance': 16.4, 'description': 'Média móvel 30 dias'},
                {'name': 'price_lag_30', 'importance': 8.8, 'description': 'Preço de 30 dias atrás'},
                {'name': 'price_lag_7', 'importance': 7.2, 'description': 'Preço de 7 dias atrás'},
                {'name': 'price_std_30', 'importance': 5.5, 'description': 'Volatilidade 30 dias'},
            ],
            'training_data': {
                'games_count': 10,
                'records_count': 1009,
                'date_range': '2014-2024',
                'last_updated': '2025-08-28'
            },
            'prediction_capabilities': {
                'max_days_ahead': 30,
                'min_days_ahead': 1,
                'supported_games': 10,
                'update_frequency': 'daily'
            }
        }
        
        return APIResponse.success(model_info, "Informações do modelo ML")
        
    except Exception as e:
        return APIResponse.error(f"Erro ao buscar informações do modelo: {str(e)}")
