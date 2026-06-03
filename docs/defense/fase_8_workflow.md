# Defesa Técnica - Fase 8: Orquestração de Workflow com LangGraph

## 1. Visão Geral

A Fase 8 integra todas as fases anteriores (3 a 7) em um workflow orquestrado e stateful utilizando LangGraph. O sistema agora opera como uma máquina de estados que gerencia o ciclo completo: upload → extração → avaliação → quiz → diagnóstico → nivelamento.

## 2. Decisões Arquiteturais

### 2.1. LangGraph StateGraph como Orquestrador Central

* **Decisão:** Utilização do `StateGraph` do LangGraph para modelar o workflow como um grafo de estados explícito.
* **Racional:** O problema de nivelamento educacional mapeia naturalmente para um workflow sequencial com pontos de decisão. LangGraph oferece:
  * **State management explícito:** Cada transição preserva e valida o estado.
  * **Checkpointing:** Workflows podem ser pausados e retomados.
  * **Tracing integrado:** Cada passo é automaticamente registrado no LangSmith/LangFuse.
  * **Paralelismo:** Nós independentes (ex: gap detection + strength analysis) podem executar em paralelo.

### 2.2. Nós do Workflow

* **Decisão:** Cinco nós principais no grafo: `extract_prerequisites`, `generate_assessment`, `evaluate_student`, `detect_gaps`, `generate_leveling`.
* **Racional:** Cada nó encapsula uma fase completa com responsabilidade única. A separação permite:
  * Testar cada nó independentemente.
  * Substituir implementações (ex: trocar o método de avaliação).
  * Adicionar nós de validação ou pós-processamento sem alterar o fluxo principal.

### 2.3. Checkpointing com PostgreSQL

* **Decisão:** Checkpoints do workflow são persistidos no PostgreSQL via tabela dedicada.
* **Racional:** Diferente de cache em memória, checkpoints em banco permitem recuperação mesmo após reinicialização do servidor. O aluno pode retomar o workflow de onde parou.

### 2.4. Workflow State Tipado (Pydantic)

* **Decisão:** O estado do workflow é um modelo Pydantic com validação estrita de tipos.
* **Racional:** Type safety no estado elimina bugs de "shape" (ex: acessar campo que não existe). O Pydantic valida automaticamente cada transição de estado, prevenindo corrupção.

## 3. Fluxo de Execução

```
[START] → extract_prerequisites → generate_assessment → evaluate_student → detect_gaps → generate_leveling → [END]
                ↓                       ↓                     ↓               ↓                  ↓
           KnowledgeGraph         Assessment[]          StudentScore     GapAnalysis       LevelingPlan
```

* **Condições de desvio:** Se a extração falhar (PDF inválido), o workflow termina com erro. Se o aluno já possui nivelamento prévio, o nó de geração pode ser pulado.

## 4. Observabilidade e Testabilidade

* **Tracing:** O LangGraph integra nativamente com OpenTelemetry. Cada nó do workflow aparece como um span no Jaeger.
* **Testes E2E:** O workflow completo é testado com `MockProvider` em todos os nós, validando o fluxo sem chamadas externas.
* **Resume:** Testes específicos validam que workflows interrompidos são retomados corretamente.

## 5. Conclusão

A Fase 8 consolida todo o sistema em um workflow orquestrado, stateful e resiliente. O LangGraph fornece a infraestrutura de orquestração necessária para operar o Adaptive Leveling System como um produto coeso.
