"""
Diagnóstico e configuração automática do MySQL
Testa diferentes configurações até encontrar a que funciona
"""

import mysql.connector
from mysql.connector import Error
import sys
import os
from pathlib import Path

class MySQLDiagnostic:
    def __init__(self):
        """Inicializa o diagnóstico MySQL"""
        self.working_config = None
        
        # Configurações comuns para testar
        self.test_configs = [
            {
                'name': 'XAMPP (sem senha)',
                'host': 'localhost',
                'port': 3306,
                'user': 'root',
                'password': ''
            },
            {
                'name': 'XAMPP/Local (senha root)',
                'host': 'localhost',
                'port': 3306,
                'user': 'root',
                'password': 'root'
            },
            {
                'name': 'MySQL Local (sem senha)',
                'host': 'localhost',
                'port': 3306,
                'user': 'root',
                'password': ''
            },
            {
                'name': 'MySQL Local (senha mysql)',
                'host': 'localhost',
                'port': 3306,
                'user': 'root',
                'password': 'mysql'
            },
            {
                'name': 'MySQL Local (senha 123456)',
                'host': 'localhost',
                'port': 3306,
                'user': 'root',
                'password': '123456'
            }
        ]
    
    def test_config(self, config):
        """Testa uma configuração específica"""
        try:
            connection = mysql.connector.connect(
                host=config['host'],
                port=config['port'],
                user=config['user'],
                password=config['password'],
                connect_timeout=5
            )
            
            if connection.is_connected():
                server_info = connection.get_server_info()
                connection.close()
                return True, server_info
                
        except Error as e:
            return False, str(e)
        except Exception as e:
            return False, f"Erro inesperado: {e}"
    
    def run_diagnostic(self):
        """Executa diagnóstico completo"""
        print("🔍 DIAGNÓSTICO MYSQL")
        print("=" * 50)
        
        print("Testando configurações comuns...")
        
        for i, config in enumerate(self.test_configs, 1):
            print(f"\n{i}. Testando: {config['name']}")
            print(f"   Usuário: {config['user']}")
            print(f"   Senha: {'***' if config['password'] else '(sem senha)'}")
            
            success, info = self.test_config(config)
            
            if success:
                print(f"   ✅ SUCESSO! MySQL {info}")
                self.working_config = config.copy()
                break
            else:
                print(f"   ❌ Falhou: {info}")
        
        if self.working_config:
            print(f"\n🎉 CONFIGURAÇÃO ENCONTRADA!")
            print(f"   Nome: {self.working_config['name']}")
            print(f"   Host: {self.working_config['host']}")
            print(f"   Usuário: {self.working_config['user']}")
            print(f"   Senha: {'***' if self.working_config['password'] else '(sem senha)'}")
            
            return True
        else:
            print(f"\n❌ NENHUMA CONFIGURAÇÃO FUNCIONOU")
            print("🔧 Possíveis soluções:")
            print("1. Verifique se o MySQL/XAMPP está rodando")
            print("2. Confirme usuário e senha no phpMyAdmin")
            print("3. Configure manualmente em mysql_config.py")
            
            return False
    
    def update_config_file(self):
        """Atualiza o arquivo de configuração com a configuração que funciona"""
        if not self.working_config:
            return False
        
        config_file = Path("src/mysql_config.py")
        
        try:
            # Lê o arquivo atual
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Atualiza a configuração XAMPP
            new_xampp_config = f"""    'xampp': {{
        'host': '{self.working_config['host']}',
        'port': {self.working_config['port']},
        'user': '{self.working_config['user']}',
        'password': '{self.working_config['password']}',  # {self.working_config['name']}
        'database': 'pryzor_db'
    }}"""
            
            # Substitui a configuração XAMPP no arquivo
            import re
            pattern = r"'xampp': \{[^}]+\}"
            
            if re.search(pattern, content):
                new_content = re.sub(pattern, new_xampp_config, content, flags=re.MULTILINE | re.DOTALL)
                
                # Salva o arquivo atualizado
                with open(config_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print(f"✅ Arquivo mysql_config.py atualizado!")
                return True
            else:
                print("⚠️ Não foi possível atualizar automaticamente")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao atualizar arquivo: {e}")
            return False
    
    def create_database(self):
        """Cria o banco de dados usando a configuração que funciona"""
        if not self.working_config:
            return False
        
        try:
            connection = mysql.connector.connect(
                host=self.working_config['host'],
                port=self.working_config['port'],
                user=self.working_config['user'],
                password=self.working_config['password']
            )
            
            cursor = connection.cursor()
            
            # Verifica se o banco existe
            cursor.execute("SHOW DATABASES")
            databases = [db[0] for db in cursor.fetchall()]
            
            if 'pryzor_db' not in databases:
                cursor.execute("CREATE DATABASE pryzor_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                print("✅ Banco 'pryzor_db' criado com sucesso!")
            else:
                print("ℹ️ Banco 'pryzor_db' já existe")
            
            cursor.close()
            connection.close()
            return True
            
        except Error as e:
            print(f"❌ Erro ao criar banco: {e}")
            return False
    
    def run_complete_setup(self):
        """Executa setup completo"""
        print("🚀 SETUP AUTOMÁTICO MYSQL")
        print("=" * 40)
        
        # Passo 1: Diagnóstico
        if not self.run_diagnostic():
            return False
        
        # Passo 2: Atualizar configuração
        print(f"\n📝 Atualizando configuração...")
        self.update_config_file()
        
        # Passo 3: Criar banco
        print(f"\n🗄️ Criando banco de dados...")
        self.create_database()
        
        # Passo 4: Teste final
        print(f"\n✅ TESTE FINAL...")
        try:
            # Importa a configuração atualizada
            sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
            
            # Recarrega o módulo de configuração
            import importlib
            if 'mysql_config' in sys.modules:
                importlib.reload(sys.modules['mysql_config'])
            
            from database_manager import DatabaseManager
            db = DatabaseManager('xampp')
            stats = db.get_database_stats()
            
            print("🎉 CONFIGURAÇÃO FINALIZADA!")
            print(f"✅ MySQL conectado e funcionando")
            print(f"📊 Banco: {stats['total_games']} jogos, {stats['total_price_records']} registros")
            
            return True
            
        except Exception as e:
            print(f"⚠️ Configuração salva, mas teste final falhou: {e}")
            print("🔧 Execute: python main.py")
            return True  # Configuração foi salva mesmo com erro no teste

def main():
    """Função principal"""
    print("🔧 DIAGNÓSTICO E SETUP AUTOMÁTICO")
    print("=" * 50)
    
    try:
        diagnostic = MySQLDiagnostic()
        
        if diagnostic.run_complete_setup():
            print("\n🎯 PRÓXIMOS PASSOS:")
            print("1. python migrate_to_mysql.py  # Se tiver dados SQLite")
            print("2. python main.py             # Pipeline básico")
            print("3. python query_advanced.py   # Interface completa")
        else:
            print("\n🔧 AJUDA MANUAL:")
            print("1. Verifique se XAMPP/MySQL está rodando")
            print("2. Acesse phpMyAdmin e anote usuário/senha")
            print("3. Edite src/mysql_config.py manualmente")
            
    except KeyboardInterrupt:
        print("\n👋 Setup cancelado")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")

if __name__ == "__main__":
    main()
