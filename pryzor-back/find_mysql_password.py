"""
Script para testar diferentes senhas comuns do MySQL
"""

import pymysql
import mysql.connector

def test_common_passwords():
    print("🔍 TESTANDO SENHAS COMUNS DO MYSQL")
    print("=" * 40)
    
    # Senhas comuns para testar
    common_passwords = [
        '',  # Sem senha
        'root',
        'mysql',
        'password',
        '123456',
        'admin',
        '1234'
    ]
    
    print("Testando senhas comuns...")
    
    for password in common_passwords:
        print(f"\n🔑 Testando senha: {'(vazia)' if password == '' else password}")
        
        # Teste com pymysql
        try:
            connection = pymysql.connect(
                host='localhost',
                user='root',
                password=password,
                charset='utf8mb4'
            )
            
            print(f"✅ SUCESSO com PyMySQL! Senha: {'(vazia)' if password == '' else password}")
            connection.close()
            return password
            
        except Exception as e:
            print(f"   ❌ PyMySQL falhou: {str(e)[:50]}...")
        
        # Teste com mysql.connector
        try:
            connection = mysql.connector.connect(
                host='localhost',
                user='root',
                password=password
            )
            
            print(f"✅ SUCESSO com MySQL Connector! Senha: {'(vazia)' if password == '' else password}")
            connection.close()
            return password
            
        except Exception as e:
            print(f"   ❌ MySQL Connector falhou: {str(e)[:50]}...")
    
    print("\n❌ Nenhuma senha comum funcionou")
    return None

def manual_password_test():
    print("\n🔧 TESTE MANUAL DE SENHA")
    print("=" * 30)
    
    while True:
        password = input("Digite a senha do MySQL (ou 'quit' para sair): ")
        
        if password.lower() == 'quit':
            break
            
        try:
            connection = pymysql.connect(
                host='localhost',
                user='root',
                password=password,
                charset='utf8mb4'
            )
            
            print(f"✅ SUCESSO! Senha correta: {password}")
            connection.close()
            return password
            
        except Exception as e:
            print(f"❌ Falhou: {e}")
    
    return None

if __name__ == "__main__":
    print("🚀 DIAGNÓSTICO DE SENHA MYSQL")
    print("Este script vai tentar descobrir a senha correta do MySQL")
    print()
    
    # Testa senhas comuns
    correct_password = test_common_passwords()
    
    if not correct_password:
        # Permite teste manual
        correct_password = manual_password_test()
    
    if correct_password is not None:
        print(f"\n🎉 Senha encontrada: {'(vazia)' if correct_password == '' else correct_password}")
        print("Agora você pode usar esta senha no script de correção!")
    else:
        print("\n❌ Não foi possível encontrar a senha")
        print("💡 Verifique:")
        print("1. Se o MySQL está rodando (Services.msc → MySQL)")
        print("2. Se você lembra da senha que definiu na instalação")
        print("3. Considere reinstalar o MySQL se necessário")
