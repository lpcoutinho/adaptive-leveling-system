# Fase 4: Geração de Avaliação Diagnóstica

## Contexto

Este plano implementa a **Fase 4** do Adaptive Leveling System: Geração de Avaliação Diagnóstica.

Agora que conseguimos extrair os pré-requisitos de uma aula usando LLM (Fase 3), o objetivo desta fase é **gerar questões de avaliação** que testem o conhecimento do aluno em cada pré-requisito identificado. A avaliação é o ponto de partida para medir a prontidão do aluno antes da disciplina alvo.

**Objetivo:** Gerar um conjunto balanceado de questões (Múltipla Escolha, Resposta Curta, Cálculo) para cada pré-requisito, utilizando o LLM com prompts versionados e validação Pydantic.

---

## Estrutura de Arquivos Planejada

```
backend/
├── api/
│   ├── routes/
│   │   └── assessment.py              # POST /generate, GET /{assessment_id}
│   └── schemas/
│       └── assessment.py              # Pydantic schemas para a API (request/response)
│
├── domain/
│   └── models/
│       ├── assessment.py              # QuizQuestion, Assessment, QuestionType enum
│       └── student.py                 # Student, StudentAnswer
│
├── infrastructure/
│   ├── cache/
│   │   └── assessment_cache.py        # Valkey cache (TTL 7d)
│   └── repository/
│       └── assessment_repository.py   # DB operations
│
├── llm/
│   └── prompts/
│       └── assessment_generator_v1.txt # Prompt para gerar questões
│
└── services/
    └── assessment_service.py          # generate_assessment, balanceamento de tipos

frontend/
└── app/
    ├── components/
    │   └── quiz.py                    # Quiz widget base (reutilizado na Fase 5)
    └── pages/
        └── assessment.py              # Preview da avaliação gerada

tests/
├── test_assessment_service.py         # Testes com MockProvider
├── test_assessment_routes.py          # Testes dos endpoints
└── fixtures/
    └── assessment_fixtures.py         # Mock assessments
```

---

## Fluxo de Processamento (Arquitetura)

1. **Requisição:** O usuário solicita a geração de avaliação para um `pdf_id`.
2. **Recuperação de Pré-requisitos:** O serviço busca o grafo de conhecimento (salvo na Fase 3) no banco.
3. **Preparação do Prompt:** O template `assessment_generator_v1.txt` é populado com a lista de pré-requisitos e suas importâncias.
4. **Geração com LLM (Structured Output):**
   - O `ILLMProvider.generate_structured()` é chamado com o modelo `Assessment`.
   - O LLM retorna N questões por pré-requisito com distribuição: 40% MC, 30% SA, 30% Calc.
5. **Validação e Cache:** A avaliação gerada é validada contra o schema, armazenada em cache (Valkey, TTL 7d) e persistida no PostgreSQL.
6. **Observabilidade:** Métricas de distribuição de tipos são registradas; tracing no Jaeger.

---

## Tarefas Sequenciais

### Tarefa 1: Modelagem de Domínio

- Criar `backend/domain/models/assessment.py` com:
  - `QuestionType` enum (MULTIPLE_CHOICE, SHORT_ANSWER, CALCULATION)
  - `QuizQuestion` modelo com campos: id, type, text, options (MC), correct_answer, difficulty, topic, justification
  - `Assessment` modelo com: id, pdf_id, questions[], created_at
- Criar `backend/domain/models/student.py` com `Student` e `StudentAnswer`.

### Tarefa 2: Schema da API

- Criar `backend/api/schemas/assessment.py` com schemas request/response.

### Tarefa 3: Prompt Template

- Criar `backend/llm/prompts/assessment_generator_v1.txt`.
- Incluir exemplos few-shot para cada tipo de questão.
- Instruir distribuição balanceada (40/30/30).

### Tarefa 4: Serviço de Geração

- Implementar `assessment_service.py` com `generate_assessment(pdf_id: UUID)`.
- Lógica de balanceamento: garantir que a distribuição real se aproxime da alvo.
- Validação pós-geração: verificar se todos os pré-requisitos têm ao menos 1 questão.

### Tarefa 5: Persistência e Cache

- Criar `AssessmentRepository` para salvar/buscar avaliações no PostgreSQL.
- Criar `AssessmentCache` no Valkey com TTL de 7 dias.
- Idempotência: se avaliação já existe, retornar sem regenerar.

### Tarefa 6: Rotas FastAPI

- Criar `backend/api/routes/assessment.py`.
- `POST /api/v1/assessment/generate/{pdf_id}` → gera avaliação.
- `GET /api/v1/assessment/{assessment_id}` → recupera avaliação salva.
- Registrar rota no `main.py`.

### Tarefa 7: Frontend

- Criar `frontend/app/pages/assessment.py`.
- Exibir lista de questões agrupadas por pré-requisito.
- Mostrar metadados (tipo, dificuldade, tópico).
- Botão "Iniciar Quiz" navega para Fase 5.

### Tarefa 8: Testes

- Testar geração com `MockProvider` retornando questões mockadas.
- Testar distribuição de tipos (40/30/30).
- Testar idempotência (cache hit vs miss).
- Testar validação de schema (LLM retorna JSON inválido).

---

## Critérios de Aceitação

- [ ] Questões geradas com tipos corretos (MC, SA, Calc).
- [ ] Distribuição balanceada (40% MC, 30% SA, 30% Calc).
- [ ] Cada pré-requisito tem ao menos 1 questão.
- [ ] Cache funciona (TTL 7d, idempotência).
- [ ] Frontend exibe avaliação com metadados.
- [ ] Cobertura de testes > 80%.

---

## Decisões Técnicas

1. **Distribuição Fixa:** 40/30/30 garante balanceamento sem depender de heurísticas complexas.
2. **Few-Shot no Prompt:** Exemplos concretos melhoram a qualidade das questões geradas.
3. **Validação Pós-Geração:** O serviço valida a distribuição real após o LLM responder; se desvio > 10%, regenera questões faltantes.
4. **Testes com MockProvider:** Mock retorna questões pré-definidas para validar estrutura e distribuição.

---

## Status da Implementação (Junho/2026)

### Estrutura de Arquivos

| Arquivo | Status | Observação |
|---------|--------|------------|
| `backend/api/routes/assessment.py` | ✅ | POST /generate/{pdf_id}, GET /{id}, GET /pdf/{pdf_id} |
| `backend/api/schemas/assessment.py` | ✅ | QuizQuestionSchema, AssessmentResponse |
| `backend/domain/models/assessment.py` | ✅ | QuestionType, QuizQuestion, Assessment |
| `backend/domain/models/student.py` | ❌ | **Não criado.** Student/StudentAnswer migrados para quiz.py |
| `backend/infrastructure/cache/assessment_cache.py` | ❌ | **Não criado.** Apenas idempotência via banco (sem cache Valkey dedicado) |
| `backend/infrastructure/repository/assessment_repository.py` | ✅ | save, get_by_pdf_id, get_by_id com upsert |
| `backend/llm/prompts/assessment_generator_v1.txt` | ✅ | Prompt com 40/30/30 e self-correction |
| `backend/services/assessment_service.py` | ✅ | generate_assessment com idempotência |
| `frontend/app/components/quiz.py` | ✅ | render_quiz() e render_question() |
| `frontend/app/pages/3_📋_Assessment.py` | ✅ | Métricas de tipo + botão "Iniciar Quiz" |
| `tests/test_assessment_service.py` | ✅ | 4 testes (success, no prereqs, idempotency, prompt) |
| `tests/test_assessment_routes.py` | ✅ | 3 testes (no prereqs 404, not found 404s) |
| `tests/fixtures/assessment_fixtures.py` | ❌ | **Não criado.** Mocks inline nos testes |

### Critérios de Aceitação

- [x] Questões geradas com tipos corretos (MC, SA, Calc)
- [ ] Distribuição balanceada (40% MC, 30% SA, 30% Calc) — *depende exclusivamente do prompt, sem validação server-side*
- [ ] Cada pré-requisito tem ao menos 1 questão — *prompt pede 2 por pré-requisito, sem validação server-side*
- [x] Idempotência via PostgreSQL (upsert por pdf_id)
- [ ] Cache Valkey com TTL 7d — **não implementado**
- [x] Frontend exibe avaliação com metadados
- [x] Botão "Iniciar Quiz" navega para Fase 5

### Notas Técnicas

- O balanceamento 40/30/30 não é validado após a geração. O prompt instrui a distribuição mas não há verificação server-side de desvio > 10% conforme planejado nas decisões técnicas.
- O cache Valkey dedicado (TTL 7d) não foi implementado. A idempotência funciona via `ON CONFLICT (pdf_id) DO UPDATE` no PostgreSQL.
- O modelo `Student`/`StudentAnswer` planejado em `student.py` foi substituído pelos modelos de `quiz.py` (`QuizSession`, `QuizAnswer`).
- A validação de schema do JSON retornado pelo LLM é feita pelo Pydantic (`generate_structured`).
