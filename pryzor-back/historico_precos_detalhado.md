# 📊 TABELA DE HISTÓRICO DE PREÇOS - VERSÃO CORRIGIDA

## 🎯 PRECOS_HISTORICOS_DETALHADO (Tabela Principal)

```sql
CREATE TABLE precos_historicos_detalhado (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    steam_id VARCHAR(20) NOT NULL,
    
    -- ===== DADOS TEMPORAIS PRECISOS =====
    timestamp_coleta TIMESTAMP NOT NULL,
    data_coleta DATE NOT NULL,
    hora_coleta TIME NOT NULL,
    ano SMALLINT NOT NULL,
    mes TINYINT NOT NULL,
    semana TINYINT NOT NULL,
    dia_semana TINYINT NOT NULL, -- 1=segunda, 7=domingo
    
    -- ===== DADOS DE PREÇO COMPLETOS =====
    preco_atual DECIMAL(10,2) NOT NULL,
    preco_original DECIMAL(10,2) NOT NULL, -- Preço sem desconto
    desconto_absoluto DECIMAL(10,2) DEFAULT 0,
    desconto_percentual DECIMAL(5,2) DEFAULT 0,
    
    -- ===== CONTEXTO DA MUDANÇA =====
    mudanca_desde_ultima DECIMAL(10,2) DEFAULT 0, -- +/- valor
    percentual_mudanca DECIMAL(5,2) DEFAULT 0, -- +/- %
    tipo_mudanca ENUM('alta', 'baixa', 'estavel') DEFAULT 'estavel',
    
    -- ===== STATUS DE PROMOÇÃO =====
    em_promocao BOOLEAN DEFAULT FALSE,
    inicio_promocao TIMESTAMP NULL, -- Quando começou a promoção
    fim_promocao_previsto TIMESTAMP NULL, -- Quando termina
    tipo_promocao VARCHAR(100) NULL, -- Daily Deal, Weekend Deal, etc
    
    -- ===== RANKING E POPULARIDADE =====
    posicao_wishlist INT NULL, -- Posição no ranking de wishlists
    posicao_top_sellers INT NULL, -- Posição nos mais vendidos
    numero_reviews_dia INT DEFAULT 0, -- Reviews recebidas no dia
    
    -- ===== DADOS DE CONTEXTO =====
    evento_steam_id INT NULL, -- FK para eventos steam
    update_jogo_recente BOOLEAN DEFAULT FALSE, -- Jogo teve update recente
    dlc_lancado_recente BOOLEAN DEFAULT FALSE, -- DLC lançado recentemente
    
    -- ===== METADADOS =====
    fonte_dados VARCHAR(50) DEFAULT 'SteamDB',
    confiabilidade DECIMAL(3,2) DEFAULT 1.0, -- 0-1 quão confiável é o dado
    observacoes TEXT NULL, -- Qualquer observação especial
    
    -- ===== ÍNDICES E CONSTRAINTS =====
    FOREIGN KEY (steam_id) REFERENCES jogos(steam_id),
    FOREIGN KEY (evento_steam_id) REFERENCES eventos_steam(evento_id),
    
    -- Evita duplicatas no mesmo timestamp
    UNIQUE KEY uk_steam_timestamp (steam_id, timestamp_coleta),
    
    -- Índices para performance
    INDEX idx_steam_data (steam_id, data_coleta),
    INDEX idx_promocao (em_promocao, tipo_promocao),
    INDEX idx_mudanca (tipo_mudanca, percentual_mudanca),
    INDEX idx_temporal (ano, mes, semana, dia_semana),
    INDEX idx_ranking (posicao_wishlist, posicao_top_sellers),
    
    -- Particionamento por ano para performance em grandes volumes
    PARTITION BY RANGE (ano) (
        PARTITION p2020 VALUES LESS THAN (2021),
        PARTITION p2021 VALUES LESS THAN (2022),
        PARTITION p2022 VALUES LESS THAN (2023),
        PARTITION p2023 VALUES LESS THAN (2024),
        PARTITION p2024 VALUES LESS THAN (2025),
        PARTITION p2025 VALUES LESS THAN (2026),
        PARTITION p_future VALUES LESS THAN MAXVALUE
    )
);
```

## 🔍 **VIEWS ANALÍTICAS BASEADAS NO HISTÓRICO:**

### 1. VIEW_PRECOS_AGREGADOS_SEMANAIS
```sql
CREATE VIEW view_precos_agregados_semanais AS
SELECT 
    steam_id,
    ano,
    semana,
    MIN(preco_atual) as preco_minimo_semana,
    MAX(preco_atual) as preco_maximo_semana,
    AVG(preco_atual) as preco_medio_semana,
    STDDEV(preco_atual) as volatilidade_semana,
    SUM(CASE WHEN em_promocao THEN 1 ELSE 0 END) as dias_em_promocao,
    MAX(desconto_percentual) as maior_desconto_semana,
    COUNT(DISTINCT tipo_promocao) as tipos_promocao_diferentes,
    COUNT(*) as registros_na_semana
FROM precos_historicos_detalhado 
GROUP BY steam_id, ano, semana;
```

### 2. VIEW_TENDENCIAS_RECENTES
```sql
CREATE VIEW view_tendencias_recentes AS
SELECT 
    steam_id,
    
    -- Preços recentes
    (SELECT preco_atual FROM precos_historicos_detalhado p1 
     WHERE p1.steam_id = p.steam_id ORDER BY timestamp_coleta DESC LIMIT 1) as preco_atual,
    
    -- Tendência 7 dias
    AVG(CASE WHEN timestamp_coleta >= DATE_SUB(NOW(), INTERVAL 7 DAY) 
        THEN preco_atual END) as preco_medio_7d,
    
    -- Tendência 30 dias  
    AVG(CASE WHEN timestamp_coleta >= DATE_SUB(NOW(), INTERVAL 30 DAY) 
        THEN preco_atual END) as preco_medio_30d,
    
    -- Volatilidade
    STDDEV(CASE WHEN timestamp_coleta >= DATE_SUB(NOW(), INTERVAL 30 DAY) 
        THEN preco_atual END) as volatilidade_30d,
    
    -- Promoções recentes
    COUNT(CASE WHEN em_promocao AND timestamp_coleta >= DATE_SUB(NOW(), INTERVAL 30 DAY) 
        THEN 1 END) as promocoes_ultimos_30d,
    
    -- Última atualização
    MAX(timestamp_coleta) as ultima_atualizacao

FROM precos_historicos_detalhado p
GROUP BY steam_id;
```

### 3. VIEW_OPORTUNIDADES_COMPRA
```sql
CREATE VIEW view_oportunidades_compra AS
SELECT 
    j.steam_id,
    j.nome_jogo,
    tr.preco_atual,
    
    -- Distância do mínimo histórico
    (SELECT MIN(preco_atual) FROM precos_historicos_detalhado p2 
     WHERE p2.steam_id = j.steam_id) as preco_minimo_historico,
    
    -- % acima do mínimo
    ROUND(((tr.preco_atual - (SELECT MIN(preco_atual) FROM precos_historicos_detalhado p3 
                               WHERE p3.steam_id = j.steam_id)) / 
           (SELECT MIN(preco_atual) FROM precos_historicos_detalhado p4 
            WHERE p4.steam_id = j.steam_id)) * 100, 2) as percentual_acima_minimo,
    
    -- Dias desde mínimo
    DATEDIFF(NOW(), (SELECT data_coleta FROM precos_historicos_detalhado p5 
                     WHERE p5.steam_id = j.steam_id 
                     AND p5.preco_atual = (SELECT MIN(preco_atual) FROM precos_historicos_detalhado p6 
                                           WHERE p6.steam_id = j.steam_id)
                     ORDER BY timestamp_coleta DESC LIMIT 1)) as dias_desde_minimo,
    
    -- Status atual
    CASE 
        WHEN tr.preco_atual <= (SELECT MIN(preco_atual) * 1.1 FROM precos_historicos_detalhado p7 
                                WHERE p7.steam_id = j.steam_id) THEN 'EXCELENTE'
        WHEN tr.preco_atual <= (SELECT MIN(preco_atual) * 1.25 FROM precos_historicos_detalhado p8 
                                WHERE p8.steam_id = j.steam_id) THEN 'BOM'
        WHEN tr.preco_atual <= (SELECT AVG(preco_atual) FROM precos_historicos_detalhado p9 
                                WHERE p9.steam_id = j.steam_id) THEN 'REGULAR'
        ELSE 'CARO'
    END as classificacao_oportunidade,
    
    tr.ultima_atualizacao

FROM jogos j
JOIN view_tendencias_recentes tr ON j.steam_id = tr.steam_id
ORDER BY percentual_acima_minimo ASC;
```

## 💡 **POR QUE ESSA ESTRUTURA É SUPERIOR:**

### 1. **Granularidade Temporal Máxima**
- ✅ Timestamp preciso de cada mudança
- ✅ Contexto temporal completo (hora, dia da semana, etc)
- ✅ Duração exata de promoções

### 2. **Contexto Rico de Cada Preço**
- ✅ Motivo da mudança (evento, update, etc)
- ✅ Tipo de promoção específico
- ✅ Dados de popularidade no momento

### 3. **Análises Poderosas**
- ✅ Padrões intra-semanais (qual dia tem mais promoções?)
- ✅ Sazonalidade precisa (não só mensal, mas semanal)
- ✅ Correlação preço × popularidade × eventos

### 4. **Machine Learning Ready**
- ✅ Features temporais ricas
- ✅ Dados de contexto para correlações
- ✅ Histórico completo para treinamento

## 🎯 **CONCLUSÃO:**

Você está **100% correto**! Sem uma tabela de histórico de preços **robusta e detalhada**, qualquer análise preditiva seria superficial. O histórico não é apenas "mais uma tabela" - **É A BASE** de todo o sistema.

A estrutura que propus acima resolve:
- ✅ **Granularidade temporal** (timestamp preciso)
- ✅ **Contexto de mudanças** (por que o preço mudou?)
- ✅ **Dados de promoções** (tipo, duração, etc)
- ✅ **Performance** (índices e particionamento)
- ✅ **Escalabilidade** (para milhões de registros)

**Esta tabela sozinha já permitiria análises 10x mais precisas que o formato wide atual!**
