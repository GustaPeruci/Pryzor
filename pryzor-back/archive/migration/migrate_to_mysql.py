"""
Script para migrar dados do SQLite para MySQL
Preserva todos os dados existentes
"""

import sqlite3
import sys
import os
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database_manager import DatabaseManager
from mysql_config import get_mysql_config

class SQLiteToMySQLMigrator:
    def __init__(self):
        """Inicializa o migrador"""
        self.sqlite_path = Path("database/pryzor.db")
        self.mysql_db = None
        
    def check_sqlite_exists(self):
        """Verifica se o banco SQLite existe"""
        if not self.sqlite_path.exists():
            print("❌ Banco SQLite não encontrado em database/pryzor.db")
            print("🔧 Execute primeiro: python main.py (para criar dados)")
            return False
        
        print(f"✅ Banco SQLite encontrado: {self.sqlite_path}")
        return True
    
    def connect_mysql(self):
        """Conecta ao MySQL"""
        try:
            self.mysql_db = DatabaseManager()
            print("✅ Conectado ao MySQL com sucesso")
            return True
        except Exception as e:
            print(f"❌ Erro ao conectar MySQL: {e}")
            print("🔧 Execute primeiro: python setup_mysql.py")
            return False
    
    def get_sqlite_data(self):
        """Busca dados do SQLite"""
        try:
            conn = sqlite3.connect(self.sqlite_path)
            
            # Busca jogos
            games_query = "SELECT steam_id, name FROM games ORDER BY id"
            games = []
            cursor = conn.execute(games_query)
            for row in cursor.fetchall():
                games.append({
                    'steam_id': row[0],
                    'name': row[1]
                })
            
            # Busca histórico de preços
            prices_query = """
                SELECT g.steam_id, ph.price, ph.date, ph.week_year
                FROM price_history ph
                JOIN games g ON ph.game_id = g.id
                ORDER BY g.steam_id, ph.date
            """
            prices = []
            cursor = conn.execute(prices_query)
            for row in cursor.fetchall():
                prices.append({
                    'steam_id': row[0],
                    'price': row[1],
                    'date': row[2],
                    'week_year': row[3]
                })
            
            conn.close()
            
            print(f"📊 SQLite: {len(games)} jogos, {len(prices)} registros de preço")
            return games, prices
            
        except Exception as e:
            print(f"❌ Erro ao ler SQLite: {e}")
            return [], []
    
    def migrate_games(self, games):
        """Migra jogos para MySQL"""
        print("\n🎮 Migrando jogos...")
        
        migrated = 0
        game_id_map = {}  # Mapeia steam_id -> mysql_game_id
        
        for game in games:
            try:
                game_id = self.mysql_db.add_game(game['steam_id'], game['name'])
                game_id_map[game['steam_id']] = game_id
                migrated += 1
                
                if migrated % 5 == 0:
                    print(f"  📈 {migrated}/{len(games)} jogos migrados...")
                    
            except Exception as e:
                print(f"  ⚠️ Erro ao migrar {game['name']}: {e}")
        
        print(f"✅ {migrated} jogos migrados com sucesso")
        return game_id_map
    
    def migrate_prices(self, prices, game_id_map):
        """Migra preços para MySQL"""
        print("\n💰 Migrando preços...")
        
        migrated = 0
        errors = 0
        
        for price in prices:
            steam_id = price['steam_id']
            
            if steam_id not in game_id_map:
                errors += 1
                continue
            
            try:
                game_id = game_id_map[steam_id]
                # Converte a data do SQLite para timestamp MySQL
                from datetime import datetime
                timestamp = datetime.strptime(price['date'], '%Y-%m-%d')
                
                self.mysql_db.add_price_record(
                    game_id, 
                    price['price'], 
                    timestamp,
                    price.get('discount_percent', 0)
                )
                migrated += 1
                
                if migrated % 100 == 0:
                    print(f"  📈 {migrated}/{len(prices)} preços migrados...")
                    
            except Exception as e:
                errors += 1
                if errors <= 5:  # Mostra apenas os primeiros 5 erros
                    print(f"  ⚠️ Erro ao migrar preço: {e}")
        
        print(f"✅ {migrated} preços migrados, {errors} erros")
        return migrated
    
    def verify_migration(self):
        """Verifica se a migração foi bem-sucedida"""
        print("\n🔍 Verificando migração...")
        
        # Estatísticas MySQL
        mysql_stats = self.mysql_db.get_database_stats()
        
        # Estatísticas SQLite
        conn = sqlite3.connect(self.sqlite_path)
        cursor = conn.execute("SELECT COUNT(*) FROM games")
        sqlite_games = cursor.fetchone()[0]
        cursor = conn.execute("SELECT COUNT(*) FROM price_history")
        sqlite_prices = cursor.fetchone()[0]
        conn.close()
        
        print("📊 COMPARAÇÃO:")
        print(f"  Jogos    - SQLite: {sqlite_games:4d} | MySQL: {mysql_stats['total_games']:4d}")
        print(f"  Preços   - SQLite: {sqlite_prices:4d} | MySQL: {mysql_stats['total_price_records']:4d}")
        
        # Verifica se os números batem
        games_ok = mysql_stats['total_games'] >= sqlite_games
        prices_ok = mysql_stats['total_price_records'] >= sqlite_prices * 0.95  # Aceita 5% de perda
        
        if games_ok and prices_ok:
            print("✅ Migração verificada com sucesso!")
            return True
        else:
            print("⚠️ Possível problema na migração")
            return False
    
    def run_migration(self):
        """Executa migração completa"""
        print("🔄 MIGRAÇÃO SQLITE → MYSQL")
        print("=" * 50)
        
        # Passo 1: Verificar SQLite
        if not self.check_sqlite_exists():
            return False
        
        # Passo 2: Conectar MySQL
        if not self.connect_mysql():
            return False
        
        # Passo 3: Buscar dados SQLite
        print("\n📂 Lendo dados do SQLite...")
        games, prices = self.get_sqlite_data()
        
        if not games:
            print("❌ Nenhum dado encontrado no SQLite")
            return False
        
        # Passo 4: Migrar jogos
        game_id_map = self.migrate_games(games)
        
        # Passo 5: Migrar preços
        if prices:
            self.migrate_prices(prices, game_id_map)
        
        # Passo 6: Verificar migração
        self.verify_migration()
        
        print("\n🎉 MIGRAÇÃO CONCLUÍDA!")
        print("🗄️ Dados agora disponíveis no MySQL")
        print("🚀 Execute: python main_advanced.py")
        
        return True

def main():
    """Função principal"""
    print("🔄 MIGRADOR SQLITE → MYSQL")
    print("=" * 40)
    
    # Pergunta se o usuário quer continuar
    try:
        confirm = input("Migrar dados do SQLite para MySQL? (s/N): ").lower()
        if confirm != 's':
            print("👋 Migração cancelada")
            return
        
        migrator = SQLiteToMySQLMigrator()
        success = migrator.run_migration()
        
        if success:
            # Pergunta se quer criar backup do SQLite
            backup = input("\nCriar backup do SQLite? (S/n): ").lower()
            if backup != 'n':
                import shutil
                backup_path = Path("database/pryzor_backup.db")
                shutil.copy2(migrator.sqlite_path, backup_path)
                print(f"💾 Backup criado: {backup_path}")
        
    except KeyboardInterrupt:
        print("\n👋 Migração cancelada pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")

if __name__ == "__main__":
    main()
