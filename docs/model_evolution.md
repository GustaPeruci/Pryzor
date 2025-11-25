# Evolução do Modelo de Machine Learning (Pryzor)

Este documento complementa o resumo do README com detalhes completos do processo iterativo, decisões de arquitetura de ML, comparações de algoritmos e próximos passos.

## 1. Objetivo do Modelo
Prever se um jogo terá desconto **≥20%** nos próximos 30 dias com alta precisão para evitar recomendações erradas de espera.

## 2. Dataset e Validação
- Registros: 725.268 (Steam 2019–2020)
- Jogos: 2.000+
- Split temporal (evitando data leakage):
  - Treino: até 2020-04-01 (531.251 registros)
  - Teste: após 2020-04-01 (194.017 registros)
- Proporção ~73% / 27%

## 3. Pipeline Completo
```
1. Extração de Dados
   ├─ Histórico de preços (Steam API / dumps)
   ├─ Metadados de jogos
   └─ Consolidação em price_history

2. Pré-processamento
   ├─ Limpeza de nulos/inconsistências
   ├─ Conversão de datas (datetime)
   ├─ Criação do target binário (will_have_discount)
   │  └─ Verifica se há desconto ≥20% nos próximos 30 dias
   └─ Seleção de subset temporal

3. Feature Engineering
   ├─ month, quarter
   ├─ day_of_week, is_weekend
   ├─ is_summer_sale, is_winter_sale (janelas de eventos sazonais)
   ├─ final_price
   └─ discount_percent

4. Treinamento
   ├─ Algoritmo principal: RandomForestClassifier
   ├─ Hiperparâmetros:
   │  ├─ n_estimators=200
   │  ├─ max_depth=15
   │  ├─ min_samples_split=20
   │  ├─ min_samples_leaf=10
   │  └─ class_weight='balanced'
   └─ Validação temporal

5. Avaliação
   ├─ Precision, Recall, F1, ROC-AUC
   ├─ Matriz de confusão
   └─ Teste real em 1.000 jogos

6. Deploy
   ├─ Serialização (.pkl)
   ├─ Carregamento lazy na API FastAPI
   └─ Endpoint /api/ml/predict/{appid}
```

## 4. Features Selecionadas
| Feature | Tipo | Motivação | Observações |
|---------|------|-----------|-------------|
| month | Temporal | Sazonalidade mensal | Venda sazonal (ex: férias) |
| quarter | Temporal | Padrões trimestrais | Eventos maiores agrupados |
| final_price | Preço | Cenário atual | Correlaciona com sensibilidade a desconto |
| discount_percent | Desconto | Indicador atual | Forte para continuidade de promoção |
| is_summer_sale | Evento | Grande evento anual | Alta influência |
| is_winter_sale | Evento | Grande evento anual | Alta influência |
| day_of_week | Temporal | Micro padrão semanal | Baixa importância |
| is_weekend | Temporal | Micro padrão semanal | Baixa importância |

Critérios: sem data leakage, calculáveis em produção, diversidade temporal + contexto de preço.

## 5. Métricas (Teste Temporal)
- Precision: 90.46%
- F1-Score: 74.34%
- Recall: 63.09%
- ROC-AUC: 79.45%
- Acurácia real (1.000 jogos): 92.4%
- Acerto classe negativa: 97.7%

### Matriz de Confusão (Resumo)
| Real \ Previsto | Não Desconto | Desconto |
|-----------------|--------------|---------|
| Não Desconto    | 94.808       | 6.086   |
| Desconto        | 36.736       | 56.387  |

Foco deliberado em alta Precision (minimizar falsos positivos). Recall moderado é o trade-off aceito.

## 6. Comparação de Algoritmos
| Algoritmo | F1 | Precision | Recall | ROC-AUC | Tempo Treino | Decisão |
|-----------|----|-----------|--------|---------|--------------|---------|
| Random Forest | 74.34% | 90.46% | 63.09% | 79.45% | ~60s | Escolhido |
| Logistic Regression | 52.18% | 68.12% | 42.55% | 71.23% | ~5s | Rejeitado (baixa F1) |
| Decision Tree | 65.43% | 72.34% | 59.87% | 68.90% | ~8s | Rejeitado (menos robusto) |
| XGBoost | 71.89% | 85.23% | 62.11% | 77.12% | ~120s | Rejeitado (menor precision) |
| MLP (Neural Net) | 58.76% | 70.45% | 50.32% | 69.87% | ~180s | Rejeitado (custo maior) |

Decisão: Random Forest tem melhor combinação de F1 + Precision com custo razoável.

## 7. Evolução de Versões
### v2.0 (Produção)
- Binário (desconto ≥20%)
- 8 features
- Resultado robusto e confiável

### v3.0 (Descartado)
- Tentativa multi-classe (price_increase, stable, small_discount, large_discount)
- F1 ~45%, ROC-AUC inferior
- Complexidade sem ganho prático
- Casos de aumento de preço muito raros (~0.3%)

### v2.1 (Descartado)
- Adição de features de duração (`discount_consecutive_days`, `discount_progress_ratio`, `discount_likely_ending`)
- F1 despencou para 38.11%; Precision 25.67%
- Overfitting a padrões de sequência → avalanche de falsos positivos

## 8. Lições Aprendidas
1. Simplicidade > complexidade em dados desbalanceados
2. Alta Precision aumenta confiança do usuário
3. Multi-classe em classes raras prejudica robustez
4. Features de duração podem induzir viés de continuidade
5. Validação temporal realista é obrigatória para evitar ilusões de desempenho

## 9. Conclusão
Modelo v2.0 permanece como solução ideal: equilíbrio entre desempenho, interpretabilidade e manutenção. Evoluções devem preservar alta precision.

## 10. Próximos Passos Potenciais
1. Regras pós-predição (ex: não recomendar esperar se desconto atual já ≥50%)
2. Expansão de dados (2020–2023) para maior generalização
3. Features de frequência anual de promoções (com cuidado contra leakage)
4. Ensemble conservador (RF + verificador secundário simples)
5. Monitoramento contínuo de drift de sazonalidade

## 11. Riscos e Mitigações
| Risco | Impacto | Mitigação |
|-------|---------|-----------|
| Drift sazonal | Redução de precisão | Re-treino periódico c/ dados novos |
| Desbalanceamento maior | F1 cai | Ajuste de class_weight / técnicas de reamostragem |
| Overfitting em novas features | Perda de generalização | Validação estrita + ablação |
| Mudança na política de promoções | Previsões incoerentes | Log de erros e revisão manual |

## 12. Referências Internas
- Código de treino: `pryzor-back/scripts/02_train_model.py`
- Modelo serializado: `pryzor-back/ml_model/`
- Endpoints ML: `pryzor-back/src/api/`

---
Este documento deve ser atualizado após qualquer mudança estrutural no modelo ou inclusão de novas famílias de features.
