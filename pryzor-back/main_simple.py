# Script principal do Pryzor
# Roda análises básicas dos jogos

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database_manager import DatabaseManager
from basic_analyzer import BasicAnalyzer
from advanced_analyzer import AdvancedAnalyzer

def main():
    print("=== PRYZOR - Análise de Preços Steam ===\n")
    
    try:
        # Conectar ao banco
        print("Conectando ao MySQL...")
        db = DatabaseManager()
        
        # Análises básicas
        print("\n1. Analisando jogos...")
        analyzer = BasicAnalyzer()
        stats = analyzer.get_basic_stats()
        print(f"Total de jogos: {len(stats)}")
        
        # Melhores ofertas
        print("\n2. Buscando melhores ofertas...")
        deals = analyzer.find_best_deals(limit=3)
        for deal in deals:
            print(f"- {deal['game_name']}: R${deal['current_price']:.2f} (desconto de {deal['discount_percentage']:.1f}%)")
        
        # Predições ML
        print("\n3. Fazendo predições (7 dias)...")
        advanced = AdvancedAnalyzer()
        predictions = advanced.predict_future_prices(days=7)
        
        if not predictions.empty:
            for _, row in predictions.head(3).iterrows():
                trend = ((row['predicted_price'] - row['current_price']) / row['current_price']) * 100
                print(f"- {row['game']}: {trend:+.1f}% (R${row['current_price']:.2f} → R${row['predicted_price']:.2f})")
        
        print("\n✅ Análise concluída!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()
