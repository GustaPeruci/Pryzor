"""
Script de consulta rápida para análises pontuais
Execute comandos simples no banco de dados
"""

import sys
import os
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database_manager import DatabaseManager
from basic_analyzer import BasicAnalyzer

def show_menu():
    """Mostra menu de opções"""
    print("\n🎮 PRYZOR - CONSULTA RÁPIDA")
    print("=" * 40)
    print("1. 📊 Estatísticas gerais")
    print("2. 🔥 Melhores oportunidades")
    print("3. 📈 Preços atuais")
    print("4. 🎯 Análise de jogo específico")
    print("5. 📊 Gerar gráfico de preços")
    print("6. 🔍 Análise completa")
    print("0. ❌ Sair")
    print("=" * 40)

def analyze_specific_game(analyzer, db):
    """Analisa um jogo específico"""
    games = db.get_games()
    
    print("\n🎮 JOGOS DISPONÍVEIS:")
    for i, row in games.iterrows():
        print(f"{i+1}. {row['name']}")
    
    try:
        choice = int(input("\nEscolha um jogo (número): ")) - 1
        if 0 <= choice < len(games):
            game_name = games.iloc[choice]['name']
            
            # Busca dados históricos do jogo
            game_data = db.get_price_history()
            game_data = game_data[game_data['name'] == game_name]
            
            if not game_data.empty:
                print(f"\n📊 ANÁLISE: {game_name}")
                print("=" * 50)
                print(f"💰 Preço atual: R$ {game_data['price'].iloc[-1]:.2f}")
                print(f"📉 Preço mínimo: R$ {game_data['price'].min():.2f}")
                print(f"📈 Preço máximo: R$ {game_data['price'].max():.2f}")
                print(f"📊 Preço médio: R$ {game_data['price'].mean():.2f}")
                print(f"📅 Registros: {len(game_data)} preços")
                
                # Gera gráfico específico
                analyzer.create_price_chart(game_name)
            else:
                print("❌ Nenhum dado encontrado para este jogo")
        else:
            print("❌ Opção inválida")
    except ValueError:
        print("❌ Digite um número válido")

def main():
    """Menu principal de consultas"""
    db = DatabaseManager()
    analyzer = BasicAnalyzer()
    
    while True:
        show_menu()
        
        try:
            choice = input("\nEscolha uma opção: ").strip()
            
            if choice == "0":
                print("👋 Até logo!")
                break
            
            elif choice == "1":
                print("\n📊 ESTATÍSTICAS GERAIS")
                print("=" * 50)
                stats = db.get_database_stats()
                for key, value in stats.items():
                    print(f"📈 {key.replace('_', ' ').title()}: {value}")
            
            elif choice == "2":
                print("\n🔥 MELHORES OPORTUNIDADES")
                print("=" * 50)
                deals = analyzer.find_best_deals()
                
            elif choice == "3":
                print("\n📈 PREÇOS ATUAIS")
                print("=" * 50)
                current = db.get_latest_prices()
                for _, row in current.iterrows():
                    print(f"🎮 {row['name']}: R$ {row['price']:.2f}")
            
            elif choice == "4":
                analyze_specific_game(analyzer, db)
            
            elif choice == "5":
                print("\n📊 Gerando gráfico...")
                analyzer.create_price_chart()
            
            elif choice == "6":
                print("\n🔍 Executando análise completa...")
                analyzer.run_basic_analysis()
            
            else:
                print("❌ Opção inválida")
        
        except KeyboardInterrupt:
            print("\n\n👋 Até logo!")
            break
        except Exception as e:
            print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()
