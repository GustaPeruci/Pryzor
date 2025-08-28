# 🚀 **Pryzor API - Documentação Completa**

API REST para análise de preços de jogos Steam com Machine Learning.

## 📋 **Visão Geral**

- **Versão**: 1.0.0
- **Base URL**: `http://127.0.0.1:5000`
- **Formato**: JSON
- **CORS**: Habilitado para React frontend

## 🏃‍♂️ **Quick Start**

```bash
# 1. Instalar dependências
pip install Flask Flask-CORS PyMySQL python-dotenv

# 2. Executar API
python run_api.py

# 3. Testar
curl http://127.0.0.1:5000/health
```

## 🎯 **Endpoints Principais**

### **Sistema**
- `GET /health` - Status da API
- `GET /api/info` - Informações da API

### **Jogos**
- `GET /api/games` - Lista todos os jogos
- `GET /api/games/{id}` - Dados de um jogo específico
- `GET /api/games/search?q={termo}` - Buscar jogos

### **Análises**
- `GET /api/analysis/basic/stats` - Estatísticas básicas
- `GET /api/analysis/basic/best-deals` - Melhores ofertas
- `GET /api/analysis/advanced/seasonal` - Análise sazonal
- `GET /api/analysis/advanced/anomalies` - Detectar anomalias

### **Predições ML**
- `GET /api/predictions?days=7` - Predições para todos os jogos
- `GET /api/predictions/{steam_id}` - Predição específica
- `GET /api/predictions/model/info` - Info do modelo ML

### **Alertas**
- `GET /api/alerts` - Listar alertas
- `POST /api/alerts` - Criar alerta
- `DELETE /api/alerts/{id}` - Remover alerta
- `POST /api/alerts/check` - Verificar alertas

### **Dashboard**
- `GET /api/dashboard` - Visão geral completa
- `GET /api/dashboard/charts/price-trends` - Gráficos de tendências
- `GET /api/dashboard/charts/predictions-summary` - Resumo predições

## 📊 **Exemplos de Uso**

### **1. Buscar Jogos**
```bash
curl "http://127.0.0.1:5000/api/games?page=1&limit=10"
```

**Resposta:**
```json
{
  "success": true,
  "data": {
    "games": [...],
    "pagination": {
      "page": 1,
      "limit": 10,
      "total": 10,
      "pages": 1
    }
  },
  "message": "Lista de jogos",
  "timestamp": "2024-08-28T10:30:00"
}
```

### **2. Melhores Ofertas**
```bash
curl "http://127.0.0.1:5000/api/analysis/basic/best-deals?limit=5"
```

### **3. Predições ML**
```bash
curl "http://127.0.0.1:5000/api/predictions?days=7"
```

**Resposta:**
```json
{
  "success": true,
  "data": [
    {
      "game_name": "Counter-Strike 2",
      "current_price": 29.99,
      "predicted_price": 24.99,
      "trend_percent": -16.7,
      "recommendation": "🔥 AGUARDE! Grande queda prevista",
      "confidence": "high"
    }
  ]
}
```

### **4. Criar Alerta**
```bash
curl -X POST "http://127.0.0.1:5000/api/alerts" \
  -H "Content-Type: application/json" \
  -d '{
    "game_name": "Cyberpunk 2077",
    "steam_id": "1091500",
    "target_price": 25.00,
    "alert_type": "price_drop"
  }'
```

## 🎨 **Estrutura de Resposta**

Todas as respostas seguem o padrão:

```json
{
  "success": boolean,
  "data": any,
  "message": string,
  "timestamp": string,
  "error_code": string // apenas em erros
}
```

## 🔧 **Parâmetros Comuns**

### **Paginação**
- `page`: Número da página (padrão: 1)
- `limit`: Itens por página (padrão: 20, máximo: 100)

### **Filtros**
- `q`: Termo de busca
- `days`: Período em dias (1-30)
- `months`: Período em meses (1-24)

## 🤖 **Machine Learning**

### **Modelo**
- **Tipo**: Random Forest Regressor
- **Acurácia**: 75.7%
- **Features**: Médias móveis, lags, volatilidade
- **Dados**: 10 jogos, 1009 registros (2014-2024)

### **Recomendações**
- 🔥 **AGUARDE**: Queda > 15%
- ⏳ **Espere**: Queda 5-15%
- 👍 **Compre**: Alta > 5%
- 🤔 **Estável**: ±5%

## 🚨 **Códigos de Erro**

- `400`: Bad Request - Parâmetros inválidos
- `404`: Not Found - Recurso não encontrado
- `500`: Internal Server Error - Erro interno

## 🎯 **Para o Frontend React**

A API está preparada para React com:
- ✅ CORS configurado
- ✅ Respostas padronizadas
- ✅ Paginação
- ✅ Filtros e busca
- ✅ Dados para gráficos
- ✅ Real-time via polling

### **Exemplo React Hook**
```typescript
const useGames = () => {
  const [games, setGames] = useState([]);
  
  useEffect(() => {
    fetch('http://127.0.0.1:5000/api/games')
      .then(res => res.json())
      .then(data => setGames(data.data.games));
  }, []);
  
  return games;
};
```

## 🔄 **Próximos Passos**

1. ✅ **API Flask** - Concluída
2. 🔄 **React Frontend** - Próximo
3. 🔄 **Autenticação** - Futuro
4. 🔄 **WebSockets** - Futuro
5. 🔄 **Cache Redis** - Futuro

---

**Status**: 🟢 API 100% funcional  
**Accuracia ML**: 75.7%  
**Endpoints**: 15+ rotas  
**Pronto para**: React Frontend
