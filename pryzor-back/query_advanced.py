"""
Interface de consulta simples para análises específicas
Fase 1.2: Interface amigável para usuário final
"""

import sys
import os
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta

# Adiciona o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database_manager import DatabaseManager
from basic_analyzer import BasicAnalyzer
from advanced_analyzer import AdvancedAnalyzer
from price_alerts import PriceAlertSystem

class QueryInterface:
    def __init__(self):
        """Inicializa a interface de consulta"""
        self.db = DatabaseManager()
        self.basic_analyzer = BasicAnalyzer()
        self.advanced_analyzer = AdvancedAnalyzer()
        self.alert_system = PriceAlertSystem()
    
    def show_main_menu(self):
        """Mostra menu principal"""
        print("\n🎮 PRYZOR - INTERFACE DE CONSULTA AVANÇADA")
        print("=" * 60)
        print("📊 ANÁLISES BÁSICAS:")
        print("  1. 📈 Estatísticas gerais")
        print("  2. 🔥 Melhores oportunidades")
        print("  3. 💰 Preços atuais")
        print("  4. 🎯 Análise de jogo específico")
        print("  5. 📊 Gerar gráfico de evolução")
        
        print("\n🤖 ANÁLISES AVANÇADAS:")
        print("  6. 📅 Análise sazonal")
        print("  7. 🔮 Predições futuras")
        print("  8. ⚠️ Detecção de anomalias")
        print("  9. 🚀 Análise completa avançada")
        
        print("\n🚨 SISTEMA DE ALERTAS:")
        print(" 10. 👀 Adicionar jogo ao monitoramento")
        print(" 11. ❌ Remover jogo do monitoramento")
        print(" 12. 🔍 Verificar alertas agora")
        print(" 13. 📊 Status do monitoramento")
        
        print("\n📈 RELATÓRIOS:")
        print(" 14. 📋 Comparar múltiplos jogos")
        print(" 15. 🎲 Recomendações personalizadas")
        print(" 16. 📊 Dashboard resumido")
        
        print("\n 0. ❌ Sair")
        print("=" * 60)
    
    def analyze_specific_game(self):
        """Análise detalhada de um jogo específico"""
        games = self.db.get_games()
        
        if games.empty:
            print("❌ Nenhum jogo encontrado no banco")
            return
        
        print("\n🎮 JOGOS DISPONÍVEIS:")
        for i, row in games.iterrows():
            print(f"{i+1:2d}. {row['name']}")
        
        try:
            choice = int(input("\nEscolha um jogo (número): ")) - 1
            if 0 <= choice < len(games):
                game_name = games.iloc[choice]['name']
                game_id = games.iloc[choice]['id']
                
                print(f"\n📊 ANÁLISE DETALHADA: {game_name}")
                print("=" * 60)
                
                # Dados históricos
                game_data = self.db.get_price_history(game_id=game_id)
                
                if not game_data.empty:
                    current_price = game_data['price'].iloc[-1]
                    min_price = game_data['price'].min()
                    max_price = game_data['price'].max()
                    avg_price = game_data['price'].mean()
                    volatility = game_data['price'].std()
                    
                    print(f"💰 Preço atual: R$ {current_price:.2f}")
                    print(f"📉 Menor preço: R$ {min_price:.2f}")
                    print(f"📈 Maior preço: R$ {max_price:.2f}")
                    print(f"📊 Preço médio: R$ {avg_price:.2f}")
                    print(f"📊 Volatilidade: R$ {volatility:.2f}")
                    print(f"📅 Total de registros: {len(game_data)}")
                    
                    # Análise de posição atual
                    if max_price > min_price:
                        position = ((current_price - min_price) / (max_price - min_price)) * 100
                        print(f"📍 Posição no histórico: {position:.1f}%")
                        
                        if position < 25:
                            print("🔥 EXCELENTE oportunidade - preço muito baixo!")
                        elif position < 50:
                            print("👍 BOA oportunidade - preço abaixo da média")
                        elif position < 75:
                            print("🤔 Preço RAZOÁVEL - considere esperar")
                        else:
                            print("❌ Preço ALTO - recomenda-se esperar")
                    
                    # Tendência recente (últimos 30 dias)
                    recent_data = game_data.tail(30)
                    if len(recent_data) > 1:
                        trend = recent_data['price'].iloc[-1] - recent_data['price'].iloc[0]
                        trend_percent = (trend / recent_data['price'].iloc[0]) * 100
                        
                        print(f"📈 Tendência (30 dias): {trend_percent:+.1f}%")
                        
                        if trend_percent > 5:
                            print("⬆️ Preço em ALTA - considere comprar logo")
                        elif trend_percent < -5:
                            print("⬇️ Preço em QUEDA - boa oportunidade")
                        else:
                            print("➡️ Preço ESTÁVEL")
                    
                    # Gráfico específico
                    self.basic_analyzer.create_price_chart(game_name)
                    
                else:
                    print("❌ Nenhum dado histórico encontrado")
            else:
                print("❌ Opção inválida")
        except ValueError:
            print("❌ Digite um número válido")
    
    def compare_multiple_games(self):
        """Compara múltiplos jogos lado a lado"""
        games = self.db.get_games()
        
        print("\n🎮 COMPARAÇÃO DE JOGOS")
        print("=" * 60)
        print("Escolha até 5 jogos para comparar (digite os números separados por vírgula)")
        
        for i, row in games.iterrows():
            print(f"{i+1:2d}. {row['name']}")
        
        try:
            choices = input("\nJogos para comparar (ex: 1,3,5): ").split(',')
            selected_games = []
            
            for choice in choices:
                idx = int(choice.strip()) - 1
                if 0 <= idx < len(games):
                    selected_games.append(games.iloc[idx])
            
            if not selected_games:
                print("❌ Nenhum jogo válido selecionado")
                return
            
            print(f"\n📊 COMPARAÇÃO DE {len(selected_games)} JOGOS:")
            print("=" * 80)
            
            comparison_data = []
            
            for game in selected_games:
                game_data = self.db.get_price_history(game_id=game['id'])
                
                if not game_data.empty:
                    current_price = game_data['price'].iloc[-1]
                    min_price = game_data['price'].min()
                    max_price = game_data['price'].max()
                    avg_price = game_data['price'].mean()
                    
                    # Calcula score de oportunidade
                    if max_price > min_price:
                        position = ((current_price - min_price) / (max_price - min_price))
                        opportunity_score = (1 - position) * 100
                    else:
                        opportunity_score = 50
                    
                    comparison_data.append({
                        'Jogo': game['name'],
                        'Preço_Atual': f"R$ {current_price:.2f}",
                        'Mínimo': f"R$ {min_price:.2f}",
                        'Máximo': f"R$ {max_price:.2f}",
                        'Média': f"R$ {avg_price:.2f}",
                        'Score_Oportunidade': f"{opportunity_score:.1f}/100"
                    })
            
            if comparison_data:
                df = pd.DataFrame(comparison_data)
                print(df.to_string(index=False))
                
                # Salva comparação
                output_path = Path("data/analysis_output/game_comparison.csv")
                df.to_csv(output_path, index=False)
                print(f"\n💾 Comparação salva em: {output_path}")
            
        except ValueError:
            print("❌ Formato inválido")
    
    def personalized_recommendations(self):
        """Gera recomendações personalizadas baseadas em preferências"""
        print("\n🎯 RECOMENDAÇÕES PERSONALIZADAS")
        print("=" * 60)
        
        # Coleta preferências do usuário
        try:
            max_budget = float(input("💰 Orçamento máximo (R$): "))
            
            print("\n📊 Tipo de análise:")
            print("1. Melhor custo-benefício (preço vs histórico)")
            print("2. Maior potencial de economia")
            print("3. Preços mais estáveis")
            print("4. Tendência de queda prevista")
            
            analysis_type = int(input("Escolha o tipo (1-4): "))
            
            # Busca dados
            latest_prices = self.db.get_latest_prices()
            all_history = self.db.get_price_history()
            
            # Filtra por orçamento
            affordable_games = latest_prices[latest_prices['price'] <= max_budget]
            
            if affordable_games.empty:
                print(f"❌ Nenhum jogo encontrado dentro do orçamento de R$ {max_budget:.2f}")
                return
            
            recommendations = []
            
            for _, row in affordable_games.iterrows():
                game_name = row['name']
                current_price = row['price']
                
                game_history = all_history[all_history['name'] == game_name]
                
                if len(game_history) > 5:
                    min_price = game_history['price'].min()
                    max_price = game_history['price'].max()
                    avg_price = game_history['price'].mean()
                    volatility = game_history['price'].std()
                    
                    # Calcula métricas baseadas no tipo de análise
                    if analysis_type == 1:  # Custo-benefício
                        if max_price > min_price:
                            score = ((avg_price - current_price) / avg_price) * 100
                        else:
                            score = 0
                    elif analysis_type == 2:  # Potencial de economia
                        score = ((max_price - current_price) / max_price) * 100
                    elif analysis_type == 3:  # Estabilidade (menor volatilidade)
                        score = 100 - min(volatility / avg_price * 100, 100) if avg_price > 0 else 0
                    else:  # Tendência de queda (simplified)
                        recent_data = game_history.tail(10)
                        if len(recent_data) > 1:
                            trend = (recent_data['price'].iloc[-1] - recent_data['price'].iloc[0]) / recent_data['price'].iloc[0]
                            score = max(0, -trend * 100)  # Maior score para tendência de queda
                        else:
                            score = 0
                    
                    recommendations.append({
                        'game': game_name,
                        'price': current_price,
                        'score': max(0, score),
                        'min_price': min_price,
                        'avg_price': avg_price
                    })
            
            # Ordena por score
            recommendations.sort(key=lambda x: x['score'], reverse=True)
            
            print(f"\n🎯 TOP RECOMENDAÇÕES (Orçamento: R$ {max_budget:.2f}):")
            print("=" * 80)
            
            for i, rec in enumerate(recommendations[:10], 1):
                print(f"{i:2d}. 🎮 {rec['game']}")
                print(f"     💰 Preço atual: R$ {rec['price']:.2f}")
                print(f"     📊 Score: {rec['score']:.1f}/100")
                print(f"     📉 Mínimo histórico: R$ {rec['min_price']:.2f}")
                print(f"     📊 Média histórica: R$ {rec['avg_price']:.2f}")
                print()
            
        except ValueError:
            print("❌ Valor inválido inserido")
    
    def show_dashboard(self):
        """Mostra dashboard resumido com principais informações"""
        print("\n📊 DASHBOARD PRYZOR")
        print("=" * 60)
        
        # Estatísticas gerais
        stats = self.db.get_database_stats()
        print("📈 ESTATÍSTICAS GERAIS:")
        print(f"  🎮 Total de jogos: {stats['total_games']}")
        print(f"  📊 Registros de preço: {stats['total_price_records']}")
        print(f"  📅 Período dos dados: {stats['date_range']}")
        
        # Top 3 oportunidades
        print("\n🔥 TOP 3 OPORTUNIDADES:")
        deals = self.basic_analyzer.find_best_deals(3)
        if not deals.empty:
            for i, row in deals.iterrows():
                print(f"  {i+1}. {row['Jogo']} - {row['Preço_Atual']} ({row['Score_Oportunidade']})")
        
        # Status de alertas
        print("\n🚨 STATUS DE ALERTAS:")
        monitored_count = len(self.alert_system.alert_rules['monitored_games'])
        last_check = self.alert_system.alert_rules.get('last_check', 'Nunca')
        print(f"  👀 Jogos monitorados: {monitored_count}")
        print(f"  🕒 Última verificação: {last_check}")
        
        # Verificação rápida de alertas
        recent_alerts = self.alert_system.run_alert_check()
        if recent_alerts:
            print(f"  🚨 Alertas ativos: {len(recent_alerts)}")
        else:
            print("  ✅ Nenhum alerta ativo")
        
        print("\n" + "=" * 60)
    
    def run_interface(self):
        """Executa a interface principal"""
        while True:
            self.show_main_menu()
            
            try:
                choice = input("\nEscolha uma opção: ").strip()
                
                if choice == "0":
                    print("👋 Até logo!")
                    break
                
                elif choice == "1":
                    self.basic_analyzer.get_summary_stats()
                
                elif choice == "2":
                    self.basic_analyzer.find_best_deals()
                
                elif choice == "3":
                    print("\n📈 PREÇOS ATUAIS:")
                    current = self.db.get_latest_prices()
                    for _, row in current.iterrows():
                        print(f"🎮 {row['name']}: R$ {row['price']:.2f}")
                
                elif choice == "4":
                    self.analyze_specific_game()
                
                elif choice == "5":
                    self.basic_analyzer.create_price_chart()
                
                elif choice == "6":
                    self.advanced_analyzer.analyze_seasonal_patterns()
                
                elif choice == "7":
                    days = int(input("Quantos dias à frente (padrão 30): ") or "30")
                    self.advanced_analyzer.predict_future_prices(days)
                
                elif choice == "8":
                    self.advanced_analyzer.detect_price_anomalies()
                
                elif choice == "9":
                    self.advanced_analyzer.run_advanced_analysis()
                
                elif choice == "10":
                    games = self.db.get_games()
                    print("\nJogos disponíveis:")
                    for i, row in games.iterrows():
                        print(f"{i+1}. {row['name']}")
                    
                    game_idx = int(input("Escolha um jogo: ")) - 1
                    if 0 <= game_idx < len(games):
                        game_name = games.iloc[game_idx]['name']
                        target_price = input("Preço alvo (opcional, Enter para pular): ")
                        target_price = float(target_price) if target_price else None
                        self.alert_system.add_game_to_watch(game_name, target_price)
                
                elif choice == "11":
                    games = [g['name'] for g in self.alert_system.alert_rules['monitored_games']]
                    if games:
                        print("\nJogos monitorados:")
                        for i, game in enumerate(games, 1):
                            print(f"{i}. {game}")
                        
                        game_idx = int(input("Escolha um jogo para remover: ")) - 1
                        if 0 <= game_idx < len(games):
                            self.alert_system.remove_game_from_watch(games[game_idx])
                    else:
                        print("Nenhum jogo sendo monitorado")
                
                elif choice == "12":
                    self.alert_system.run_alert_check()
                
                elif choice == "13":
                    self.alert_system.show_monitoring_status()
                
                elif choice == "14":
                    self.compare_multiple_games()
                
                elif choice == "15":
                    self.personalized_recommendations()
                
                elif choice == "16":
                    self.show_dashboard()
                
                else:
                    print("❌ Opção inválida")
                
                input("\n⏸️ Pressione Enter para continuar...")
                
            except KeyboardInterrupt:
                print("\n\n👋 Até logo!")
                break
            except Exception as e:
                print(f"❌ Erro: {e}")
                input("⏸️ Pressione Enter para continuar...")

if __name__ == "__main__":
    interface = QueryInterface()
    interface.run_interface()
