# 📊 ESTRUTURA DE DADOS - SISTEMA DE ANÁLISE PREDITIVA DE PREÇOS

## 🔄 SITUAÇÃO ATUAL

### JOGOS_PRECOS_WIDE (Tabela Existente)
```sql
nome_jogo           VARCHAR(255) PRIMARY KEY
steam_id            VARCHAR(20) 
semana_2014-47      DECIMAL(10,2)
semana_2014-48      DECIMAL(10,2)
...                 (uma coluna para cada semana)
semana_2025-34      DECIMAL(10,2)
```

**Limitações Atuais:**
- ❌ Apenas dados de preço sem contexto
- ❌ Sem informações sobre eventos/promoções
- ❌ Sem dados de popularidade/reviews
- ❌ Sem comparação com outras plataformas
- ❌ Estrutura wide dificulta análises temporais

---

## 🚀 ESTRUTURA PROPOSTA

### 1. JOGOS_METADADOS (Nova - Tabela Mestre)
```sql
steam_id                VARCHAR(20) PRIMARY KEY
nome_jogo              VARCHAR(255) NOT NULL
publisher              VARCHAR(255)
developer              VARCHAR(255)
data_lancamento        DATE
generos                TEXT (JSON array)
classificacao_etaria   VARCHAR(50)
tags                   TEXT (JSON array)
multiplayer            BOOLEAN
dlc_disponivel         BOOLEAN
idiomas                TEXT (JSON array)
preco_lancamento       DECIMAL(10,2)
status_jogo            ENUM('Active','Discontinued','Early Access')
created_at             TIMESTAMP DEFAULT NOW()
updated_at             TIMESTAMP DEFAULT NOW()
```

### 2. JOGOS_POPULARIDADE (Nova - Dados Dinâmicos)
```sql
steam_id                    VARCHAR(20) FK
data_coleta                 DATE
total_reviews               INT
porcentagem_positiva        DECIMAL(5,2)
jogadores_simultaneos_pico  INT
jogadores_simultaneos_atual INT
posicao_top_sellers         INT
numero_wishlists            BIGINT
media_horas_jogadas         DECIMAL(10,2)
review_score               VARCHAR(50)
INDEX(steam_id, data_coleta)
```

### 3. EVENTOS_STEAM (Nova - Calendário de Promoções)
```sql
evento_id       INT PRIMARY KEY AUTO_INCREMENT
nome_evento     VARCHAR(255) (Summer Sale, Winter Sale, etc)
data_inicio     DATE
data_fim        DATE
tipo_evento     ENUM('Sale','Free Weekend','Update','Release')
descricao       TEXT
desconto_medio  DECIMAL(5,2)
global          BOOLEAN
INDEX(data_inicio, data_fim)
```

### 4. JOGOS_EVENTOS (Nova - Participação em Promoções)
```sql
participacao_id        INT PRIMARY KEY AUTO_INCREMENT
steam_id              VARCHAR(20) FK
evento_id             INT FK
desconto_aplicado     DECIMAL(5,2)
preco_com_desconto    DECIMAL(10,2)
data_inicio_desconto  DATE
data_fim_desconto     DATE
promocao_destaque     BOOLEAN
INDEX(steam_id, evento_id)
```

### 5. PRECOS_MULTIPLAS_PLATAFORMAS (Nova - Comparação)
```sql
preco_id        INT PRIMARY KEY AUTO_INCREMENT
steam_id        VARCHAR(20) FK
plataforma      VARCHAR(100) (Epic, GOG, Microsoft Store)
preco           DECIMAL(10,2)
data_coleta     DATE
moeda           VARCHAR(3) DEFAULT 'BRL'
disponivel      BOOLEAN
url_loja        TEXT
INDEX(steam_id, plataforma, data_coleta)
```

### 6. BUNDLES (Nova - Pacotes e Ofertas)
```sql
bundle_id       INT PRIMARY KEY AUTO_INCREMENT
nome_bundle     VARCHAR(255)
plataforma      VARCHAR(100)
preco_bundle    DECIMAL(10,2)
desconto_bundle DECIMAL(5,2)
data_inicio     DATE
data_fim        DATE
ativo           BOOLEAN
INDEX(data_inicio, data_fim, ativo)
```

### 7. JOGOS_BUNDLES (Nova - Relação Jogo-Bundle)
```sql
item_id           INT PRIMARY KEY AUTO_INCREMENT
bundle_id         INT FK
steam_id          VARCHAR(20) FK
preco_individual  DECIMAL(10,2)
jogo_principal    BOOLEAN
INDEX(bundle_id, steam_id)
```

### 8. DLCS (Nova - Expansões e DLCs)
```sql
dlc_id               VARCHAR(20) PRIMARY KEY
steam_id_jogo_base   VARCHAR(20) FK
nome_dlc             VARCHAR(255)
preco_dlc            DECIMAL(10,2)
data_lancamento_dlc  DATE
tipo_dlc             ENUM('Expansion','Cosmetic','Season Pass','Map Pack')
incluido_deluxe      BOOLEAN
INDEX(steam_id_jogo_base)
```

### 9. DADOS_ECONOMICOS (Nova - Contexto Econômico)
```sql
data                        DATE PRIMARY KEY
taxa_cambio_usd_brl        DECIMAL(8,4)
inflacao_mensal_br         DECIMAL(5,2)
indice_confianca_consumidor DECIMAL(5,2)
feriado_nacional           BOOLEAN
black_friday               BOOLEAN
mes_pagamento_13           BOOLEAN
semana_mes                 TINYINT (1-4)
INDEX(data)
```

### 10. UPDATES_JOGOS (Nova - Histórico de Atualizações)
```sql
update_id        INT PRIMARY KEY AUTO_INCREMENT
steam_id         VARCHAR(20) FK
data_update      DATE
versao           VARCHAR(50)
tipo_update      ENUM('Bugfix','Content','Major Update','DLC')
descricao        TEXT
update_gratuito  BOOLEAN
tamanho_mb       DECIMAL(10,2)
INDEX(steam_id, data_update)
```

### 11. SUBSCRIPTIONS (Nova - Game Pass, PS Plus, etc)
```sql
subscription_id  INT PRIMARY KEY AUTO_INCREMENT
steam_id         VARCHAR(20) FK
servico          VARCHAR(100) (Game Pass, PS Plus, EA Play)
data_inclusao    DATE
data_remocao     DATE NULL
ativo            BOOLEAN
tier             VARCHAR(50) (Basic, Premium, Ultimate)
INDEX(steam_id, servico, ativo)
```

### 12. ANALISES_PREDITIVAS (Nova - Cache de Análises)
```sql
analise_id         INT PRIMARY KEY AUTO_INCREMENT
steam_id           VARCHAR(20) FK
data_analise       TIMESTAMP
score_compra       DECIMAL(5,2) (0-100)
recomendacao       ENUM('Compre Agora','Bom Momento','Aguarde','Evite')
preco_previsto     DECIMAL(10,2)
confianca_previsao DECIMAL(3,2) (0-1)
fatores_decisao    JSON
modelo_usado       VARCHAR(100)
INDEX(steam_id, data_analise)
INDEX(score_compra DESC)
```

---

## 📊 VIEWS E TABELAS DERIVADAS

### VIEW_TENDENCIAS_MENSAIS
```sql
CREATE VIEW VIEW_TENDENCIAS_MENSAIS AS
SELECT 
    steam_id,
    YEAR(data_coleta) as ano,
    MONTH(data_coleta) as mes,
    AVG(preco) as preco_medio_mensal,
    MIN(preco) as preco_minimo_mensal,
    MAX(preco) as preco_maximo_mensal,
    STDDEV(preco) as volatilidade_mensal,
    COUNT(DISTINCT evento_id) as numero_promocoes
FROM JOGOS_PRECOS_WIDE 
LEFT JOIN JOGOS_EVENTOS USING(steam_id)
GROUP BY steam_id, ano, mes;
```

### VIEW_RANKING_OPORTUNIDADES
```sql
CREATE VIEW VIEW_RANKING_OPORTUNIDADES AS
SELECT 
    jm.steam_id,
    jm.nome_jogo,
    ap.score_compra as score_oportunidade,
    -- Preço atual seria a última semana disponível
    ap.preco_previsto,
    ap.recomendacao,
    ap.data_analise as ultima_atualizacao
FROM JOGOS_METADADOS jm
LEFT JOIN ANALISES_PREDITIVAS ap ON jm.steam_id = ap.steam_id
WHERE ap.data_analise = (
    SELECT MAX(data_analise) 
    FROM ANALISES_PREDITIVAS ap2 
    WHERE ap2.steam_id = jm.steam_id
)
ORDER BY ap.score_compra DESC;
```

---

## 🔄 MIGRAÇÃO E IMPLEMENTAÇÃO

### Fase 1: Estrutura Base
1. ✅ Manter `JOGOS_PRECOS_WIDE` atual
2. 🆕 Criar `JOGOS_METADADOS`
3. 🆕 Criar `EVENTOS_STEAM` com dados históricos

### Fase 2: Dados de Mercado
1. 🆕 Implementar `JOGOS_POPULARIDADE`
2. 🆕 Implementar `PRECOS_MULTIPLAS_PLATAFORMAS`
3. 🆕 Implementar `DADOS_ECONOMICOS`

### Fase 3: Funcionalidades Avançadas
1. 🆕 Implementar sistema de bundles
2. 🆕 Implementar tracking de DLCs
3. 🆕 Implementar cache de análises

### Fase 4: Otimização
1. 📊 Criar views otimizadas
2. 🚀 Implementar índices de performance
3. 🔄 Automação de coleta de dados

---

## 🎯 BENEFÍCIOS DA NOVA ESTRUTURA

### Para Análise Preditiva:
- ✅ **Contexto Rico**: Eventos, popularidade, concorrência
- ✅ **Sazonalidade**: Dados econômicos e feriados
- ✅ **Precisão**: Múltiplas fontes de dados
- ✅ **Confiabilidade**: Cache de análises anteriores

### Para Performance:
- ✅ **Consultas Rápidas**: Índices otimizados
- ✅ **Escalabilidade**: Estrutura normalizada
- ✅ **Manutenibilidade**: Separação de responsabilidades
- ✅ **Flexibilidade**: Fácil adição de novos dados

### Para Usuário Final:
- ✅ **Recomendações Precisas**: Mais dados = melhor análise
- ✅ **Transparência**: Fatores de decisão explícitos
- ✅ **Comparação**: Preços em múltiplas plataformas
- ✅ **Timing**: Alertas baseados em eventos conhecidos
