# 🎮 PRYZOR - Sistema Inteligente de Análise de Preços de Jogos

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://python.org)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-orange.svg)](https://mysql.com)
[![Machine Learning](https://img.shields.io/badge/ML-Scikit--Learn-green.svg)](https://scikit-learn.org)

Sistema avançado de análise preditiva de preços de jogos com Machine Learning, alertas inteligentes e dashboard interativo.

## 🚀 Funcionalidades Principais

### 📊 **Análises Básicas**
- Estatísticas gerais do banco de dados
- Identificação de melhores oportunidades de compra
- Consulta de preços atuais
- Análise específica por jogo
- Geração de gráficos de evolução

### 🤖 **Análises Avançadas com ML**
- **Predições futuras** (7-30 dias) com Random Forest
- **Análise sazonal** - identifica meses com mais promoções
- **Detecção de anomalias** - picos e quedas suspeitas de preço
- **Precisão de 75.7%** (R² = 0.757) com erro médio de R$ 15.06

### 🚨 **Sistema de Alertas Inteligente**
- Monitoramento automático de jogos
- Alertas de quedas significativas de preço
- Notificações de oportunidades históricas
- Dashboard em tempo real

### 📈 **Relatórios e Dashboard**
- Comparação entre múltiplos jogos
- Recomendações personalizadas
- Dashboard executivo com métricas principais
- Exportação para CSV/PNG

## 🛠️ Instalação e Configuração

### Pré-requisitos
- Python 3.12+
- MySQL Server 8.0+

### 1. Instale as dependências
```bash
pip install pandas numpy scikit-learn matplotlib seaborn pymysql mysql-connector-python
```

### 2. Configure o MySQL
```bash
python setup_simple.py
```

### 3. Execute os testes
```bash
python test_mysql.py
```

## 🎯 Como Usar

### Interface Interativa (Recomendado)
```bash
python query_advanced.py
```

### Pipeline Automático
```bash
python main_advanced.py
```

## 📊 Dados Atuais

- **10 jogos** monitorados
- **1.009 registros** de preço
- **Período**: 2014-2024 (11 anos)
- **Jogos inclusos**: Elden Ring, Cyberpunk 2077, The Witcher 3, Hollow Knight, e mais

## 🧠 Machine Learning

### Modelo: Random Forest Regressor
- **Features**: médias móveis, lags, sazonalidade
- **Precisão**: R² = 0.757 (75.7%)
- **Erro médio**: R$ 15.06
- **Predições**: até 30 dias no futuro

### Features Principais
1. `price_ma_7` - Média móvel 7 dias (52.9% importância)
2. `price_ma_30` - Média móvel 30 dias (16.4% importância)
3. `price_lag_30` - Preço de 30 dias atrás (8.8% importância)

## 📁 Estrutura do Projeto

```
Pryzor/
├── 🎯 SISTEMA PRINCIPAL
│   ├── src/                    # Módulos principais
│   │   ├── database_manager.py # Gerenciador MySQL
│   │   ├── advanced_analyzer.py # ML e predições
│   │   ├── basic_analyzer.py   # Análises básicas
│   │   ├── price_alerts.py     # Sistema de alertas
│   │   └── mysql_config.py     # Configurações
│   │
│   ├── main_advanced.py        # Pipeline principal
│   ├── query_advanced.py       # Interface interativa
│   └── data/                   # Dados e resultados
│
├── ⚙️ CONFIGURAÇÃO
│   ├── setup_simple.py         # Setup automático
│   ├── test_mysql.py          # Testes do sistema
│   └── README.md              # Este arquivo
│
└── 📦 ARCHIVE
    ├── old_versions/           # Versões antigas
    ├── troubleshooting/        # Scripts de correção
    ├── migration/              # Ferramentas de migração
    └── docs/                   # Documentação técnica
```

## 🎮 Exemplos de Uso

### Verificar melhores oportunidades
```python
from src.basic_analyzer import BasicAnalyzer

analyzer = BasicAnalyzer()
deals = analyzer.get_best_deals(limit=5)
print(deals)
```

### Fazer predições
```python
from src.advanced_analyzer import AdvancedAnalyzer

analyzer = AdvancedAnalyzer()
predictions = analyzer.predict_future_prices(days=7)
print(predictions)
```

### Sistema de alertas
```python
from src.price_alerts import PriceAlerts

alerts = PriceAlerts()
alerts.add_game_to_monitoring("1234567", threshold=20.0)
alerts.check_all_alerts()
```

## 📈 Resultados Típicos

### Predições Recentes (Exemplo)
- **Dead By Daylight**: -52.3% 🔥 (Grande queda prevista)
- **Grand Theft Auto**: -19.0% 🔥 (Grande queda prevista)  
- **Hollow Knight**: +3.9% 👍 (Compre agora)

### Análise Sazonal
- **Meses com mais promoções**: Março, Junho, Novembro, Dezembro
- **Variação sazonal**: até 40% de diferença entre meses

## 🔧 Solução de Problemas

### MySQL não conecta
```bash
# Verifique se o MySQL está rodando
python archive/troubleshooting/find_mysql_password.py

# Reconfigure se necessário
python setup_simple.py
```

### Dados faltando
```bash
# Execute migração se tiver dados SQLite
python archive/migration/migrate_to_mysql.py
```

## 🏆 Status

✅ **Sistema 100% funcional**  
✅ **MySQL integrado**  
✅ **Machine Learning ativo**  
✅ **Interface completa**  
✅ **Alertas funcionando**  

---

*Desenvolvido com ❤️ para gamers inteligentes que querem economizar!*
