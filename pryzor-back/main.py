"""
Script principal para executar a Fase 1.1
Orquestra migração de dados e análise básica
"""

import sys
import os
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database_manager import DatabaseManager
from data_migrator import DataMigrator
from basic_analyzer import BasicAnalyzer

def main():
    """Executa o pipeline completo da Fase 1.1"""
    print("🚀 PRYZOR - FASE 1.1: ESTRUTURA BÁSICA")
    print("=" * 60)
    print("📋 Pipeline: Banco → Migração → Análise")
    print("=" * 60)
    
    try:
        # Passo 1: Inicializar banco de dados
        print("\n🔧 PASSO 1: Inicializando banco de dados...")
        db = DatabaseManager()
        print("✅ Banco de dados pronto!")
        
        # Passo 2: Migrar dados existentes
        print("\n📦 PASSO 2: Migrando dados existentes...")
        migrator = DataMigrator()
        migrator.run_migration()
        print("✅ Migração concluída!")
        
        # Passo 3: Executar análise básica
        print("\n📊 PASSO 3: Executando análise básica...")
        analyzer = BasicAnalyzer()
        analyzer.run_basic_analysis()
        print("✅ Análise concluída!")
        
        # Resumo final
        print("\n🎉 FASE 1.1 CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        print("📁 Estrutura criada:")
        print("  ├── 📂 database/pryzor.db (Banco SQLite)")
        print("  ├── 📂 data/analysis_output/ (Resultados)")
        print("  └── 📂 src/ (Código fonte)")
        print("\n🎯 Próximos passos:")
        print("  → Executar análises específicas")
        print("  → Adicionar novos dados do SteamDB")
        print("  → Implementar Fase 1.2 (análise avançada)")
        
        # Estatísticas finais
        stats = db.get_database_stats()
        print(f"\n📊 Banco atual: {stats['total_games']} jogos, {stats['total_price_records']} registros")
        
    except Exception as e:
        print(f"\n❌ ERRO na execução: {e}")
        print("🔧 Verifique os logs e tente novamente")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🚀 Execute 'python -m src.basic_analyzer' para análises adicionais!")
    else:
        sys.exit(1)
