# Fase 9: Polimento, Testes Completos e Documentação

## Contexto

Este plano implementa a **Fase 9** do Adaptive Leveling System: Polimento, Testes Completos e Documentação.

Após todas as fases funcionais implementadas (3-8), o objetivo desta fase é **elevar o projeto ao padrão production-ready**. O foco está em três pilares: (1) Resiliência operacional (Circuit Breaker, Rate Limiting), (2) Testes abrangentes (segurança, performance, E2E) e (3) Documentação completa para diferentes stakeholders.

**Objetivo:** Garantir que o sistema seja robusto, seguro e bem documentado para implantação real.

---

## Estrutura de Arquivos Planejada

```
backend/
├── infrastructure/
│   ├── resilience/
│   │   ├── circuit_breaker.py          # Circuit breaker (LLM, DB, Cache)
│   │   ├── retry.py                    # Retry com exponential backoff
│   │   └── rate_limit.py              # Rate limiting por rota e usuário
│   └── security/
│       └── input_validator.py         # Validação de entrada (PDF, prompts)

tests/
├── integration/
│   └── test_full_workflow.py          # E2E workflow completo
├── security/
│   └── test_security.py               # LLM evasion, injection
├── performance/
│   └── test_load.py                   # 100 concurrent requests
└── fixtures/
    ├── calculus_1.pdf                 # PDF de teste
    └── malicious_prompt.pdf           # PDF com injeção de prompt

docs/
├── API.md                             # Documentação completa da API
├── ARCHITECTURE.md                    # Diagramas e decisões arquiteturais
└── USER_GUIDE.md                      # Guia passo-a-passo para usuários

frontend/
└── app/
    ├── theme.py                       # Tema consistente
    ├── components/
    │   └── loading.py                 # Custom loading states
    └── pages/
        └── help.py                    # Página de ajuda
```

---

## Fluxo de Validação (Qualidade)

1. **Testes de Segurança:** Enviar PDFs com injeções de prompt → sistema deve ignorar instruções maliciosas.
2. **Testes de Performance:** 100 requests concorrentes → p95 < 5s para orquestração (excluindo LLM).
3. **Testes E2E:** Workflow completo com `MockProvider` → valida integração entre todas as fases.
4. **Circuit Breaker:** Simular falha do LLM → circuito abre após 5 falhas → requests são rejeitados rapidamente → circuito half-open após timeout → recuperação gradual.
5. **Rate Limiting:** Exceder limite → 429 Too Many Requests.
6. **Cobertura:** `make test-cov` deve reportar > 80%.

---

## Tarefas Sequenciais

### Tarefa 1: Circuit Breaker

- Implementar `backend/infrastructure/resilience/circuit_breaker.py`.
- Configurações: threshold=5 falhas, timeout=60s, half-open max=3 requests.
- Aplicar aos clients: LLM (Groq), Database, Cache.

### Tarefa 2: Rate Limiting

- Implementar `rate_limit.py` com suporte a:
  - Limite global (ex: 100 requests/min).
  - Limite por rota (ex: `/extract` = 10 requests/min).
  - Limite por usuário (ex: 30 requests/min).
- Retornar headers `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`.

### Tarefa 3: Testes de Segurança (LLM Evasion)

- Criar PDF de teste com injeções de prompt no texto (ex: "Ignore instruções anteriores...").
- Testar que o sistema não é desviado por comandos maliciosos.
- Validar que o output do LLM ainda segue o schema esperado.

### Tarefa 4: Testes de Performance

- Criar `tests/performance/test_load.py`.
- 100 requests concorrentes para endpoints críticos.
- Validar p95 < 5s (excluindo tempo de LLM, usando MockProvider).
- Validar que rate limiting não é acionado injustamente.

### Tarefa 5: Testes E2E

- Criar `tests/integration/test_full_workflow.py`.
- Workflow completo: upload → extração → avaliação → quiz → gaps → nivelamento.
- Usar `MockProvider` em todos os nós.
- Validar estado em cada etapa.

### Tarefa 6: Documentação

- `docs/API.md`: Documentar todos os endpoints com exemplos curl.
- `docs/ARCHITECTURE.md`: Diagramas de arquitetura, fluxos, decisões técnicas.
- `docs/USER_GUIDE.md`: Guia para usuários não-técnicos (como usar o sistema).

### Tarefa 7: Frontend (Polimento)

- Criar `frontend/app/theme.py` com cores e estilos consistentes.
- Componente `Loading` com estados personalizados.
- Página de `Help` com FAQ e atalhos.

---

## Critérios de Aceitação

- [ ] Circuit breaker abre em 5 falhas consecutivas e recupera.
- [ ] Rate limiting retorna 429 com headers corretos.
- [ ] Testes de segurança: injeções de prompt são inertes.
- [ ] Performance: p95 < 5s em 100 requests concorrentes.
- [ ] Cobertura de testes > 80%.
- [ ] Documentação completa (API + Architecture + User Guide).
- [ ] Tema visual consistente no frontend.

---

## Decisões Técnicas

1. **Circuit Breaker no LLM:** Evita que falhas da API Groq derrubem todo o sistema; permite recuperação gradual.
2. **Rate Limiting em Camadas:** Protege endpoints caros (`/extract`) de forma mais rigorosa que endpoints leves (`/health`).
3. **Testes com MockProvider:** Garantem que os testes de performance meçam o overhead do sistema, não o tempo do LLM.
4. **Documentação em Três Níveis:** API (dev), Architecture (arquiteto), User Guide (usuário final) — cada um com linguagem e profundidade adequadas.
