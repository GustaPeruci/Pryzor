"""
Migrador de dados - Converte CSV wide-format para banco normalizado
Fase 1.1: Migração dos dados existentes
"""

import pandas as pd
import numpy as np
from pathlib import Path
import re
from datetime import datetime
import sys
import os

# Adiciona o diretório src ao path para importar o database_manager
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from database_manager import DatabaseManager

class DataMigrator:
    def __init__(self):
        """Inicializa o migrador de dados"""
        self.db = DatabaseManager()
        self.data_path = Path(__file__).parent.parent / "data"
        
    def extract_steam_id_from_filename(self, filename):
        """Extrai o Steam ID do nome do arquivo CSV"""
        # Padrão: nome_do_jogo_STEAMID.csv
        match = re.search(r'_(\d+)\.csv$', filename)
        if match:
            return int(match.group(1))
        return None
    
    def process_wide_format_csv(self, csv_path):
        """Processa o CSV em formato wide e migra para o banco"""
        print(f"📂 Processando arquivo: {csv_path}")
        
        try:
            # Lê o CSV
            df = pd.read_csv(csv_path)
            
            print(f"  ✅ CSV carregado: {len(df)} jogos encontrados")
            
            migrated_games = 0
            migrated_prices = 0
            
            for _, row in df.iterrows():
                game_name = row['nome_jogo']
                steam_id = int(row['steam_id']) if pd.notna(row['steam_id']) else None
                
                if not steam_id:
                    print(f"  ⚠️  Steam ID não encontrado para {game_name}, pulando...")
                    continue
                
                # Adiciona o jogo ao banco
                game_id = self.db.add_game(steam_id, game_name)
                migrated_games += 1
                
                # Processa todas as colunas de semana
                week_columns = [col for col in df.columns if col.startswith('semana_')]
                
                for week_col in week_columns:
                    price = row[week_col]
                    
                    if pd.notna(price) and price > 0:
                        # Extrai ano e semana da coluna (formato: semana_YYYY-WW)
                        week_match = re.match(r'semana_(\d{4})-(\d{2})', week_col)
                        if week_match:
                            year = int(week_match.group(1))
                            week = int(week_match.group(2))
                            
                            # Converte para data (primeira segunda-feira da semana)
                            try:
                                date = datetime.strptime(f'{year}-W{week:02d}-1', '%Y-W%U-%w')
                                date_str = date.strftime('%Y-%m-%d')
                                week_year = f"{year}-{week:02d}"
                                
                                self.db.add_price_record(game_id, price, date_str, week_year)
                                migrated_prices += 1
                            except ValueError:
                                continue
            
            print(f"  ✅ Migração concluída: {migrated_games} jogos, {migrated_prices} registros de preço")
            return migrated_games, migrated_prices
            
        except Exception as e:
            print(f"  ❌ Erro ao processar {csv_path}: {e}")
            return 0, 0
    
    def process_steamdb_csv_files(self):
        """Processa arquivos CSV individuais do SteamDB"""
        steamdb_path = self.data_path / "steamdb_csv"
        
        if not steamdb_path.exists():
            print("❌ Pasta steamdb_csv não encontrada")
            return
        
        csv_files = list(steamdb_path.glob("*.csv"))
        
        if not csv_files:
            print("❌ Nenhum arquivo CSV encontrado na pasta steamdb_csv")
            return
        
        print(f"📁 Encontrados {len(csv_files)} arquivos CSV do SteamDB")
        
        total_games = 0
        total_prices = 0
        
        for csv_file in csv_files:
            steam_id = self.extract_steam_id_from_filename(csv_file.name)
            
            if not steam_id:
                print(f"  ⚠️  Não foi possível extrair Steam ID de {csv_file.name}")
                continue
            
            # Extrai nome do jogo do arquivo
            game_name = csv_file.stem.replace(f"_{steam_id}", "").replace("_", " ").title()
            
            try:
                # Lê arquivo CSV do SteamDB
                df = pd.read_csv(csv_file)
                
                # Adiciona jogo ao banco
                game_id = self.db.add_game(steam_id, game_name)
                total_games += 1
                
                # Processa registros de preço
                prices_added = 0
                for _, row in df.iterrows():
                    try:
                        # Assume que o CSV tem colunas 'Date' e 'Price'
                        if 'Date' in df.columns and 'Price' in df.columns:
                            date = pd.to_datetime(row['Date']).strftime('%Y-%m-%d')
                            price = float(str(row['Price']).replace('R$', '').replace(',', '.').strip())
                            
                            # Calcula semana do ano
                            date_obj = pd.to_datetime(date)
                            week_year = f"{date_obj.year}-{date_obj.week:02d}"
                            
                            self.db.add_price_record(game_id, price, date, week_year)
                            prices_added += 1
                    except Exception as e:
                        continue
                
                total_prices += prices_added
                print(f"  ✅ {game_name}: {prices_added} registros de preço")
                
            except Exception as e:
                print(f"  ❌ Erro ao processar {csv_file.name}: {e}")
        
        print(f"\n🎉 Migração do SteamDB concluída: {total_games} jogos, {total_prices} registros")
    
    def migrate_wide_format_data(self):
        """Migra dados do formato wide CSV para o banco normalizado"""
        wide_csv = self.data_path / "steamdb_dataset_geral_wide.csv"
        
        if wide_csv.exists():
            print("🔄 Migrando dados do formato wide...")
            games, prices = self.process_wide_format_csv(wide_csv)
            print(f"✅ Migração wide concluída: {games} jogos, {prices} registros")
        else:
            print("📝 Arquivo wide format não encontrado, processando CSVs individuais...")
            self.process_steamdb_csv_files()
    
    def run_migration(self):
        """Executa a migração completa"""
        print("🚀 Iniciando migração de dados...")
        print("=" * 50)
        
        # Primeiro tenta migrar dados wide format
        self.migrate_wide_format_data()
        
        # Exibe estatísticas finais
        print("\n📊 Estatísticas finais do banco:")
        stats = self.db.get_database_stats()
        for key, value in stats.items():
            print(f"  📈 {key}: {value}")
        
        print("\n✅ Migração concluída com sucesso!")

if __name__ == "__main__":
    migrator = DataMigrator()
    migrator.run_migration()
