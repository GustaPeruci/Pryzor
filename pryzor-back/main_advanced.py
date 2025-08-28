"""
Script principal para Fase 1.2 - Análise Avançada
Integra todas as funcionalidades avançadas
"""

import sys
import os
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database_manager import DatabaseManager
from advanced_analyzer import AdvancedAnalyzer
from price_alerts import PriceAlertSystem

def main():
    """Executa o pipeline completo da Fase 1.2"""
    print("🚀 PRYZOR - FASE 1.2: ANÁLISE AVANÇADA")
    print("=" * 60)
    print("📋 Pipeline: Análise Sazonal → Predições → Alertas")
    print("=" * 60)
    
    try:
        # Verificar se há dados suficientes
        print("\n🔧 PASSO 1: Verificando dados...")
        db = DatabaseManager()
        stats = db.get_database_stats()
        
        if stats['total_games'] == 0:
            print("❌ Nenhum jogo encontrado no banco!")
            print("🔧 Execute primeiro: python main.py")
            return False
        
        print(f"✅ Banco carregado: {stats['total_games']} jogos, {stats['total_price_records']} registros")
        
        # Análise avançada
        print("\n📊 PASSO 2: Executando análise avançada...")
        analyzer = AdvancedAnalyzer()
        analyzer.run_advanced_analysis()
        print("✅ Análise avançada concluída!")
        
        # Sistema de alertas
        print("\n🚨 PASSO 3: Configurando sistema de alertas...")
        alert_system = PriceAlertSystem()
        
        # Adiciona alguns jogos populares ao monitoramento automático
        popular_games = ["Cyberpunk 2077", "Elden Ring", "The Witcher 3"]
        for game in popular_games:
            # Verifica se o jogo existe no banco
            games = db.get_games()
            if any(games['name'].str.contains(game, case=False, na=False)):
                alert_system.add_game_to_watch(game)
        
        # Executa verificação de alertas
        alerts = alert_system.run_alert_check()
        print("✅ Sistema de alertas configurado!")
        
        # Resumo final
        print("\n🎉 FASE 1.2 CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        print("🔧 Funcionalidades implementadas:")
        print("  ├── 📅 Análise sazonal e detecção de períodos de promoção")
        print("  ├── 🤖 Modelo preditivo com Random Forest")
        print("  ├── 🔮 Predições de preços futuros (30 dias)")
        print("  ├── ⚠️ Detecção automática de anomalias")
        print("  ├── 🚨 Sistema de alertas inteligente")
        print("  └── 📊 Interface avançada de consultas")
        
        print("\n📁 Novos arquivos gerados:")
        output_path = Path("data/analysis_output")
        if output_path.exists():
            files = list(output_path.glob("*.csv")) + list(output_path.glob("*.png"))
            for file in files:
                print(f"  📄 {file.name}")
        
        print(f"\n📊 Estatísticas atuais:")
        print(f"  🎮 {stats['total_games']} jogos monitorados")
        print(f"  📈 {stats['total_price_records']} registros de preço")
        print(f"  📅 Dados de {stats['date_range']}")
        
        if alerts:
            print(f"  🚨 {len(alerts)} alertas ativos encontrados!")
        else:
            print("  ✅ Nenhum alerta ativo no momento")
        
        print("\n🎯 Próximos comandos úteis:")
        print("  python query_advanced.py  # Interface completa avançada")
        print("  python src/advanced_analyzer.py  # Análise avançada standalone")
        print("  python src/price_alerts.py  # Verificar alertas")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO na execução: {e}")
        print("🔧 Verifique se a Fase 1.1 foi executada com sucesso")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
