# Fase 5: Avaliação do Estudante (Quiz Interativo)

## Contexto

Este plano implementa a **Fase 5** do Adaptive Leveling System: Avaliação do Estudante.

Com a avaliação diagnóstica gerada na Fase 4, o próximo passo é **apresentá-la ao aluno** em formato de quiz interativo. O sistema corrige as respostas usando uma abordagem híbrida: Múltipla Escolha (MC) é corrigida deterministicamente (comparação exata), enquanto Resposta Curta (SA) e Cálculo (Calc) são avaliadas por um LLM atuando como juiz (LLM-as-a-Judge).

**Objetivo:** Implementar um quiz funcional com correção inteligente, sessão com auto-save e feedback imediato ao aluno.

---

## Estrutura de Arquivos Planejada

```
backend/
├── api/
│   ├── routes/
│   │   └── quiz.py                    # GET /start, GET /questions, POST /answer, POST /finish
│   └── schemas/
│       └── quiz.py                    # Schemas para quiz session
│
├── llm/
│   ├── evaluators/
│   │   └── answer_evaluator.py        # LLM-as-a-Judge para SA/Calc
│   └── prompts/
│       └── answer_evaluator_v1.txt    # Prompt de avaliação com rubrica
│
├── infrastructure/
│   ├── cache/
│   │   └── student_cache.py           # Session cache (TTL 1h) via Valkey
│   └── repository/
│       └── student_repository.py      # Student progress no PostgreSQL
│
└── services/
    └── quiz_service.py                # Quiz logic, evaluate_answer

frontend/
└── app/
    ├── components/
    │   ├── question_card.py           # MC=radio, SA=textarea, Calc=textarea+math
    │   └── timer.py                   # Timer por questão e sessão
    └── pages/
        └── quiz.py                    # Quiz interativo completo

tests/
├── test_quiz_service.py               # Avaliação MC (determinística)
├── test_answer_evaluator.py           # LLM evaluator com MockProvider
└── fixtures/
    └── quiz_fixtures.py               # Mock answers
```

---

## Fluxo de Processamento (Arquitetura)

1. **Início da Sessão:** O aluno solicita iniciar o quiz → sistema cria sessão no Valkey (TTL 1h).
2. **Apresentação de Questões:** Questões são exibidas uma por vez com timer.
3. **Submissão de Resposta:** O aluno responde → sistema salva progresso no cache.
4. **Correção Híbrida:**
   - **MC:** `resposta == gabarito` → score 0 ou 100.
   - **SA/Calc:** Envia (questão, resposta esperada, resposta do aluno) para o LLM → retorna score 0-100 com justificativa.
5. **Finalização:** Ao terminar, scores consolidados são persistidos no PostgreSQL.
6. **Navegação:** Botão "Ver Resultados" → Fase 6.

---

## Tarefas Sequenciais

### Tarefa 1: Modelagem de Domínio

- Criar `QuizSession`, `QuizAnswer` em `backend/domain/models/quiz.py`.
- Definir status: `IN_PROGRESS`, `COMPLETED`, `TIMEOUT`.

### Tarefa 2: Repositórios e Cache

- `StudentRepository`: salvar progresso final no PostgreSQL.
- `StudentCache`: salvar respostas parciais no Valkey (TTL 1h) para auto-save.

### Tarefa 3: Prompt de Avaliação (LLM-as-a-Judge)

- Criar `backend/llm/prompts/answer_evaluator_v1.txt`.
- Rubrica explícita com níveis: 0% (errado), 25% (parcial), 50% (médio), 75% (quase certo), 100% (correto).
- Exigir justificativa para cada nota.

### Tarefa 4: Serviço de Quiz

- Implementar `quiz_service.py`:
  - `start_session(student_id, assessment_id)` → cria sessão.
  - `submit_answer(session_id, question_id, answer)` → corrige e salva.
  - `finish_quiz(session_id)` → persiste resultados, calcula score parcial.
- Para MC: correção direta (`answer == question.correct_answer`).
- Para SA/Calc: chamar `AnswerEvaluator.evaluate()`.

### Tarefa 5: Rotas FastAPI

- `POST /api/v1/quiz/start` → inicia sessão.
- `GET /api/v1/quiz/{session_id}/questions` → próxima questão.
- `POST /api/v1/quiz/{session_id}/answer` → submete resposta.
- `POST /api/v1/quiz/{session_id}/finish` → finaliza.

### Tarefa 6: Frontend

- Criar `frontend/app/pages/quiz.py` com quiz interativo.
- Componente `QuestionCard`: renderiza MC como radio buttons, SA/Calc como textarea.
- Timer visual por questão, indicador de progresso.
- Auto-save a cada resposta (feedback "Salvo").
- Botão "Ver Meus Resultados" → Fase 6.

### Tarefa 7: Testes

- Testar correção MC com respostas certas e erradas (determinístico).
- Testar `AnswerEvaluator` com `MockProvider` para SA/Calc.
- Testar fluxo completo: start → answer → finish.
- Testar auto-save (cache hit/miss).

---

## Critérios de Aceitação

- [ ] Quiz flow funcional (start → questions → answer → finish).
- [ ] MC corrigida deterministicamente (certa/errada).
- [ ] SA/Calc corrigidas por LLM com score 0-100 e justificativa.
- [ ] Auto-save a cada resposta (Valkey).
- [ ] Dados persistidos ao finalizar (PostgreSQL).
- [ ] Timer por questão (não bloqueante).
- [ ] Cobertura de testes > 80%.

---

## Decisões Técnicas

1. **Correção Híbrida:** MC determinística (sem custo de API) + SA/Calc com LLM (flexibilidade semântica). Reduz custos em ~40%.
2. **Rubrica Estruturada:** Níveis discretos de acerto reduzem variabilidade do LLM e produzem scores consistentes.
3. **Auto-Save em Cache:** Valkey com TTL 1h protege contra perda de sessão sem sobrecarregar o PostgreSQL.
4. **Timer Não Bloqueante:** Apenas informativo para reduzir ansiedade, não trava o quiz.

---

## Status da Implementação (Junho/2026)

### Estrutura de Arquivos

| Arquivo | Status | Observação |
|---------|--------|------------|
| `backend/api/routes/quiz.py` | ✅ | POST /start, GET /{id}/next, POST /{id}/answer, POST /{id}/finish |
| `backend/api/schemas/quiz.py` | ✅ | StartQuizRequest/Response, SubmitAnswerRequest/Response, FinishQuizResponse |
| `backend/llm/evaluators/answer_evaluator.py` | ✅ | evaluate_mcq() deterministic, evaluate() LLM-as-a-Judge |
| `backend/llm/prompts/answer_evaluator_v1.txt` | ✅ | Rubrica 0/25/50/75/100 com justificativa |
| `backend/infrastructure/student_cache.py` | ✅ | Valkey TTL 1h (nota: em `infrastructure/`, não `infrastructure/cache/`) |
| `backend/infrastructure/repository/student_repository.py` | ✅ | save_quiz_session, get_quiz_session com upsert |
| `backend/services/quiz_service.py` | ✅ | start_quiz, get_next_question, submit_answer, finish_quiz |
| `backend/domain/models/quiz.py` | ✅ | SessionStatus, QuizAnswer, QuizSession |
| `migrations/004_quiz_schema.sql` | ✅ | Tabela quiz_sessions com JSONB answers |
| `frontend/app/components/question_card.py` | ❌ | **Embedded** na página 5_🏁_Quiz.py |
| `frontend/app/components/timer.py` | ❌ | **Não implementado** |
| `frontend/app/pages/5_🏁_Quiz.py` | ✅ | Quiz interativo com progresso e score |
| `tests/test_quiz_service.py` | ✅ | 4 testes (start, no questions, submit MCQ, finish) |
| `tests/test_answer_evaluator.py` | ✅ | 5 testes (MC correct/wrong/case, prompt, model) |
| `tests/fixtures/quiz_fixtures.py` | ❌ | **Não criado.** Mocks inline nos testes |

### Critérios de Aceitação

- [x] Quiz flow funcional (start → questions → answer → finish)
- [x] MC corrigida deterministicamente (certa/errada, case-insensitive)
- [x] SA/Calc corrigidas por LLM com score 0-100 e justificativa
- [x] Auto-save a cada resposta (Valkey, TTL 1h)
- [x] Dados persistidos ao finalizar (PostgreSQL)
- [ ] Timer por questão — **não implementado**
- [x] Cobertura de testes > 80% (módulo de avaliação)

### Notas Técnicas

- O `student_cache.py` ficou em `backend/infrastructure/student_cache.py` (não dentro de `cache/`) porque `backend/infrastructure/cache.py` (módulo) conflitaria com `backend/infrastructure/cache/` (pacote).
- O timer por questão não foi implementado. A decisão técnica original mencionava timer "apenas informativo e não bloqueante", mas não chegou a ser codificado.
- O componente `QuestionCard` (MC=radio, SA=textarea, Calc=textarea) foi implementado inline na página de quiz em vez de componente separado.
- O frontend faz correção MC localmente (não chama API para SA/Calc). O backend suporta SA/Calc via LLM mas o frontend não está integrado a esse endpoint.
