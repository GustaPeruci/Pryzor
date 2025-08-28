"""
Rotas para sistema de alertas de preços
"""

from flask import Blueprint, request, jsonify
import sys
import os
from datetime import datetime, timedelta

# Adicionar src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from api.utils.response import APIResponse, APIError
from alert_system import AlertSystem

alerts_bp = Blueprint('alerts', __name__)

# Sistema de alertas global (em produção seria banco de dados)
alert_system = AlertSystem()

@alerts_bp.route('/', methods=['GET'])
def get_all_alerts():
    """GET /api/alerts - Lista todos os alertas ativos"""
    try:
        alerts = alert_system.list_alerts()
        
        # Converter alertas para formato API
        alerts_list = []
        for alert in alerts:
            alerts_list.append({
                'id': alert.get('id'),
                'game_name': alert.get('game_name'),
                'steam_id': alert.get('steam_id'),
                'target_price': float(alert.get('target_price')),
                'current_price': float(alert.get('current_price', 0)),
                'price_drop_percentage': alert.get('price_drop_percentage'),
                'alert_type': alert.get('alert_type', 'price_drop'),
                'status': alert.get('status', 'active'),
                'created_at': alert.get('created_at'),
                'triggered_at': alert.get('triggered_at'),
                'formatted_prices': {
                    'target': f"R$ {alert.get('target_price'):.2f}",
                    'current': f"R$ {alert.get('current_price', 0):.2f}"
                }
            })
        
        return APIResponse.success(
            alerts_list,
            f"Lista de {len(alerts_list)} alertas"
        )
        
    except Exception as e:
        return APIResponse.error(f"Erro ao buscar alertas: {str(e)}")

@alerts_bp.route('/', methods=['POST'])
def create_alert():
    """POST /api/alerts - Criar novo alerta"""
    try:
        data = request.get_json()
        
        # Validação dos dados
        required_fields = ['game_name', 'steam_id', 'target_price']
        for field in required_fields:
            if field not in data:
                raise APIError(f"Campo obrigatório: {field}", 400)
        
        # Validações específicas
        if data['target_price'] <= 0:
            raise APIError("Preço alvo deve ser maior que zero", 400)
        
        alert_type = data.get('alert_type', 'price_drop')
        if alert_type not in ['price_drop', 'price_rise', 'exact_price']:
            raise APIError("Tipo de alerta inválido", 400)
        
        # Criar alerta
        alert_data = {
            'game_name': data['game_name'],
            'steam_id': data['steam_id'],
            'target_price': float(data['target_price']),
            'alert_type': alert_type,
            'price_drop_percentage': data.get('price_drop_percentage'),
            'created_at': datetime.now().isoformat(),
            'status': 'active'
        }
        
        alert_id = alert_system.create_alert(alert_data)
        alert_data['id'] = alert_id
        
        return APIResponse.success(
            alert_data,
            f"Alerta criado para {data['game_name']}",
            201
        )
        
    except APIError:
        raise
    except Exception as e:
        return APIResponse.error(f"Erro ao criar alerta: {str(e)}")

@alerts_bp.route('/<alert_id>', methods=['GET'])
def get_alert(alert_id):
    """GET /api/alerts/{id} - Buscar alerta específico"""
    try:
        alert = alert_system.get_alert(alert_id)
        
        if not alert:
            raise APIError("Alerta não encontrado", 404)
        
        # Formatar resposta
        alert_data = {
            'id': alert.get('id'),
            'game_name': alert.get('game_name'),
            'steam_id': alert.get('steam_id'),
            'target_price': float(alert.get('target_price')),
            'current_price': float(alert.get('current_price', 0)),
            'price_drop_percentage': alert.get('price_drop_percentage'),
            'alert_type': alert.get('alert_type'),
            'status': alert.get('status'),
            'created_at': alert.get('created_at'),
            'triggered_at': alert.get('triggered_at'),
            'last_checked': alert.get('last_checked'),
            'formatted_prices': {
                'target': f"R$ {alert.get('target_price'):.2f}",
                'current': f"R$ {alert.get('current_price', 0):.2f}"
            }
        }
        
        return APIResponse.success(alert_data, f"Alerta {alert_id}")
        
    except APIError:
        raise
    except Exception as e:
        return APIResponse.error(f"Erro ao buscar alerta: {str(e)}")

@alerts_bp.route('/<alert_id>', methods=['DELETE'])
def delete_alert(alert_id):
    """DELETE /api/alerts/{id} - Remover alerta"""
    try:
        success = alert_system.delete_alert(alert_id)
        
        if not success:
            raise APIError("Alerta não encontrado", 404)
        
        return APIResponse.success(
            {'deleted': True, 'id': alert_id},
            f"Alerta {alert_id} removido"
        )
        
    except APIError:
        raise
    except Exception as e:
        return APIResponse.error(f"Erro ao remover alerta: {str(e)}")

@alerts_bp.route('/check', methods=['POST'])
def check_alerts():
    """POST /api/alerts/check - Verificar todos os alertas ativos"""
    try:
        triggered_alerts = alert_system.check_all_alerts()
        
        # Formatar alertas disparados
        triggered_list = []
        for alert in triggered_alerts:
            triggered_list.append({
                'id': alert.get('id'),
                'game_name': alert.get('game_name'),
                'target_price': float(alert.get('target_price')),
                'current_price': float(alert.get('current_price')),
                'alert_type': alert.get('alert_type'),
                'triggered_at': alert.get('triggered_at'),
                'message': alert.get('message'),
                'formatted_prices': {
                    'target': f"R$ {alert.get('target_price'):.2f}",
                    'current': f"R$ {alert.get('current_price'):.2f}"
                }
            })
        
        return APIResponse.success(
            {
                'triggered_alerts': triggered_list,
                'count': len(triggered_list),
                'check_timestamp': datetime.now().isoformat()
            },
            f"Verificação completa - {len(triggered_list)} alertas disparados"
        )
        
    except Exception as e:
        return APIResponse.error(f"Erro ao verificar alertas: {str(e)}")

@alerts_bp.route('/game/<steam_id>', methods=['GET'])
def get_game_alerts(steam_id):
    """GET /api/alerts/game/{steam_id} - Alertas de um jogo específico"""
    try:
        all_alerts = alert_system.list_alerts()
        game_alerts = [alert for alert in all_alerts if alert.get('steam_id') == steam_id]
        
        # Formatar alertas do jogo
        alerts_list = []
        for alert in game_alerts:
            alerts_list.append({
                'id': alert.get('id'),
                'target_price': float(alert.get('target_price')),
                'current_price': float(alert.get('current_price', 0)),
                'alert_type': alert.get('alert_type'),
                'status': alert.get('status'),
                'created_at': alert.get('created_at'),
                'formatted_prices': {
                    'target': f"R$ {alert.get('target_price'):.2f}",
                    'current': f"R$ {alert.get('current_price', 0):.2f}"
                }
            })
        
        return APIResponse.success(
            {
                'steam_id': steam_id,
                'game_name': game_alerts[0].get('game_name') if game_alerts else 'Unknown',
                'alerts': alerts_list,
                'count': len(alerts_list)
            },
            f"Alertas para jogo {steam_id}"
        )
        
    except Exception as e:
        return APIResponse.error(f"Erro ao buscar alertas do jogo: {str(e)}")

@alerts_bp.route('/stats', methods=['GET'])
def get_alerts_stats():
    """GET /api/alerts/stats - Estatísticas dos alertas"""
    try:
        all_alerts = alert_system.list_alerts()
        
        # Calcular estatísticas
        total_alerts = len(all_alerts)
        active_alerts = len([a for a in all_alerts if a.get('status') == 'active'])
        triggered_alerts = len([a for a in all_alerts if a.get('status') == 'triggered'])
        
        # Agrupar por tipo
        alert_types = {}
        for alert in all_alerts:
            alert_type = alert.get('alert_type', 'unknown')
            alert_types[alert_type] = alert_types.get(alert_type, 0) + 1
        
        # Calcular eficiência
        efficiency = (triggered_alerts / total_alerts * 100) if total_alerts > 0 else 0
        
        stats = {
            'total_alerts': total_alerts,
            'active_alerts': active_alerts,
            'triggered_alerts': triggered_alerts,
            'efficiency_percentage': round(efficiency, 1),
            'alert_types': alert_types,
            'average_target_price': 0,
            'last_check': datetime.now().isoformat()
        }
        
        # Calcular preço médio dos alvos
        if all_alerts:
            total_price = sum(float(a.get('target_price', 0)) for a in all_alerts)
            stats['average_target_price'] = round(total_price / len(all_alerts), 2)
        
        return APIResponse.success(stats, "Estatísticas dos alertas")
        
    except Exception as e:
        return APIResponse.error(f"Erro ao calcular estatísticas: {str(e)}")
