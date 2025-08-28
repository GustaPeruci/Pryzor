import pandas as pd
import sqlite3
from datetime import datetime
import os

class RefatoracaoEstruturaNormalizada:
    def __init__(self, csv_wide_path="steamdb_dataset_geral_wide.csv"):
        """Refatora estrutura wide para normalizada."""
        self.csv_wide_path = csv_wide_path
        self.db_path = "steamdb_normalizado.db"
        
    def criar_estrutura_normalizada(self):
        """Cria a nova estrutura de banco normalizada."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de jogos (mestre)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS jogos (
            steam_id TEXT PRIMARY KEY,
            nome_jogo TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Tabela de preços históricos (normalizada)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS precos_historicos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            steam_id TEXT NOT NULL,
            data_coleta DATE NOT NULL,
            ano INTEGER NOT NULL,
            semana INTEGER NOT NULL,
            preco_final DECIMAL(10,2) NOT NULL,
            preco_original DECIMAL(10,2),
            desconto_percentual DECIMAL(5,2) DEFAULT 0,
            em_promocao BOOLEAN DEFAULT FALSE,
            fonte TEXT DEFAULT 'SteamDB',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (steam_id) REFERENCES jogos(steam_id),
            UNIQUE(steam_id, data_coleta)
        )
        """)
        
        # Índices para performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_steam_id ON precos_historicos(steam_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_data_coleta ON precos_historicos(data_coleta)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ano_semana ON precos_historicos(ano, semana)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_promocao ON precos_historicos(em_promocao, desconto_percentual)")
        
        conn.commit()
        conn.close()
        print("✅ Estrutura normalizada criada com sucesso!")
    
    def migrar_dados_wide_para_long(self):
        """Converte dados do formato wide para long (normalizado)."""
        if not os.path.exists(self.csv_wide_path):
            print(f"❌ Arquivo {self.csv_wide_path} não encontrado!")
            return
        
        print("🔄 Iniciando migração de dados...")
        
        # Lê dados no formato wide
        df_wide = pd.read_csv(self.csv_wide_path)
        print(f"📊 Carregados {len(df_wide)} jogos do arquivo wide")
        
        # Transforma para formato long
        df_long = pd.melt(
            df_wide,
            id_vars=['nome_jogo', 'steam_id'],
            var_name='semana_coluna',
            value_name='preco_final'
        )
        
        # Remove valores nulos
        df_long = df_long.dropna(subset=['preco_final'])
        print(f"📈 {len(df_long)} registros de preços após remoção de NULLs")
        
        # Extrai ano e semana das colunas
        df_long['ano'] = df_long['semana_coluna'].str.extract(r'semana_(\d{4})').astype(int)
        df_long['semana'] = df_long['semana_coluna'].str.extract(r'-(\d+)$').astype(int)
        
        # Cria data aproximada baseada no ano e semana
        df_long['data_coleta'] = pd.to_datetime(
            df_long['ano'].astype(str) + '-01-01'
        ) + pd.to_timedelta(df_long['semana'] * 7, unit='D')
        
        # Conecta ao banco e insere dados
        conn = sqlite3.connect(self.db_path)
        
        # Insere jogos únicos
        jogos_unicos = df_wide[['steam_id', 'nome_jogo']].drop_duplicates()
        jogos_unicos.to_sql('jogos', conn, if_exists='replace', index=False)
        print(f"🎮 {len(jogos_unicos)} jogos inseridos na tabela jogos")
        
        # Prepara dados de preços para inserção
        df_precos = df_long[[
            'steam_id', 'data_coleta', 'ano', 'semana', 'preco_final'
        ]].copy()
        
        # Adiciona campos adicionais
        df_precos['preco_original'] = df_precos['preco_final']  # Por enquanto igual
        df_precos['desconto_percentual'] = 0  # Calcular depois se necessário
        df_precos['em_promocao'] = False  # Calcular depois
        df_precos['fonte'] = 'SteamDB'
        
        # Insere preços históricos
        df_precos.to_sql('precos_historicos', conn, if_exists='replace', index=False)
        print(f"💰 {len(df_precos)} registros de preços inseridos")
        
        conn.close()
        print("✅ Migração concluída com sucesso!")
    
    def validar_migracao(self):
        """Valida se a migração foi bem-sucedida."""
        conn = sqlite3.connect(self.db_path)
        
        # Conta registros
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM jogos")
        total_jogos = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM precos_historicos")
        total_precos = cursor.fetchone()[0]
        
        cursor.execute("""
        SELECT COUNT(DISTINCT steam_id) as jogos_com_precos 
        FROM precos_historicos
        """)
        jogos_com_precos = cursor.fetchone()[0]
        
        cursor.execute("""
        SELECT 
            MIN(data_coleta) as data_mais_antiga,
            MAX(data_coleta) as data_mais_recente
        FROM precos_historicos
        """)
        datas = cursor.fetchone()
        
        conn.close()
        
        print("\n📊 VALIDAÇÃO DA MIGRAÇÃO:")
        print(f"🎮 Total de jogos: {total_jogos}")
        print(f"💰 Total de registros de preços: {total_precos}")
        print(f"📈 Jogos com histórico de preços: {jogos_com_precos}")
        print(f"📅 Período: {datas[0]} até {datas[1]}")
        print(f"📊 Média de registros por jogo: {total_precos/total_jogos:.1f}")
    
    def exemplo_consultas(self):
        """Demonstra consultas na nova estrutura."""
        conn = sqlite3.connect(self.db_path)
        
        print("\n🔍 EXEMPLOS DE CONSULTAS NA NOVA ESTRUTURA:")
        
        # 1. Preço atual de um jogo
        query1 = """
        SELECT j.nome_jogo, p.preco_final, p.data_coleta
        FROM jogos j
        JOIN precos_historicos p ON j.steam_id = p.steam_id
        WHERE j.nome_jogo LIKE '%Elden Ring%'
        ORDER BY p.data_coleta DESC
        LIMIT 1
        """
        
        df1 = pd.read_sql_query(query1, conn)
        print("\n1️⃣ Preço atual do Elden Ring:")
        print(df1.to_string(index=False))
        
        # 2. Jogos mais baratos agora
        query2 = """
        WITH precos_atuais AS (
            SELECT 
                p1.steam_id,
                p1.preco_final,
                p1.data_coleta
            FROM precos_historicos p1
            WHERE p1.data_coleta = (
                SELECT MAX(p2.data_coleta) 
                FROM precos_historicos p2 
                WHERE p2.steam_id = p1.steam_id
            )
        )
        SELECT 
            j.nome_jogo,
            pa.preco_final as preco_atual,
            pa.data_coleta
        FROM jogos j
        JOIN precos_atuais pa ON j.steam_id = pa.steam_id
        ORDER BY pa.preco_final ASC
        LIMIT 5
        """
        
        df2 = pd.read_sql_query(query2, conn)
        print("\n2️⃣ Top 5 jogos mais baratos atualmente:")
        print(df2.to_string(index=False))
        
        # 3. Tendência de preços (últimos 3 meses exemplo)
        query3 = """
        SELECT 
            j.nome_jogo,
            AVG(p.preco_final) as preco_medio,
            MIN(p.preco_final) as preco_minimo,
            MAX(p.preco_final) as preco_maximo,
            COUNT(*) as numero_registros
        FROM jogos j
        JOIN precos_historicos p ON j.steam_id = p.steam_id
        WHERE p.data_coleta >= date('now', '-90 days')
        AND j.nome_jogo IN ('Elden Ring', 'The Witcher 3', 'Cyberpunk 2077')
        GROUP BY j.steam_id, j.nome_jogo
        ORDER BY preco_medio DESC
        """
        
        df3 = pd.read_sql_query(query3, conn)
        print("\n3️⃣ Estatísticas dos últimos 90 dias (jogos selecionados):")
        print(df3.to_string(index=False))
        
        conn.close()
    
    def executar_refatoracao_completa(self):
        """Executa todo o processo de refatoração."""
        print("🚀 INICIANDO REFATORAÇÃO PARA ESTRUTURA NORMALIZADA")
        print("=" * 60)
        
        self.criar_estrutura_normalizada()
        self.migrar_dados_wide_para_long()
        self.validar_migracao()
        self.exemplo_consultas()
        
        print(f"\n✅ REFATORAÇÃO CONCLUÍDA!")
        print(f"📁 Banco de dados criado: {self.db_path}")
        print(f"🔧 Use qualquer cliente SQLite para explorar os dados")

def main():
    """Função principal."""
    refatoracao = RefatoracaoEstruturaNormalizada()
    refatoracao.executar_refatoracao_completa()

if __name__ == "__main__":
    main()
