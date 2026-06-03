# Fase 7: Geração de Conteúdo de Nivelamento

## Contexto

Este plano implementa a **Fase 7** do Adaptive Leveling System: Geração de Conteúdo de Nivelamento.

Com os gaps identificados e priorizados na Fase 6, o objetivo desta fase é **gerar conteúdo educacional personalizado** para cada gap. Cada gap recebe uma explicação contextualizada com a disciplina alvo (Cálculo I), exemplos práticos e exercícios de fixação, organizados em um plano de estudo sequencial.

**Objetivo:** Produzir material de nivelamento sob medida para o aluno, fechando seus gaps de conhecimento de forma eficiente e pedagogicamente estruturada.

---

## Estrutura de Arquivos Planejada

```
backend/
├── api/
│   ├── routes/
│   │   └── leveling.py                # POST /generate, GET /plan/{plan_id}
│   └── schemas/
│       └── leveling.py                # Schemas para plano de nivelamento
│
├── domain/
│   └── models/
│       └── leveling.py                # GapExplanation, LevelingPlan
│
├── llm/
│   └── prompts/
│       └── leveling_generator_v1.txt  # Prompt para conteúdo personalizado
│
├── infrastructure/
│   ├── cache/
│   │   └── leveling_cache.py          # Valkey cache (TTL 7d)
│   └── repository/
│       └── leveling_repository.py     # DB operations
│
└── services/
    └── leveling_service.py            # generate_leveling_content, create_study_order

frontend/
└── app/
    ├── components/
    │   ├── gap_explanation.py         # Card: why → explanation → example → exercise
    │   └── study_plan.py              # Timeline de estudos
    └── pages/
        └── leveling.py                # Plano de nivelamento completo

tests/
├── test_leveling_service.py           # Geração com MockProvider
└── fixtures/
    └── leveling_fixtures.py           # Mock content
```

---

## Fluxo de Processamento (Arquitetura)

1. **Entrada:** Lista de gaps priorizados + strengths do aluno + grafo de conhecimento.
2. **Preparação do Prompt:** Template `leveling_generator_v1.txt` populado com:
   - Nome do gap, importância, score atual.
   - Contexto da disciplina alvo (Cálculo I).
   - Strengths do aluno (para conectar conhecido ao novo).
3. **Geração com LLM (Structured Output):**
   - Para cada gap, chama `ILLMProvider.generate_structured()` com schema `GapExplanation`.
   - Retorna: why (importância), explanation (conceito), example (relacionado a Cálculo I), exercise (fixação).
4. **Ordenação:** Plano de estudo ordenado por importância + dependência topológica.
5. **Persistência:** Conteúdo salvo no PostgreSQL e cacheado no Valkey (TTL 7d).
6. **Exibição:** Frontend mostra timeline de estudos com cards expansíveis.

---

## Tarefas Sequenciais

### Tarefa 1: Modelagem de Domínio

- Criar `backend/domain/models/leveling.py`:
  - `GapExplanation` com: gap_name, importance, why_important, explanation, calculus_example, exercise, exercise_answer
  - `LevelingPlan` com: id, student_id, gaps[], study_order[], created_at

### Tarefa 2: Prompt Template

- Criar `backend/llm/prompts/leveling_generator_v1.txt`.
- Estrutura WEEE: Why → Explanation → Example → Exercise.
- Incluir contexto do aluno (strengths) para personalização.
- Instruir conexão explícita com Cálculo I.

### Tarefa 3: Serviço de Nivelamento

- Implementar `leveling_service.py`:
  - `generate_leveling_content(readiness_result)` → gera explicações para cada gap.
  - `create_study_order(gaps, knowledge_graph)` → ordenação topológica.
  - Se o LLM falhar para um gap, usar fallback com template pré-definido.

### Tarefa 4: Cache e Repositório

- `LevelingRepository`: salvar/buscar planos no PostgreSQL.
- `LevelingCache`: Valkey com TTL 7d.
- Idempotência: mesmo readiness_result → mesmo plano.

### Tarefa 5: Rotas FastAPI

- `POST /api/v1/leveling/generate` → gera plano a partir do readiness_result.
- `GET /api/v1/leveling/plan/{plan_id}` → recupera plano salvo.

### Tarefa 6: Frontend

- Criar `frontend/app/pages/leveling.py`.
- Componente `GapExplanation`: card com as 4 seções (Why, Explanation, Example, Exercise).
- Componente `StudyPlan`: timeline mostrando ordem de estudo.
- Botões: "Marcar como Concluído", "Exportar Plano", "Refazer Avaliação" (Fase 5).

### Tarefa 7: Testes

- Testar geração de conteúdo com `MockProvider`.
- Testar ordenação topológica do plano de estudo.
- Testar fallback quando LLM falha.
- Testar idempotência (cache).

---

## Critérios de Aceitação

- [ ] Conteúdo gerado para cada gap com estrutura WEEE.
- [ ] Exemplos conectados a Cálculo I.
- [ ] Plano de estudo ordenado por criticidade + dependência.
- [ ] Cache funciona (TTL 7d).
- [ ] Fallback quando LLM falha.
- [ ] Cobertura de testes > 80%.

---

## Decisões Técnicas

1. **Estrutura WEEE:** Why → Explanation → Example → Exercise é baseada em aprendizagem multimídia (Mayer). Cada seção tem função pedagógica específica.
2. **Conexão com Cálculo I:** Exemplos usam contextos de limites/derivadas para motivar o aluno ("você precisa disso para entender...").
3. **Ordenação Topológica:** Usa o grafo de conhecimento para determinar a ordem de estudo (base → derivado).
4. **Fallback Texto:** Se LLM falha, um template genérico é usado para não deixar o gap sem conteúdo.
