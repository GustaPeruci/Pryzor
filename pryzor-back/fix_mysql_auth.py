"""
Script para corrigir o problema de autenticação MySQL
Altera o plugin de autenticação do usuário root para mysql_native_password
"""

import subprocess
import sys
import os
from pathlib import Path

def fix_mysql_authentication():
    print("🔧 CORREÇÃO DE AUTENTICAÇÃO MYSQL")
    print("=" * 50)
    
    # Solicita senha do root
    password = input("Digite a senha do usuário root do MySQL: ")
    
    # Comando SQL para alterar autenticação
    sql_commands = [
        f"ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '{password}';",
        "FLUSH PRIVILEGES;"
    ]
    
    print("\n🔄 Executando comandos SQL...")
    
    try:
        # Tenta conectar e executar comandos
        for cmd in sql_commands:
            print(f"   Executando: {cmd}")
            
            # Comando mysql via terminal
            mysql_cmd = [
                'mysql',
                '-u', 'root',
                f'-p{password}',
                '-e', cmd
            ]
            
            result = subprocess.run(mysql_cmd, 
                                  capture_output=True, 
                                  text=True,
                                  shell=True)
            
            if result.returncode != 0:
                print(f"❌ Erro: {result.stderr}")
                return False
                
        print("✅ Autenticação corrigida com sucesso!")
        
        # Atualiza configuração
        update_config(password)
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao executar: {e}")
        return False

def update_config(password):
    """Atualiza a configuração do mysql_config.py"""
    try:
        config_path = Path(__file__).parent / "src" / "mysql_config.py"
        
        if config_path.exists():
            # Lê arquivo atual
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Substitui a senha
            content = content.replace("'password': 'root'", f"'password': '{password}'")
            content = content.replace('"password": "root"', f'"password": "{password}"')
            
            # Salva arquivo
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            print(f"✅ Configuração atualizada em {config_path}")
        else:
            print("⚠️ Arquivo de configuração não encontrado")
            
    except Exception as e:
        print(f"❌ Erro ao atualizar configuração: {e}")

def test_connection():
    """Testa a conexão após correção"""
    print("\n🧪 Testando conexão...")
    
    try:
        result = subprocess.run([sys.executable, "test_mysql.py"], 
                              capture_output=True, 
                              text=True,
                              cwd=Path(__file__).parent)
        
        if "✅ Testes passaram: 4/4" in result.stdout:
            print("✅ Conexão funcionando perfeitamente!")
            return True
        else:
            print("⚠️ Ainda há problemas na conexão")
            print("📋 Saída do teste:")
            print(result.stdout)
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

if __name__ == "__main__":
    print("Este script irá:")
    print("1. Alterar a autenticação do MySQL para mysql_native_password")
    print("2. Atualizar a configuração do projeto")
    print("3. Testar a conexão")
    print()
    
    confirm = input("Deseja continuar? (s/n): ").lower()
    if confirm in ['s', 'sim', 'y', 'yes']:
        if fix_mysql_authentication():
            print("\n🎉 Correção concluída!")
            test_connection()
        else:
            print("\n❌ Falha na correção")
            print("\n💡 Alternativas:")
            print("1. Execute manualmente no MySQL:")
            print("   ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'sua_senha';")
            print("   FLUSH PRIVILEGES;")
            print("2. Ou reinstale o MySQL com configurações padrão")
    else:
        print("❌ Operação cancelada")
