# Fase 8: Orquestração de Workflow com LangGraph

## Contexto

Este plano implementa a **Fase 8** do Adaptive Leveling System: Orquestração de Workflow com LangGraph.

Até agora, cada fase opera de forma independente: o usuário navega manualmente entre upload → extração → avaliação → quiz → diagnóstico → nivelamento. O objetivo desta fase é **integrar todas as fases em um workflow orquestrado e stateful** usando LangGraph, onde o sistema gerencia automaticamente as transições de estado.

**Objetivo:** Implementar um StateGraph que orquestre o pipeline completo, com checkpointing, tracing e resumo de workflows.

---

## Estrutura de Arquivos Planejada

```
backend/
├── workflows/
│   ├── __init__.py
│   ├── readiness_graph.py             # LangGraph StateGraph definition
│   ├── states.py                      # Workflow state models (Pydantic)
│   └── nodes/
│       ├── __init__.py
│       ├── extract_node.py            # Wrapper para prerequisite_service
│       ├── assessment_node.py         # Wrapper para assessment_service
│       ├── quiz_node.py               # Wrapper para quiz_service
│       ├── readiness_node.py          # Wrapper para gap_detection_service
│       └── leveling_node.py           # Wrapper para leveling_service
│
├── api/
│   ├── routes/
│   │   └── workflow.py                # POST /execute, GET /{workflow_id}, POST /resume, DELETE
│   └── schemas/
│       └── workflow.py                # Schemas para workflow
│
├── infrastructure/
│   └── repository/
│       └── workflow_repository.py     # Checkpointing no PostgreSQL
│
└── services/
    └── workflow_service.py            # execute_workflow, resume, cancellation

frontend/
└── app/
    ├── components/
    │   ├── workflow_status.py          # Status visualization
    │   └── workflow_progress.py        # Progress tracker
    └── pages/
        └── workflow.py                 # Upload + trigger + acompanhamento

tests/
├── test_workflow.py                   # E2E com MockProvider em todos os nós
└── fixtures/
    └── workflow_fixtures.py           # Mock states
```

---

## Fluxo de Processamento (Arquitetura)

1. **Trigger:** Usuário faz upload de PDF e clica "Iniciar Análise Completa".
2. **StateGraph Inicia:** O workflow é criado com estado inicial contendo `pdf_id`.
3. **Nós Executam em Sequência:**
   - `extract_prerequisites` → grafo de conhecimento.
   - `generate_assessment` → avaliação diagnóstica.
   - `evaluate_student` → quiz e correção (requer interação do aluno).
   - `detect_gaps` → análise de prontidão.
   - `generate_leveling` → plano de nivelamento.
4. **Checkpointing:** A cada nó concluído, o estado é persistido no PostgreSQL.
5. **Resumo:** Workflows pausados (ex: aguardando quiz) podem ser retomados.
6. **Tracing:** Cada nó e transição são traceados no Jaeger via LangGraph.

---

## Tarefas Sequenciais

### Tarefa 1: Modelagem de Estado

- Criar `backend/workflows/states.py`:
  - `WorkflowState` (Pydantic BaseModel) com campos para cada fase.
  - `WorkflowStatus` enum (PENDING, IN_PROGRESS, AWAITING_INPUT, COMPLETED, FAILED).

### Tarefa 2: Definição do Grafo

- Criar `backend/workflows/readiness_graph.py`:
  - `StateGraph(WorkflowState)` com 5 nós.
  - Arestas condicionais: se extração falha → termina; se aluno pronto → pula nivelamento.
  - Compilação do grafo com `app.compile(checkpointer=...)`.

### Tarefa 3: Nós do Workflow

- Cada nó em `backend/workflows/nodes/`:
  - `extract_node.py`: chama `prerequisite_service.extract_prerequisites()`.
  - `assessment_node.py`: chama `assessment_service.generate_assessment()`.
  - `quiz_node.py`: retorna estado `AWAITING_INPUT` até aluno finalizar.
  - `readiness_node.py`: chama `gap_detection_service.analyze_gaps()`.
  - `leveling_node.py`: chama `leveling_service.generate_leveling_content()`.

### Tarefa 4: Checkpointing

- Implementar `WorkflowRepository` para persistir checkpoints no PostgreSQL.
- Tabela `workflow_checkpoints`: workflow_id, node, state (JSONB), created_at.

### Tarefa 5: Serviço de Workflow

- `workflow_service.py`:
  - `execute_workflow(pdf_id)` → cria e dispara o grafo.
  - `resume_workflow(workflow_id)` → retoma de checkpoint.
  - `cancel_workflow(workflow_id)` → cancela execução.

### Tarefa 6: Rotas FastAPI

- `POST /api/v1/workflow/execute` → inicia workflow.
- `GET /api/v1/workflow/{workflow_id}` → status atual.
- `POST /api/v1/workflow/{workflow_id}/resume` → retoma.
- `DELETE /api/v1/workflow/{workflow_id}` → cancela.

### Tarefa 7: Frontend

- Criar `frontend/app/pages/workflow.py`.
- Upload + botão "Iniciar Análise Completa".
- Status em tempo real com progress tracker.
- Suporte a pausa (para quiz) e retomada.

### Tarefa 8: Testes

- Testar workflow completo com `MockProvider`.
- Testar checkpointing (interromper e retomar).
- Testar cancelamento.
- Testar fluxo de erro (nó falha → workflow FAILED).

---

## Critérios de Aceitação

- [ ] Workflow executa end-to-end (PDF → plano de nivelamento).
- [ ] Checkpointing funciona (retoma de onde parou).
- [ ] Workflows podem ser cancelados.
- [ ] Frontend mostra progresso em tempo real.
- [ ] Nós paralelos quando possível.
- [ ] Cobertura de testes > 80%.

---

## Decisões Técnicas

1. **LangGraph StateGraph:** Modelagem explícita de estados com validação Pydantic — type safety em todas as transições.
2. **Checkpointing no PostgreSQL:** Diferente de cache em memória, permite retomada após reinicialização do servidor.
3. **Nó de Quiz como AWAITING_INPUT:** O workflow pausa até o aluno completar o quiz, permitindo workflows assíncronos.
4. **Tracing Nativo:** LangGraph integra com OpenTelemetry — cada nó vira um span no Jaeger.
