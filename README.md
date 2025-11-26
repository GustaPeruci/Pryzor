# Pryzor - Previsão de Descontos na Steam

> **Portfólio de Projeto - Engenharia de Software**  
> Sistema inteligente que recomenda se vale esperar uma promoção

## 1. Visão Geral
O Pryzor analisa histórico de preços da Steam e prevê se um jogo terá desconto ≥20% nos próximos 30 dias. Resultado: recomendação objetiva (comprar agora ou esperar). Foco em alta precisão para evitar falsos alarmes e aumentar confiança do usuário.

## 2. Arquitetura
Arquitetura client-server: frontend (React + TypeScript) e backend (FastAPI + Python + MySQL + modelo Random Forest). Modelo carregado lazy na API.

```mermaid
flowchart LR
  U[Usuário] --> FE[Frontend]
  FE --> BE[Backend]
  BE --> DB[(MySQL)]
  BE --> ML[Modelo ML]
  ML --> DB
```

Banco (simplificado): `games(appid PK, name, releasedate, freetoplay)` e `price_history(id PK, appid FK, date, final_price, initial_price, discount)`.

## 3. Funcionalidades & Casos de Uso
- Busca e listagem de jogos
- Histórico de preços e estado atual
- Previsão individual e em lote (≥20% em 30 dias)
- Recomendação de compra ou espera
- Estatísticas gerais do sistema
- Setup/importação inicial de dados

## 4. Quick Start

### Backend (Python 3.11+)
```bash
# 1. Configurar ambiente
cd pryzor-back
python -m venv venv
venv\Scripts\activate  # Windows (Linux/Mac: source venv/bin/activate)
pip install -r requirements.txt

# 2. Configurar banco de dados MySQL
# Criar arquivo .env (copiar de .env.example):
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=sua_senha
MYSQL_DATABASE=steam_pryzor
DATABASE_URL=mysql+pymysql://root:sua_senha@localhost:3306/steam_pryzor

# 3. Criar schema do banco
mysql -u root -p < setup_database.sql

# 4. (Opcional) Importar dataset
python import_dataset.py

# 5. Iniciar API
python src/main.py
```
📖 **API Docs**: http://localhost:8000/docs

### Frontend (Node.js 16+)
```bash
cd pryzor-front
npm install
npm run dev
```
**Interface**: http://localhost:5173

## 5. Principais Endpoints

| Categoria | Método | Endpoint | Descrição |
|-----------|--------|----------|------------|
| Sistema | GET | `/health` | Health check |
| Sistema | GET | `/api/stats` | Estatísticas gerais |
| Jogos | GET | `/api/games` | Lista jogos (filtros: `?search=`, `?limit=`, `?offset=`) |
| Jogos | GET | `/api/games/{appid}` | Detalhes de um jogo |
| ML | GET | `/api/ml/info` | Informações do modelo |
| ML | GET | `/api/ml/predict/{appid}` | Predição individual |
| ML | POST | `/api/ml/predict/batch` | Predição em lote (até 50 jogos) |

### Exemplo de Resposta (Predição)
```json
{
  "appid": 271590,
  "game_name": "Grand Theft Auto V",
  "will_have_discount": true,
  "probability": 0.78,
  "confidence": 0.56,
  "recommendation": "AGUARDAR - Alta probabilidade de desconto melhor em breve",
  "current_price": 119.90,
  "reasoning": "Modelo prevê desconto ≥20% nos próximos 30 dias com 78% de probabilidade"
}
```

## 6. Modelo de ML (Resumo)
Objetivo: prever se haverá desconto ≥20% em 30 dias. 
Features (8): month, quarter, final_price, discount_percent, is_summer_sale, is_winter_sale, day_of_week, is_weekend.
Validação temporal (cut 2020-04-01). Métricas (teste): Precision 90.46%, F1 74.34%, Recall 63.09%, ROC-AUC 79.45%. Alta precision → poucas recomendações erradas de “esperar”. Random Forest escolhido por melhor equilíbrio entre desempenho, interpretabilidade e tempo de treino.

Mais detalhes (pipeline completo, histórico de versões v2.0 / v3.0 / v2.1, comparação de algoritmos, lições aprendidas): ver `docs/model_evolution.md`.

## 7. Stack Tecnológica

### Backend
| Tecnologia | Versão | Uso |
|------------|--------|-----|
| Python | 3.11 | Linguagem principal |
| FastAPI | latest | Framework web assíncrono |
| scikit-learn | latest | Random Forest Classifier |
| pandas | latest | Manipulação de dados |
| MySQL | 8.0+ | Banco de dados relacional |
| pymysql | latest | Driver MySQL para Python |
| pytest | latest | Framework de testes |

### Frontend
| Tecnologia | Versão | Uso |
|------------|--------|-----|
| React | 19 | Biblioteca UI |
| TypeScript | latest | Superset JavaScript tipado |
| Vite | latest | Build tool |
| Axios | latest | Cliente HTTP |
| Jest | latest | Framework de testes |
| React Testing Library | latest | Utilitários de teste |

### DevOps & Infra
- **CI/CD**: GitHub Actions
- **Deploy**: Render (backend e frontend)
- **Versionamento**: Git/GitHub
- **Monorepo**: Separação backend/frontend

## 8. Desenvolvimento & Testes
Abordagem incremental orientada a testes. Cobertura crítica (backend ~33%, frontend ~58%) garantindo refatoração segura.
Backend:
```bash
cd pryzor-back
pytest --cov=src
```
Frontend:
```bash
cd pryzor-front
npm test -- --coverage
```
Relatórios locais em `reports/`. CI executa testes em cada push. Não foi TDD estrito em todas as features, mas princípios de validação contínua foram seguidos.

## 9. CI/CD & Deploy
GitHub Actions: testes + cobertura + deploy automático (Render) na branch `main` para cada repositório (backend e frontend). Ao passar nos testes, serviço é atualizado sem intervenção manual.

**Workflows configurados:**
- Backend: `.github/workflows/ci-cd.yml` em [pryzor-back](https://github.com/GustaPeruci/pryzor-back)
- Frontend: `.github/workflows/ci-cd.yml` em [pryzor-front](https://github.com/GustaPeruci/pryzor-front)

## 10. Estrutura do Repositório
```
pryzor/
├── pryzor-back/       # API + ML
│   ├── src/           # Código da API
│   ├── scripts/       # Treino / utilidades
│   ├── ml_model/      # Modelo (.pkl)
│   ├── tests/         # Testes pytest
│   └── docs/          # Doc técnica específica
├── pryzor-front/      # Interface React
│   └── src/           # Componentes e serviços
├── docs/              # Documentação aprofundada (ML evolução)
├── CONTEXT.md
├── COPILOT_PROMPT.md
└── README.md
```

## 11. Contexto Acadêmico
Projeto de portfólio demonstrando aplicação real de ML com validação temporal correta, engenharia de software limpa, testes automatizados e documentação reprodutível. Ênfase em confiabilidade de recomendação (precision alta) e transparência metodológica.

### Destaques Técnicos
- ✅ Validação temporal adequada (evitando data leakage)
- ✅ Pipeline ML completo (ETL → Feature Engineering → Treino → Deploy)
- ✅ Testes automatizados (backend + frontend)
- ✅ CI/CD com GitHub Actions
- ✅ Arquitetura escalável e documentada

## 12. Licença & Ética
Uso acadêmico. Dados públicos/sintéticos, sem informações pessoais. Conformidade com princípios de privacidade (LGPD). Evolução futura: revisão contínua de políticas.

## 13. Autor
**Gustavo Peruci**  
🔗 GitHub: [@GustaPeruci](https://github.com/GustaPeruci)  
📧 Email: gustavosss06@gmail.com  
📅 Portfólio de Projeto - Engenharia de Software - 2025

## 14. Links & Recursos

### 🔗 Repositórios
- [📦 Monorepo Principal](https://github.com/GustaPeruci/Pryzor)
- [⚛️ Frontend (React)](https://github.com/GustaPeruci/pryzor-front)
- [🐍 Backend (FastAPI)](https://github.com/GustaPeruci/pryzor-back)

### 🚀 Demonstração
- [🌐 App em Produção](https://pryzor-front.onrender.com/)
- [[📖 API Docs (local)](https://pryzor-back.onrender.com/docs)
- [🎥 Vídeo Pitch](youtube.com/watch?v=Pw0WEkMKU48&feature=youtu.be)

### 📚 Documentação Adicional
- [🧠 Evolução do Modelo ML](./docs/model_evolution.md) - Histórico completo, experimentos rejeitados (v3.0, v2.1), comparação de algoritmos

---

<div align="center">

**⭐ Se este projeto foi útil, considere dar uma estrela no GitHub!**

*Desenvolvido com foco em qualidade, reprodutibilidade e boas práticas de engenharia de software*

</div>
