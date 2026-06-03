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
