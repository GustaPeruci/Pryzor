"""
Setup simplificado do MySQL usando PyMySQL
"""

import pymysql
import sys
import os
from pathlib import Path

def create_database():
    print("🔧 SETUP MYSQL SIMPLES - PRYZOR")
    print("=" * 40)
    
    try:
        # Conecta sem especificar database
        print("🔌 Conectando ao MySQL...")
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='root',
            charset='utf8mb4'
        )
        
        print("✅ Conectado!")
        
        cursor = connection.cursor()
        
        # Cria database se não existir
        print("📁 Criando database 'pryzor_db'...")
        cursor.execute("CREATE DATABASE IF NOT EXISTS pryzor_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        
        print("✅ Database criado!")
        
        # Seleciona database
        cursor.execute("USE pryzor_db")
        
        # Cria tabelas
        print("📊 Criando tabelas...")
        
        # Tabela de jogos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS games (
                id INT AUTO_INCREMENT PRIMARY KEY,
                steam_id VARCHAR(50) UNIQUE NOT NULL,
                name VARCHAR(255) NOT NULL,
                current_price DECIMAL(10,2),
                base_price DECIMAL(10,2),
                discount_percent INT DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_steam_id (steam_id),
                INDEX idx_name (name)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # Tabela de histórico de preços
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS price_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                game_id INT NOT NULL,
                price DECIMAL(10,2) NOT NULL,
                discount_percent INT DEFAULT 0,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                source VARCHAR(50) DEFAULT 'manual',
                FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE,
                INDEX idx_game_id (game_id),
                INDEX idx_timestamp (timestamp)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        print("✅ Tabelas criadas!")
        
        # Fecha conexão
        connection.close()
        
        print("\n🎉 SETUP CONCLUÍDO COM SUCESSO!")
        print("Agora você pode executar:")
        print("  python test_mysql.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    create_database()
