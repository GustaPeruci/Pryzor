# 🚀 ROADMAP PRÁTICO - COMEÇANDO O PROJETO DO ZERO

## 🎯 VISÃO GERAL: EVOLUIR EM ETAPAS

```
Fase 1: BÁSICO (1-2 semanas) ➜ 
Fase 2: MELHORADO (2-3 semanas) ➜ 
Fase 3: AVANÇADO (1 mês) ➜ 
Fase 4: PROFISSIONAL (ongoing)
```

---

## 📌 FASE 1: COMEÇAR SIMPLES (PRÓXIMOS 7 DIAS)

### ✅ **1.1 - Estrutura Mínima Viável (Dia 1-2)**

#### Criar apenas 2 tabelas:
```sql
-- Tabela 1: Jogos básicos
CREATE TABLE jogos (
    steam_id TEXT PRIMARY KEY,
    nome_jogo TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela 2: Preços simples (formato normalizado)
CREATE TABLE precos_historicos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    steam_id TEXT NOT NULL,
    data_coleta DATE NOT NULL,
    preco DECIMAL(10,2) NOT NULL,
    fonte TEXT DEFAULT 'manual',
    FOREIGN KEY (steam_id) REFERENCES jogos(steam_id),
    UNIQUE(steam_id, data_coleta)
);
```

#### Script de migração atual ➜ novo:
```python
# migrar_dados_simples.py
import pandas as pd
import sqlite3

def migrar_csv_para_db():
    # Lê CSV atual
    df = pd.read_csv('steamdb_dataset_geral_wide.csv')
    
    # Conecta BD
    conn = sqlite3.connect('jogos_precos.db')
    
    # 1. Insere jogos
    jogos = df[['steam_id', 'nome_jogo']].drop_duplicates()
    jogos.to_sql('jogos', conn, if_exists='replace', index=False)
    
    # 2. Transforma wide ➜ long
    df_long = pd.melt(df, id_vars=['steam_id', 'nome_jogo'], 
                      var_name='semana', value_name='preco').dropna()
    
    # 3. Cria data aproximada
    df_long['ano'] = df_long['semana'].str.extract(r'(\d{4})')
    df_long['sem'] = df_long['semana'].str.extract(r'-(\d+)$')
    df_long['data_coleta'] = pd.to_datetime(df_long['ano'] + '-01-01') + \
                            pd.to_timedelta(df_long['sem'].astype(int) * 7, unit='D')
    
    # 4. Salva preços
    precos = df_long[['steam_id', 'data_coleta', 'preco']]
    precos.to_sql('precos_historicos', conn, if_exists='replace', index=False)
    
    conn.close()
    print("✅ Migração simples concluída!")

if __name__ == "__main__":
    migrar_csv_para_db()
```

### ✅ **1.2 - Script de Coleta Melhorado (Dia 3-4)**

#### Atualizar script de processamento:
```python
# processa_steamdb_v2.py (versão BD)
import pandas as pd
import sqlite3
from datetime import datetime

def processar_csv_para_bd(csv_path, steam_id, nome_jogo):
    # Conecta BD
    conn = sqlite3.connect('jogos_precos.db')
    
    # 1. Processa CSV (como antes)
    df = pd.read_csv(csv_path, sep=';')
    # ... processamento existente ...
    
    # 2. Insere/atualiza jogo
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO jogos (steam_id, nome_jogo) 
        VALUES (?, ?)
    """, (steam_id, nome_jogo))
    
    # 3. Insere preços
    for _, row in df_final.iterrows():
        cursor.execute("""
            INSERT OR REPLACE INTO precos_historicos 
            (steam_id, data_coleta, preco) 
            VALUES (?, ?, ?)
        """, (steam_id, row['data'], row['preco']))
    
    conn.commit()
    conn.close()
    print(f"✅ {nome_jogo} processado e salvo no BD!")

# Uso:
processar_csv_para_bd("dados/elden_ring_1245620.csv", "1245620", "Elden Ring")
```

### ✅ **1.3 - Análise Básica (Dia 5-7)**

#### Script de análise simples:
```python
# analise_basica.py
import sqlite3
import pandas as pd

def analise_basica():
    conn = sqlite3.connect('jogos_precos.db')
    
    # 1. Preços atuais
    print("🎮 PREÇOS ATUAIS:")
    query = """
    SELECT j.nome_jogo, p.preco, p.data_coleta
    FROM jogos j
    JOIN (
        SELECT steam_id, MAX(data_coleta) as max_data
        FROM precos_historicos GROUP BY steam_id
    ) latest ON j.steam_id = latest.steam_id
    JOIN precos_historicos p ON latest.steam_id = p.steam_id 
        AND latest.max_data = p.data_coleta
    ORDER BY p.preco ASC
    """
    df_atual = pd.read_sql(query, conn)
    print(df_atual)
    
    # 2. Mínimos históricos
    print("\n💰 MÍNIMOS HISTÓRICOS:")
    query2 = """
    SELECT j.nome_jogo, MIN(p.preco) as menor_preco
    FROM jogos j
    JOIN precos_historicos p ON j.steam_id = p.steam_id
    GROUP BY j.steam_id, j.nome_jogo
    ORDER BY menor_preco ASC
    """
    df_min = pd.read_sql(query2, conn)
    print(df_min)
    
    conn.close()

if __name__ == "__main__":
    analise_basica()
```

---

## 📈 FASE 2: MELHORAR (SEMANAS 2-3)

### ✅ **2.1 - Adicionar Contexto**
- Adicionar campo `em_promocao` na tabela preços
- Detectar promoções automaticamente (queda >20%)
- Calcular volatilidade semanal

### ✅ **2.2 - Primeiro ML Simples**
- Usar apenas últimas 10 semanas
- Prever próxima semana com regressão linear
- Score simples: distância do mínimo histórico

### ✅ **2.3 - Interface Básica**
- Script que mostra top 5 oportunidades
- Relatório semanal em texto

---

## 🎯 FASE 3: AVANÇAR (MÊS 2)

### ✅ **3.1 - Mais Dados**
- Adicionar dados de popularidade (Steam API)
- Eventos Steam (datas de sales)
- Comparação básica outras plataformas

### ✅ **3.2 - ML Melhorado**
- Random Forest com mais features
- Detecção de padrões sazonais
- Confiança nas previsões

---

## 🚀 FASE 4: PROFISSIONALIZAR (ONGOING)

### ✅ **4.1 - Sistema Completo**
- Todas as tabelas propostas
- APIs automatizadas
- Dashboard web

---

## 🎯 **COMEÇAR HOJE - AÇÕES PRÁTICAS:**

### **Próximas 2 horas:**
1. ✅ Executar `migrar_dados_simples.py` 
2. ✅ Verificar se BD foi criado corretamente
3. ✅ Rodar `analise_basica.py` para ver se funciona

### **Próximos 2 dias:**
1. ✅ Atualizar script de processamento para usar BD
2. ✅ Processar mais 2-3 jogos
3. ✅ Criar primeira análise de oportunidades

### **Próxima semana:**
1. ✅ Adicionar detecção automática de promoções
2. ✅ Primeiro algoritmo preditivo simples
3. ✅ Relatório de recomendações básico

---

## 🔥 **PRÓXIMO PASSO IMEDIATO:**

Quer que eu crie os scripts da **Fase 1** agora mesmo? Em 30 minutos você terá:
- ✅ Banco de dados funcionando
- ✅ Migração dos dados atuais
- ✅ Primeira análise básica rodando

**O segredo é começar pequeno e evoluir incremental. Cada fase deve funcionar 100% antes de passar para a próxima!**
