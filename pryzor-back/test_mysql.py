"""
Script de teste completo para verificar migração MySQL
Testa todas as funcionalidades básicas
"""

import sys
import os
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_mysql_connection():
    """Testa conexão básica com MySQL"""
    print("🔌 Testando conexão MySQL...")
    
    try:
        from database_manager import DatabaseManager
        db = DatabaseManager()
        stats = db.get_database_stats()
        
        print("✅ MySQL conectado com sucesso!")
        print(f"  📊 {stats['total_games']} jogos no banco")
        print(f"  📈 {stats['total_price_records']} registros de preço")
        return True
        
    except Exception as e:
        print(f"❌ Erro na conexão MySQL: {e}")
        print("🔧 Execute: python setup_mysql.py")
        return False

def test_basic_analysis():
    """Testa análise básica"""
    print("\n📊 Testando análise básica...")
    
    try:
        from basic_analyzer import BasicAnalyzer
        analyzer = BasicAnalyzer()
        
        # Teste estatísticas
        stats = analyzer.get_summary_stats()
        
        # Teste oportunidades
        deals = analyzer.find_best_deals(3)
        
        print("✅ Análise básica funcionando!")
        return True
        
    except Exception as e:
        print(f"❌ Erro na análise básica: {e}")
        return False

def test_advanced_analysis():
    """Testa análise avançada"""
    print("\n🤖 Testando análise avançada...")
    
    try:
        from advanced_analyzer import AdvancedAnalyzer
        analyzer = AdvancedAnalyzer()
        
        # Teste análise sazonal
        monthly_stats, promotion_months = analyzer.analyze_seasonal_patterns()
        
        print("✅ Análise avançada funcionando!")
        return True
        
    except Exception as e:
        print(f"❌ Erro na análise avançada: {e}")
        return False

def test_alerts():
    """Testa sistema de alertas"""
    print("\n🚨 Testando sistema de alertas...")
    
    try:
        from price_alerts import PriceAlertSystem
        alert_system = PriceAlertSystem()
        
        # Teste verificação de alertas
        alerts = alert_system.run_alert_check()
        
        print("✅ Sistema de alertas funcionando!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no sistema de alertas: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("🧪 TESTE COMPLETO MYSQL - PRYZOR")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 4
    
    # Teste 1: Conexão MySQL
    if test_mysql_connection():
        tests_passed += 1
    
    # Teste 2: Análise básica
    if test_basic_analysis():
        tests_passed += 1
    
    # Teste 3: Análise avançada
    if test_advanced_analysis():
        tests_passed += 1
    
    # Teste 4: Alertas
    if test_alerts():
        tests_passed += 1
    
    # Resultado final
    print(f"\n📊 RESULTADO DOS TESTES")
    print("=" * 30)
    print(f"✅ Testes passaram: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("🚀 Projeto MySQL pronto para uso!")
        print("\n🎯 Próximos comandos:")
        print("  python query_advanced.py  # Interface completa")
        print("  python main_advanced.py   # Pipeline avançado")
    else:
        print("⚠️ Alguns testes falharam")
        print("🔧 Verifique a configuração do MySQL")
        
        if tests_passed == 0:
            print("\n💡 Passos para resolver:")
            print("1. python setup_mysql.py")
            print("2. python migrate_to_mysql.py (se tiver dados SQLite)")
            print("3. python main.py (para criar dados)")

if __name__ == "__main__":
    main()
