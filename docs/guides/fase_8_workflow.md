# Fase 8: Orquestração de Workflow com LangGraph

## Contexto

Este plano implementa a **Fase 8** do Adaptive Leveling System: Orquestração de Workflow com LangGraph.

Com todas as fases funcionais (Extração, Avaliação, Quiz e Nivelamento) já implementadas e testadas individualmente, o objetivo desta fase é **integrá-las em um workflow único, automatizado e resiliente**. O LangGraph permite que o sistema gerencie o estado do aluno de ponta a ponta, permitindo pausas (ex: durante o quiz) e retomadas sem perda de progresso.

**Objetivo:** Implementar um `StateGraph` que orquestre o ciclo completo: upload → extração → geração de quiz → execução do quiz → diagnóstico de gaps → geração de nivelamento.

---

## Estrutura de Arquivos

```text
backend/
├── workflows/
│   ├── readiness_graph.py             # Definição do StateGraph (LangGraph)
│   ├── states.py                      # Definição do WorkflowState (Pydantic)
│   └── nodes/
│       ├── extract_node.py            # Nó de extração de inteligência
│       ├── assessment_node.py         # Nó de geração de avaliação
│       ├── quiz_node.py               # Nó de execução do quiz (Awaiting Input)
│       ├── readiness_node.py          # Nó de diagnóstico de gaps
│       └── leveling_node.py           # Nó de geração de conteúdo
├── api/
│   ├── routes/workflow.py             # Endpoints para disparo e acompanhamento
│   └── schemas/workflow.py            # Schemas de execução
└── services/workflow_service.py       # Lógica de interface com o grafo

frontend/
└── app/pages/8_⚙️_Workflow.py         # Interface visual da orquestração
```

---

## Fluxo de Processamento (Máquina de Estados)

1. **START**: O workflow inicia com o `pdf_id`.
2. **extract**: Chama o `prerequisite_service`. Se falhar, vai para **FAILED**.
3. **assessment**: Gera as 10 questões diagnósticas via `assessment_service`.
4. **quiz (Interrupt)**: O workflow pausa. O aluno realiza o quiz no frontend. O estado é salvo como `AWAITING_INPUT`.
5. **readiness**: Após o quiz, o workflow retoma, analisa os scores e identifica os gaps.
6. **leveling**: Se houver gaps, gera o conteúdo personalizado.
7. **END**: Workflow concluído com sucesso.

---

## Diferenciais da Orquestração

* **Checkpointing**: O estado de cada nó é salvo no PostgreSQL. Se a aplicação reiniciar, o aluno continua exatamente de onde parou.
* **Resiliência**: Tratamento de erros centralizado no grafo.
* **Observabilidade**: Cada transição de estado gera um trace detalhado no Jaeger/Langfuse.

---

## Critérios de Aceitação

* [ ] Grafo de estados funcional e compilado com sucesso.
* [ ] Suporte a interrupção e retomada (Human-in-the-loop simulado pelo Quiz).
* [ ] Interface visual no Streamlit mostrando o progresso em tempo real através dos nós.
* [ ] Persistência de checkpoints no banco de dados.
* [ ] Testes E2E validando o fluxo completo com MockProvider.
