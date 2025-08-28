# Pryzor Backend

API simples para análise de preços de jogos Steam usando Flask e Machine Learning.

## Como rodar

1. Instalar dependências:
```bash
pip install -r requirements.txt
```

2. Configurar MySQL:
```bash
python setup_simple.py
```

3. Rodar API:
```bash
python app.py
```

## Endpoints

- `GET /health` - Status da API
- `GET /api/games` - Lista de jogos
- `GET /api/games/{steam_id}` - Dados de um jogo
- `GET /api/analysis/best-deals` - Melhores ofertas
- `GET /api/analysis/stats` - Estatísticas gerais
- `GET /api/predictions?days=7` - Predições ML
- `GET /api/dashboard` - Dashboard com resumo

## Estrutura

```
pryzor-back/
├── app.py              # API Flask principal
├── setup_simple.py     # Setup do banco
├── requirements.txt    # Dependências
├── src/
│   ├── database_manager.py
│   ├── basic_analyzer.py
│   └── advanced_analyzer.py
└── data/               # CSVs dos jogos
```

## Dados

- 10 jogos monitorados
- 1009 registros históricos
- Modelo ML com 75% de precisão

Desenvolvido como projeto de estudos em Engenharia de Software.
