"""
Script para configurar o banco de dados MySQL
Cria o banco e usuário se necessário
"""

try:
    import pymysql
    pymysql.install_as_MySQLdb()
    MYSQL_CONNECTOR = 'pymysql'
    Error = pymysql.Error
    print("✅ Usando PyMySQL como conector")
except ImportError:
    try:
        import mysql.connector
        from mysql.connector import Error
        MYSQL_CONNECTOR = 'mysql.connector'
        print("✅ Usando MySQL Connector")
    except ImportError:
        raise ImportError("Instale mysql-connector-python ou pymysql")

import sys
import os
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from mysql_config import MYSQL_CONFIG, get_mysql_config

class MySQLSetup:
    def __init__(self, environment='local'):
        """Inicializa o configurador MySQL"""
        self.config = get_mysql_config(environment)
        self.environment = environment
        
    def test_connection(self):
        """Testa conexão com MySQL (sem especificar database)"""
        try:
            if MYSQL_CONNECTOR == 'mysql.connector':
                import mysql.connector
                connection = mysql.connector.connect(
                    host=self.config['host'],
                    port=self.config['port'],
                    user=self.config['user'],
                    password=self.config['password']
                )
            else:  # pymysql
                import pymysql
                connection = pymysql.connect(
                    host=self.config['host'],
                    port=self.config['port'],
                    user=self.config['user'],
                    password=self.config['password']
                )
                user=self.config['user'],
                password=self.config['password']
            )
            
            if connection.is_connected():
                print(f"✅ Conectado ao MySQL Server {connection.get_server_info()}")
                connection.close()
                return True
                
        except Error as e:
            print(f"❌ Erro ao conectar ao MySQL: {e}")
            return False
    
    def create_database(self):
        """Cria o banco de dados se não existir"""
        try:
            connection = mysql.connector.connect(
                host=self.config['host'],
                port=self.config['port'],
                user=self.config['user'],
                password=self.config['password']
            )
            
            cursor = connection.cursor()
            
            # Verifica se o banco existe
            cursor.execute("SHOW DATABASES")
            databases = [db[0] for db in cursor.fetchall()]
            
            if self.config['database'] not in databases:
                cursor.execute(f"CREATE DATABASE {self.config['database']} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                print(f"✅ Banco de dados '{self.config['database']}' criado com sucesso")
            else:
                print(f"ℹ️ Banco de dados '{self.config['database']}' já existe")
            
            cursor.close()
            connection.close()
            return True
            
        except Error as e:
            print(f"❌ Erro ao criar banco de dados: {e}")
            return False
    
    def create_user_if_needed(self):
        """Cria usuário específico se necessário (apenas para ambiente docker)"""
        if self.environment != 'docker':
            return True
            
        try:
            connection = mysql.connector.connect(
                host=self.config['host'],
                port=self.config['port'],
                user='root',  # Usa root para criar usuário
                password='pryzor_pass'  # Senha do root no docker
            )
            
            cursor = connection.cursor()
            
            # Cria usuário se não existir
            try:
                cursor.execute(f"CREATE USER '{self.config['user']}'@'%' IDENTIFIED BY '{self.config['password']}'")
                cursor.execute(f"GRANT ALL PRIVILEGES ON {self.config['database']}.* TO '{self.config['user']}'@'%'")
                cursor.execute("FLUSH PRIVILEGES")
                print(f"✅ Usuário '{self.config['user']}' criado com sucesso")
            except Error as e:
                if "already exists" in str(e):
                    print(f"ℹ️ Usuário '{self.config['user']}' já existe")
                else:
                    print(f"⚠️ Erro ao criar usuário: {e}")
            
            cursor.close()
            connection.close()
            return True
            
        except Error as e:
            print(f"❌ Erro ao configurar usuário: {e}")
            return False
    
    def test_database_connection(self):
        """Testa conexão com o banco específico"""
        try:
            connection = mysql.connector.connect(
                host=self.config['host'],
                port=self.config['port'],
                user=self.config['user'],
                password=self.config['password'],
                database=self.config['database']
            )
            
            if connection.is_connected():
                print(f"✅ Conectado ao banco '{self.config['database']}' com sucesso")
                
                # Testa uma query simples
                cursor = connection.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                print(f"✅ Query de teste executada: {result}")
                
                cursor.close()
                connection.close()
                return True
                
        except Error as e:
            print(f"❌ Erro ao conectar ao banco: {e}")
            return False
    
    def run_setup(self):
        """Executa configuração completa"""
        print("🔧 CONFIGURANDO MYSQL PARA PRYZOR")
        print("=" * 50)
        
        print(f"\n📋 Configuração escolhida: {self.environment}")
        print(f"  Host: {self.config['host']}:{self.config['port']}")
        print(f"  Usuário: {self.config['user']}")
        print(f"  Banco: {self.config['database']}")
        
        # Passo 1: Testar conexão básica
        print("\n🔌 PASSO 1: Testando conexão...")
        if not self.test_connection():
            print("❌ Falha na conexão. Verifique se o MySQL está rodando.")
            return False
        
        # Passo 2: Criar usuário se necessário
        print("\n👤 PASSO 2: Configurando usuário...")
        if not self.create_user_if_needed():
            print("⚠️ Problema na configuração do usuário, mas continuando...")
        
        # Passo 3: Criar banco
        print("\n🗄️ PASSO 3: Criando banco de dados...")
        if not self.create_database():
            print("❌ Falha ao criar banco de dados.")
            return False
        
        # Passo 4: Testar conexão com banco
        print("\n✅ PASSO 4: Testando conexão final...")
        if not self.test_database_connection():
            print("❌ Falha na conexão com o banco.")
            return False
        
        print("\n🎉 CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!")
        print("🚀 Agora execute: python main.py")
        return True

def main():
    """Função principal do setup"""
    print("🔧 SETUP MYSQL PARA PRYZOR")
    print("=" * 40)
    
    # Escolha do ambiente
    print("Escolha o ambiente:")
    print("1. Local (MySQL local/XAMPP)")
    print("2. Docker")
    print("3. Personalizado")
    
    try:
        choice = input("\nOpção (1-3): ").strip()
        
        if choice == "1":
            environment = "xampp"  # Assume XAMPP como padrão local
        elif choice == "2":
            environment = "docker"
        elif choice == "3":
            environment = "local"
            print("\n⚠️ Configure manualmente em src/mysql_config.py")
        else:
            environment = "xampp"
            print("Usando configuração padrão (XAMPP)")
        
        setup = MySQLSetup(environment)
        setup.run_setup()
        
    except KeyboardInterrupt:
        print("\n👋 Setup cancelado pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")

if __name__ == "__main__":
    main()
