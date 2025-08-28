"""
Sistema de alertas de preço
Fase 1.2: Monitoramento automático de oportunidades
"""

import pandas as pd
import json
from datetime import datetime, timedelta
from pathlib import Path
import sys
import os

# Adiciona o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from database_manager import DatabaseManager
from advanced_analyzer import AdvancedAnalyzer

class PriceAlertSystem:
    def __init__(self):
        """Inicializa o sistema de alertas"""
        self.db = DatabaseManager()
        self.analyzer = AdvancedAnalyzer()
        self.alerts_path = Path(__file__).parent.parent / "data" / "alerts.json"
        self.load_alert_rules()
    
    def load_alert_rules(self):
        """Carrega regras de alerta salvas"""
        if self.alerts_path.exists():
            with open(self.alerts_path, 'r', encoding='utf-8') as f:
                self.alert_rules = json.load(f)
        else:
            self.alert_rules = {
                'price_drop_threshold': 15,  # % de queda para alertar
                'price_below_avg_threshold': 20,  # % abaixo da média histórica
                'monitored_games': [],  # Lista de jogos específicos para monitorar
                'last_check': None
            }
            self.save_alert_rules()
    
    def save_alert_rules(self):
        """Salva regras de alerta"""
        with open(self.alerts_path, 'w', encoding='utf-8') as f:
            json.dump(self.alert_rules, f, indent=2, ensure_ascii=False)
    
    def add_game_to_watch(self, game_name, target_price=None):
        """Adiciona um jogo à lista de monitoramento"""
        if game_name not in [g['name'] for g in self.alert_rules['monitored_games']]:
            self.alert_rules['monitored_games'].append({
                'name': game_name,
                'target_price': target_price,
                'added_date': datetime.now().isoformat()
            })
            self.save_alert_rules()
            print(f"✅ {game_name} adicionado ao monitoramento")
            if target_price:
                print(f"   🎯 Alerta quando preço ≤ R$ {target_price:.2f}")
        else:
            print(f"⚠️ {game_name} já está sendo monitorado")
    
    def remove_game_from_watch(self, game_name):
        """Remove um jogo da lista de monitoramento"""
        original_count = len(self.alert_rules['monitored_games'])
        self.alert_rules['monitored_games'] = [
            g for g in self.alert_rules['monitored_games'] 
            if g['name'] != game_name
        ]
        
        if len(self.alert_rules['monitored_games']) < original_count:
            self.save_alert_rules()
            print(f"✅ {game_name} removido do monitoramento")
        else:
            print(f"⚠️ {game_name} não estava sendo monitorado")
    
    def check_price_drops(self):
        """Verifica quedas significativas de preço"""
        print("🔍 VERIFICANDO QUEDAS DE PREÇO...")
        
        # Busca preços dos últimos 7 dias
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        recent_data = self.db.get_price_history(
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d')
        )
        
        if recent_data.empty:
            print("📅 Nenhum dado recente encontrado")
            return []
        
        alerts = []
        
        for game in recent_data['name'].unique():
            game_data = recent_data[recent_data['name'] == game].sort_values('date')
            
            if len(game_data) < 2:
                continue
            
            # Compara preço atual com preço de 7 dias atrás
            current_price = game_data['price'].iloc[-1]
            old_price = game_data['price'].iloc[0]
            
            if old_price > 0:
                drop_percent = ((old_price - current_price) / old_price) * 100
                
                if drop_percent >= self.alert_rules['price_drop_threshold']:
                    alerts.append({
                        'type': 'price_drop',
                        'game': game,
                        'current_price': current_price,
                        'old_price': old_price,
                        'drop_percent': drop_percent,
                        'message': f"📉 {game}: Queda de {drop_percent:.1f}% (R$ {old_price:.2f} → R$ {current_price:.2f})"
                    })
        
        return alerts
    
    def check_historical_opportunities(self):
        """Verifica oportunidades baseadas no histórico"""
        print("📊 VERIFICANDO OPORTUNIDADES HISTÓRICAS...")
        
        all_data = self.db.get_price_history()
        latest_prices = self.db.get_latest_prices()
        
        alerts = []
        
        for _, row in latest_prices.iterrows():
            game_name = row['name']
            current_price = row['price']
            
            # Histórico do jogo
            game_history = all_data[all_data['name'] == game_name]
            
            if len(game_history) > 10:
                avg_price = game_history['price'].mean()
                min_price = game_history['price'].min()
                
                # Verifica se está significativamente abaixo da média
                below_avg_percent = ((avg_price - current_price) / avg_price) * 100
                
                if below_avg_percent >= self.alert_rules['price_below_avg_threshold']:
                    # Calcula posição no histórico (0-100%)
                    price_position = ((current_price - min_price) / (game_history['price'].max() - min_price)) * 100
                    
                    alerts.append({
                        'type': 'historical_opportunity',
                        'game': game_name,
                        'current_price': current_price,
                        'avg_price': avg_price,
                        'below_avg_percent': below_avg_percent,
                        'price_position': price_position,
                        'message': f"🎯 {game_name}: {below_avg_percent:.1f}% abaixo da média (posição histórica: {price_position:.0f}%)"
                    })
        
        return alerts
    
    def check_monitored_games(self):
        """Verifica jogos específicos da lista de monitoramento"""
        print("👀 VERIFICANDO JOGOS MONITORADOS...")
        
        if not self.alert_rules['monitored_games']:
            print("📝 Nenhum jogo sendo monitorado")
            return []
        
        latest_prices = self.db.get_latest_prices()
        alerts = []
        
        for monitored_game in self.alert_rules['monitored_games']:
            game_name = monitored_game['name']
            target_price = monitored_game.get('target_price')
            
            # Busca preço atual
            current_game = latest_prices[latest_prices['name'].str.contains(game_name, case=False, na=False)]
            
            if not current_game.empty:
                current_price = current_game['price'].iloc[0]
                
                if target_price and current_price <= target_price:
                    alerts.append({
                        'type': 'target_reached',
                        'game': game_name,
                        'current_price': current_price,
                        'target_price': target_price,
                        'message': f"🎯 {game_name}: Alerta de preço! R$ {current_price:.2f} ≤ R$ {target_price:.2f}"
                    })
        
        return alerts
    
    def check_prediction_alerts(self):
        """Verifica alertas baseados em predições"""
        print("🔮 VERIFICANDO PREDIÇÕES...")
        
        try:
            # Executa predições (apenas para jogos monitorados se houver)
            predictions = self.analyzer.predict_future_prices(7)  # 7 dias à frente
            
            if not predictions:
                return []
            
            alerts = []
            
            for pred in predictions:
                # Alerta para quedas previstas significativas
                if pred['trend_percent'] <= -10:
                    alerts.append({
                        'type': 'predicted_drop',
                        'game': pred['game'],
                        'current_price': pred['current_price'],
                        'trend_percent': pred['trend_percent'],
                        'message': f"🔮 {pred['game']}: Queda de {pred['trend_percent']:.1f}% prevista nos próximos 7 dias"
                    })
                
                # Alerta para altas previstas (urgência de compra)
                elif pred['trend_percent'] >= 15:
                    alerts.append({
                        'type': 'predicted_rise',
                        'game': pred['game'],
                        'current_price': pred['current_price'],
                        'trend_percent': pred['trend_percent'],
                        'message': f"🚀 {pred['game']}: Alta de {pred['trend_percent']:.1f}% prevista - considere comprar agora!"
                    })
            
            return alerts
            
        except Exception as e:
            print(f"⚠️ Erro nas predições: {e}")
            return []
    
    def run_alert_check(self):
        """Executa verificação completa de alertas"""
        print("🚨 SISTEMA DE ALERTAS - VERIFICAÇÃO COMPLETA")
        print("=" * 60)
        
        all_alerts = []
        
        # 1. Verifica quedas de preço
        price_drop_alerts = self.check_price_drops()
        all_alerts.extend(price_drop_alerts)
        
        # 2. Verifica oportunidades históricas
        historical_alerts = self.check_historical_opportunities()
        all_alerts.extend(historical_alerts)
        
        # 3. Verifica jogos monitorados
        monitored_alerts = self.check_monitored_games()
        all_alerts.extend(monitored_alerts)
        
        # 4. Verifica predições
        prediction_alerts = self.check_prediction_alerts()
        all_alerts.extend(prediction_alerts)
        
        # Atualiza timestamp da última verificação
        self.alert_rules['last_check'] = datetime.now().isoformat()
        self.save_alert_rules()
        
        # Exibe resultados
        if all_alerts:
            print(f"\n🚨 {len(all_alerts)} ALERTAS ENCONTRADOS:")
            print("=" * 60)
            
            for i, alert in enumerate(all_alerts, 1):
                print(f"{i}. {alert['message']}")
            
            # Salva relatório de alertas
            alert_report = pd.DataFrame([{
                'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'Tipo': alert['type'],
                'Jogo': alert['game'],
                'Mensagem': alert['message']
            } for alert in all_alerts])
            
            # Para MySQL, usamos um caminho relativo ao projeto
            from pathlib import Path
            report_path = Path(__file__).parent.parent / "data" / "analysis_output" / "alert_report.csv"
            
            # Anexa ao relatório existente ou cria novo
            if report_path.exists():
                existing_report = pd.read_csv(report_path)
                combined_report = pd.concat([existing_report, alert_report], ignore_index=True)
            else:
                combined_report = alert_report
            
            combined_report.to_csv(report_path, index=False)
            print(f"\n💾 Relatório salvo em: {report_path}")
            
        else:
            print("\n✅ Nenhum alerta encontrado no momento")
        
        return all_alerts
    
    def show_monitoring_status(self):
        """Mostra status atual do monitoramento"""
        print("\n📊 STATUS DO MONITORAMENTO")
        print("=" * 50)
        print(f"🎯 Limite queda de preço: {self.alert_rules['price_drop_threshold']}%")
        print(f"📉 Limite abaixo da média: {self.alert_rules['price_below_avg_threshold']}%")
        print(f"🕒 Última verificação: {self.alert_rules.get('last_check', 'Nunca')}")
        
        if self.alert_rules['monitored_games']:
            print(f"\n👀 JOGOS MONITORADOS ({len(self.alert_rules['monitored_games'])}):")
            for game in self.alert_rules['monitored_games']:
                target_info = f" (alvo: R$ {game['target_price']:.2f})" if game.get('target_price') else ""
                print(f"  🎮 {game['name']}{target_info}")
        else:
            print("\n📝 Nenhum jogo específico sendo monitorado")

if __name__ == "__main__":
    alert_system = PriceAlertSystem()
    alert_system.show_monitoring_status()
    alert_system.run_alert_check()
