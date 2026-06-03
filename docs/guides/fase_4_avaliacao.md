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
