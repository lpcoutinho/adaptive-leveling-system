# Fase 6: Detecção de Gaps e Análise de Prontidão

## Contexto

Este plano implementa a **Fase 6** do Adaptive Leveling System: Detecção de Gaps e Análise de Prontidão.

Após o aluno completar o quiz (Fase 5), temos as respostas corrigidas com scores individuais. O objetivo desta fase é **analisar esses scores** à luz do grafo de conhecimento (Fase 3) para:

1. Calcular um score de prontidão geral ponderado pela importância dos pré-requisitos.
2. Identificar gaps de conhecimento (pré-requisitos com score baixo).
3. Classificar o nível de prontidão do aluno (Ready, Needs Review, Not Ready).

**Objetivo:** Transformar respostas brutas do quiz em um diagnóstico educacional estruturado e acionável.

---

## Estrutura de Arquivos Planejada

```
backend/
├── api/
│   ├── routes/
│   │   └── readiness.py               # POST /analyze, GET /{session_id}
│   └── schemas/
│       └── readiness.py               # Schemas de request/response
│
├── domain/
│   └── models/
│       └── readiness.py               # ReadinessResult, GapAnalysis, ReadinessLevel
│
├── infrastructure/
│   └── repository/
│       └── readiness_repository.py    # Salvar/buscar resultados
│
└── services/
    └── gap_detection_service.py       # analyze_gaps, scoring, thresholds

frontend/
└── app/
    ├── components/
    │   ├── readiness_card.py          # Score gauge + level badge
    │   └── gaps_list.py               # Gaps priorizados
    └── pages/
        └── readiness.py               # Dashboard de prontidão

tests/
├── test_gap_detection_service.py      # Scoring, thresholds, priorização
└── fixtures/
    └── readiness_fixtures.py          # Mock results
```

---

## Fluxo de Processamento (Arquitetura)

1. **Entrada:** `session_id` do quiz finalizado (Fase 5) + `pdf_id` do grafo de conhecimento (Fase 3).
2. **Cálculo do Score por Pré-requisito:** Média dos scores das questões daquele pré-requisito.
3. **Cálculo do Score Geral:** Média ponderada: `Critical * 3 + Important * 2 + Helpful * 1`.
4. **Classificação de Prontidão:** Score ≥ 80% → **Ready** | 50-79% → **Needs Review** | < 50% → **Not Ready**.
5. **Identificação de Gaps:** Pré-requisitos com score < 60% são marcados como gaps.
6. **Identificação de Forças (Strengths):** Pré-requisitos com score ≥ 80% são marcados como forças.
7. **Priorização:** Gaps ordenados por importância (Critical first) + score (menor primeiro) + dependência.
8. **Persistência:** Resultado salvo no PostgreSQL e cacheado no Valkey (TTL 7d).

---

## Tarefas Sequenciais

### Tarefa 1: Modelagem de Domínio

- Criar `backend/domain/models/readiness.py`:
  - `ReadinessLevel` enum (READY, NEEDS_REVIEW, NOT_READY)
  - `GapAnalysis` com: prerequisite_name, score, importance, is_gap, is_strength
  - `ReadinessResult` com: overall_score, level, gaps[], strengths[], created_at

### Tarefa 2: Serviço de Detecção de Gaps

- Implementar `gap_detection_service.py`:
  - `analyze_gaps(session_id, pdf_id)` → `ReadinessResult`.
  - `_calculate_scores(quiz_answers, knowledge_graph)` → scores por pré-requisito.
  - `_weighted_scoring(scores, knowledge_graph)` → score geral ponderado.
  - `_classify_readiness(overall_score)` → ReadinessLevel.
  - `_identify_gaps_and_strengths(scores)` → gaps + strengths.
  - `_prioritize_gaps(gaps, knowledge_graph)` → gaps ordenados.

### Tarefa 3: Cache e Repositório

- `ReadinessRepository`: salvar/buscar resultados no PostgreSQL.
- Idempotência: se análise já existe para a sessão, retornar sem recalcular.

### Tarefa 4: Rotas FastAPI

- `POST /api/v1/readiness/analyze` → analisa sessão.
- `GET /api/v1/readiness/{session_id}` → recupera resultado.

### Tarefa 5: Frontend

- Criar `frontend/app/pages/readiness.py`.
- Componente `ReadinessCard`: gauge visual do score + badge do nível.
- Componente `GapsList`: gaps priorizados com score e importância.
- Seção de "Forças" (strengths) para feedback positivo.
- Botões: "Ver Plano de Nivelamento" (Fase 7), "Refazer Quiz" (Fase 5).

### Tarefa 6: Testes

- Testar cálculo de score ponderado (pesos 3x, 2x, 1x).
- Testar thresholds de classificação (Ready, Needs Review, Not Ready).
- Testar ordenação de gaps por importância + score + dependência.
- Testar idempotência (mesma sessão não recalcula).

---

## Critérios de Aceitação

- [ ] Score geral calculado com pesos corretos (Critical 3x, Important 2x, Helpful 1x).
- [ ] Classificação de prontidão correta (Ready ≥ 80%, Needs Review 50-79%, Not Ready < 50%).
- [ ] Gaps identificados (score < 60%) e priorizados por severidade.
- [ ] Strengths identificados (score ≥ 80%) destacados positivamente.
- [ ] Frontend exibe gauge, gaps e strengths.
- [ ] Cobertura de testes > 80%.

---

## Decisões Técnicas

1. **Pesos Diferenciados:** Critical (3x) reflete que gaps em conceitos fundamentais impedem o progresso; Helpful (1x) indica conhecimento complementar.
2. **Threshold Duplo:** Gap < 60% e Strength ≥ 80% criam uma zona neutra (60-79%) onde o aluno tem conhecimento parcial mas precisa de revisão.
3. **Ordenação por Dependência:** Gaps são ordenados considerando o grafo de conhecimento — conceitos base vêm antes dos derivados.
4. **Feedback Positivo:** Destacar strengths mantém o engajamento e mostra ao aluno o que ele já domina.
