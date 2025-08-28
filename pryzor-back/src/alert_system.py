"""
Sistema de alertas de preços
"""

import uuid
from datetime import datetime
from typing import List, Dict, Optional

class AlertSystem:
    """Sistema para gerenciar alertas de preços de jogos"""
    
    def __init__(self):
        # Em produção, isso seria um banco de dados
        self.alerts_storage = []
    
    def create_alert(self, alert_data: Dict) -> str:
        """Criar novo alerta"""
        alert_id = str(uuid.uuid4())
        alert = {
            'id': alert_id,
            **alert_data,
            'created_at': datetime.now().isoformat(),
            'status': 'active'
        }
        self.alerts_storage.append(alert)
        return alert_id
    
    def list_alerts(self) -> List[Dict]:
        """Listar todos os alertas"""
        return self.alerts_storage.copy()
    
    def get_alert(self, alert_id: str) -> Optional[Dict]:
        """Buscar alerta por ID"""
        for alert in self.alerts_storage:
            if alert['id'] == alert_id:
                return alert.copy()
        return None
    
    def delete_alert(self, alert_id: str) -> bool:
        """Remover alerta"""
        for i, alert in enumerate(self.alerts_storage):
            if alert['id'] == alert_id:
                del self.alerts_storage[i]
                return True
        return False
    
    def check_all_alerts(self) -> List[Dict]:
        """Verificar todos os alertas ativos e retornar os disparados"""
        triggered_alerts = []
        
        # Em produção, aqui buscaríamos preços atuais do banco
        # Por enquanto, simular alguns alertas disparados
        for alert in self.alerts_storage:
            if alert['status'] == 'active':
                # Simular verificação de preço
                current_price = alert.get('current_price', alert['target_price'] * 1.1)
                
                # Verificar se deve disparar baseado no tipo
                should_trigger = False
                message = ""
                
                if alert['alert_type'] == 'price_drop':
                    if current_price <= alert['target_price']:
                        should_trigger = True
                        message = f"Preço caiu para R$ {current_price:.2f} (alvo: R$ {alert['target_price']:.2f})"
                
                elif alert['alert_type'] == 'price_rise':
                    if current_price >= alert['target_price']:
                        should_trigger = True
                        message = f"Preço subiu para R$ {current_price:.2f} (alvo: R$ {alert['target_price']:.2f})"
                
                elif alert['alert_type'] == 'exact_price':
                    if abs(current_price - alert['target_price']) <= 0.01:
                        should_trigger = True
                        message = f"Preço atingiu exatamente R$ {current_price:.2f}"
                
                if should_trigger:
                    alert['status'] = 'triggered'
                    alert['triggered_at'] = datetime.now().isoformat()
                    alert['current_price'] = current_price
                    alert['message'] = message
                    triggered_alerts.append(alert.copy())
        
        return triggered_alerts
