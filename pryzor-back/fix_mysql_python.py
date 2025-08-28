"""
Script alternativo para corrigir autenticação MySQL usando Python
"""

import pymysql
from pathlib import Path

def fix_mysql_with_python():
    print("🔧 CORREÇÃO DE AUTENTICAÇÃO MYSQL (via Python)")
    print("=" * 55)
    
    password = input("Digite a senha atual do usuário root do MySQL: ")
    
    try:
        print("\n🔄 Conectando ao MySQL...")
        
        # Conecta com o plugin atual (pode dar erro, mas vamos tentar)
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password=password,
            charset='utf8mb4'
        )
        
        print("✅ Conectado!")
        
        cursor = connection.cursor()
        
        print("🔄 Alterando plugin de autenticação...")
        
        # Altera o plugin de autenticação
        cursor.execute(f"ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '{password}';")
        cursor.execute("FLUSH PRIVILEGES;")
        
        print("✅ Plugin de autenticação alterado!")
        
        connection.close()
        
        # Atualiza configuração do projeto
        update_config(password)
        
        # Testa conexão
        print("\n🧪 Testando nova conexão...")
        test_new_connection(password)
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        print("\n💡 Possíveis soluções:")
        print("1. Verifique se o MySQL está rodando")
        print("2. Confirme a senha do root")
        print("3. Use o MySQL Workbench para executar:")
        print("   ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'sua_senha';")
        print("   FLUSH PRIVILEGES;")
        return False

def update_config(password):
    """Atualiza mysql_config.py"""
    try:
        config_path = Path("src/mysql_config.py")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Atualiza senha na configuração
        content = content.replace("'password': 'root'", f"'password': '{password}'")
        
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"✅ Configuração atualizada")
        
    except Exception as e:
        print(f"⚠️ Erro ao atualizar config: {e}")

def test_new_connection(password):
    """Testa nova conexão"""
    try:
        # Testa com mysql.connector agora
        import mysql.connector
        
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password=password,
            auth_plugin='mysql_native_password'
        )
        
        if connection.is_connected():
            print("✅ Conexão com mysql.connector funcionando!")
            connection.close()
            return True
            
    except Exception as e:
        print(f"❌ Teste falhou: {e}")
        
    try:
        # Testa com pymysql também
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password=password
        )
        
        print("✅ Conexão com pymysql funcionando!")
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ Teste pymysql falhou: {e}")
        return False

if __name__ == "__main__":
    print("⚠️ IMPORTANTE: Certifique-se que o MySQL Server está rodando!")
    print()
    
    if fix_mysql_with_python():
        print("\n🎉 Correção concluída com sucesso!")
        print("🔄 Execute agora: python test_mysql.py")
    else:
        print("\n❌ Correção falhou")
        print("📋 Use o MySQL Workbench ou phpMyAdmin para executar:")
        print("   ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'sua_senha';")
        print("   FLUSH PRIVILEGES;")
