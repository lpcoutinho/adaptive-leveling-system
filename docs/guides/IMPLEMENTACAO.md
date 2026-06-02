# Plano de Implementação - Adaptive Leveling System

## Contexto

Este plano implementa o **Case 1 - Nivelamento** do desafio técnico, usando LLM para extrair pré-requisitos de uma aula de Cálculo I, analisar a prontidão do aluno e gerar conteúdo de nivelamento personalizado.

**Estratégia:** Full Stack Vertical (cada fase com backend + frontend + testes + observabilidade completos)

**Stack:** LLM Abstraction + Groq/OpenAI/Anthropic + Postgres + Valkey + Minio + OpenTelemetry + Jaeger + Langfuse (Fase 3)

**LLM Abstraction com Dependency Injection:**

- **Interface ILLMProvider**: Contrato abstrato para providers
- **Providers**: Groq, OpenAI, Anthropic, Mock (testes)
- **DI Setup**: FastAPI Depends + Provider Factory
- **Configuração**: LLM_PROVIDER=groq|openai|anthropic|mock (via env var)
- **Resiliência**: Retry, Timeout, Circuit Breaker, Fallback Chain
- **Observabilidade**: Jaeger (Tracing) e Langfuse (LLM Monitoring - Fase 3)

**Arquitetura Local com Containers Dedicados:**

- **Minio (S3)**: PDFs armazenados como objetos (porta 9005 API, 9006 Console)
- **PostgreSQL**: Metadados + dados relacionais (porta 5435)
- **Valkey**: Cache de resultados processados (porta 6385)
- **Vantagens**: Isolamento total, portas exclusivas para evitar conflitos, compatibilidade nativa com drivers async.

---

## Fase 1: Fundação e Infraestrutura Base

**Objetivo:** Estabelecer toda a fundação técnica com infraestruturas críticas configuradas.

### Backend

- `pyproject.toml` - Dependências (FastAPI, LangGraph, PydanticAI, Groq, boto3/S3, OpenTelemetry, Loguru, redis-py)
- `backend/main.py` - FastAPI app factory com CORS, exception handlers
- `backend/config.py` - Configuração centralizada (settings, secrets via env vars)
- `backend/llm/` - LLM Abstraction Layer
  - `base/interface.py` - Interface ILLMProvider (contrato abstrato)
  - `base/models.py` - Request/Response models
  - `config.py` - LLM configuration via environment variables
  - `factory.py` - Provider factory com DI setup
  - `providers/groq_provider.py` - Groq implementation
  - `providers/openai_provider.py` - OpenAI implementation (future)
  - `providers/anthropic_provider.py` - Anthropic implementation (future)
  - `providers/mock_provider.py` - Mock para testes
  - `resilience/retry.py` - Retry com exponential backoff
  - `resilience/circuit_breaker.py` - Circuit breaker
  - `resilience/fallback.py` - Fallback chain
  - `prompts/*.txt` - Prompts versionados
- `backend/api/dependencies/llm.py` - FastAPI dependencies para LLM DI
- `backend/infrastructure/telemetry/tracer.py` - OpenTelemetry setup (tracing + metrics)
- `backend/infrastructure/telemetry/metrics.py` - Métricas customizadas
- `backend/infrastructure/telemetry/logger.py` - Loguru wrapper com structured logging
- `backend/infrastructure/database.py` - PostgreSQL connection pool com retry logic
- `backend/infrastructure/cache.py` - Valkey client com serialization
- `backend/infrastructure/storage.py` - S3 client (Minio) com presigned URLs (endpoint_url=<http://localhost:9005>)
- `backend/infrastructure/security.py` - Input validation, rate limiting
- `backend/api/routes/health.py` - Health check (DB, Redis, Groq)
- `migrations/001_initial_schema.sql` - Schema base (sem BLOB, apenas metadados)

### Frontend

- `frontend/app/app.py` - App principal com sidebar
- `frontend/app/pages/health.py" - Health check page
- `frontend/app/config.py` - Configuração do frontend

### Infraestrutura

- `docker-compose.yml` - Postgres + Valkey + Minio

```yaml
services:
  db:
    image: postgres:16-alpine
    container_name: als-db
    ports:
      - "5435:5432"
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5
    networks:
      - als

  cache:
    image: valkey/valkey:8
    container_name: als-cache
    ports:
      - "6385:6379"
    healthcheck:
      test: ["CMD", "valkey-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5
    networks:
      - als

  s3:
    image: minio/minio
    container_name: als-s3
    ports:
      - "9005:9000"
      - "9006:9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    volumes:
      - minio_data:/data
    command: server /data --console-address ":9001"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 5s
      timeout: 5s
      retries: 5
    networks:
      - als

  create-buckets:
    image: minio/mc
    container_name: als-init-s3
    depends_on:
      s3:
        condition: service_healthy
    entrypoint: >
      /bin/sh -c "
      /usr/bin/mc alias set local http://s3:9000 minioadmin minioadmin;
      /usr/bin/mc mb local/als-documents;
      /usr/bin/mc policy set public local/als-documents;
      exit 0;
      "
    networks:
      - als

volumes:
  postgres_data:
    driver: local
  minio_data:
    driver: local

networks:
  als:
    driver: bridge
```

### Testes

- `tests/test_infrastructure.py` - Testes DB, Valkey, S3, config
- `tests/test_api_health.py` - Testes health endpoints
- `tests/conftest.py` - Fixtures (DB, Valkey, HTTP client)

### Critérios de Aceitação

- Backend inicia sem erros, health check retorna 200
- Containers (S3, DB, Cache) saudáveis e conectáveis
- Traces visíveis no Jaeger/Console
- Frontend inicia e mostra status dos serviços
- Upload/download no Minio funciona
- Valkey cache operations funcionam

---

## Fase 2: Upload e Processamento de PDF

**Objetivo:** Upload de PDF com processamento, cache e idempotência.

### Backend

- `backend/domain/models/pdf.py` - PDFDocument, PDFMetadata (Pydantic)
- `backend/domain/models/common.py` - BaseModel, Timestamps
- `backend/services/pdf_service.py` - Upload para S3, extração de texto (PyPDF2), hash SHA-256, validação, normalização
- `backend/infrastructure/repository/pdf_repository.py` - DB operations (save metadata, get by hash/id)
- `backend/infrastructure/storage/pdf_storage.py` - S3 operations (upload, download, delete, presigned URL)
- `backend/infrastructure/cache/pdf_cache.py` - Valkey cache (TTL 24h)
- `backend/api/routes/pdf.py` - POST /upload, GET /{pdf_id}, GET /hash/{hash}, DELETE
- `backend/api/schemas/pdf.py` - Request/response schemas

### Frontend

- `frontend/app/pages/upload.py` - File uploader, drag & drop, preview
- `frontend/app/components/pdf_preview.py` - PDF preview component
- `frontend/app/components/pdf_download.py` - Download button com presigned URL

### Testes

- `tests/test_pdf_service.py` - Extração, hash, validação
- `tests/test_pdf_routes.py` - API endpoints
- `tests/test_pdf_storage.py` - S3 operations
- `tests/test_pdf_cache.py` - Cache layer
- `tests/fixtures/pdf_fixtures.py` - Test PDFs
- `tests/fixtures/calculus_1.pdf` - Sample PDF

### Critérios de Aceitação

- Upload funciona, PDF enviado para S3
- Hash SHA-256 gerado e metadados salvos no PostgreSQL
- Cache Valkey funciona
- Re-upload do mesmo PDF reusa resultado (idempotência via hash)
- PDFs inválidos rejeitados, rate limiting funciona
- Download com presigned URL funciona (expira corretamente)

---

## Fase 3: Extração de Pré-requisitos com LLM

**Objetivo:** Extrair pré-requisitos usando LLM Abstraction com structured outputs e monitoramento com Langfuse.

### Backend

- `backend/domain/models/prerequisite.py` - Prerequisite, ConceptNode (Pydantic)
- `backend/domain/models/knowledge_graph.py` - KnowledgeGraph
- `backend/llm/` - LLM Abstraction (implementado na Fase 1)
  - `providers/groq_provider.py` - Groq implementation
  - `providers/mock_provider.py` - Mock para testes
  - `prompts/prerequisite_extractor_v1.txt` - Prompt template versionado
- `backend/services/prerequisite_service.py` - extract_prerequisites, build_knowledge_graph (usa ILLMProvider via DI)
- `backend/api/routes/prerequisites.py" - POST /extract, GET /{pdf_id}, GET /{pdf_id}/graph

### Frontend

- `frontend/app/pages/prerequisites.py` - Lista de pré-requisitos, filtragem por importance
- `frontend/app/components/knowledge_graph.py` - Graph visualization (network graph)

### Testes

- `tests/test_prerequisite_service.py` - Extraction com mock LLM
- `tests/test_llm_provider.py` - Groq API, retry, fallback
- `tests/fixtures/prerequisite_fixtures.py` - Mock data

### Critérios de Aceitação

- Extração funciona via API, structured output validado
- Knowledge graph construído corretamente
- Cache funciona, idempotência (reuso)
- Fallback model e retry funcionam

---

## Fase 4: Geração de Avaliação Diagnóstica

**Objetivo:** Gerar questões de avaliação baseadas nos pré-requisitos.

### Backend

- `backend/domain/models/assessment.py` - QuizQuestion, Assessment, QuestionType (Pydantic)
- `backend/domain/models/student.py` - Student, StudentAnswer
- `backend/services/assessment_service.py` - generate_assessment com balanceamento de tipos (40% MC, 30% SA, 30% Calc)
- `backend/llm/prompts/assessment_generator_v1.txt` - Assessment prompt
- `backend/infrastructure/repository/assessment_repository.py` - DB operations
- `backend/infrastructure/cache/assessment_cache.py` - Valkey cache (TTL 7d)
- `backend/api/routes/assessment.py` - POST /generate, GET /{assessment_id}

### Frontend

- `frontend/app/pages/assessment.py` - Lista de questões, filtragem, preview
- `frontend/app/components/quiz.py` - Quiz widget base

### Testes

- `tests/test_assessment_service.py` - Geração com mock LLM
- `tests/fixtures/assessment_fixtures.py` - Mock assessments

### Critérios de Aceitação

- Questões geradas com tipos corretos
- Distribuição balanceada, cache funciona

---

## Fase 5: Avaliação do Estudante

**Objetivo:** Quiz interativo com correção (objetiva + LLM-as-a-Judge).

### Backend

- `backend/services/quiz_service.py` - Quiz logic, evaluate_answer (deterministic para MC, LLM para SA/Calc)
- `backend/llm/evaluators/answer_evaluator.py` - LLM-as-a-Judge
- `backend/infrastructure/repository/student_repository.py` - Student progress
- `backend/infrastructure/cache/student_cache.py` - Session cache (TTL 1h) via Valkey
- `backend/api/routes/quiz.py` - GET /start, GET /questions, POST /answer, POST /finish

### Frontend

- `frontend/app/pages/quiz.py` - Quiz interativo
- `frontend/app/components/question_card.py` - Question component (MC=radio, SA/Calc=text)

### Testes

- `tests/test_quiz_service.py` - Avaliação MC (determinística), SA/Calc (LLM)
- `tests/test_answer_evaluator.py` - LLM evaluator

### Critérios de Aceitação

- Quiz flow funciona, score calculado corretamente
- MC avaliada deterministicamente, SA/Calc por LLM
- Session management funciona, auto-save

---

## Fase 6: Detecção de Gaps e Análise de Prontidão

**Objetivo:** Analisar prontidão e detectar gaps de conhecimento.

### Backend

- `backend/domain/models/readiness.py` - ReadinessResult, GapAnalysis, ReadinessLevel (Ready/Needs Review/Not Ready)
- `backend/services/gap_detection_service.py` - analyze_gaps, scoring (Critical=3x, Important=2x, Helpful=1x)
- `backend/api/routes/readiness.py` - POST /analyze, GET /{session_id}, GET /{session_id}/gaps

### Frontend

- `frontend/app/pages/readiness.py` - Score (gauge), level visual, strengths/gaps lists
- `frontend/app/components/readiness_card.py` - Score card
- `frontend/app/components/gaps_list.py` - Gaps visualization

### Testes

- `tests/test_gap_detection_service.py` - Scoring, strengths/gaps identification
- `tests/fixtures/readiness_fixtures.py` - Mock results

### Critérios de Aceitação

- Score calculado com pesos corretos
- Strengths/gaps identificados, level determinado
- Gaps priorizados por severidade

---

## Fase 7: Geração de Conteúdo de Nivelamento

**Objetivo:** Gerar conteúdo de nivelamento personalizado para cada gap.

### Backend

- `backend/domain/models/leveling.py" - GapExplanation, LevelingPlan (Pydantic)
- `backend/services/leveling_service.py` - generate_leveling_content, create_study_order
- `backend/llm/prompts/leveling_generator_v1.txt` - Leveling prompt
- `backend/infrastructure/repository/leveling_repository.py` - DB operations
- `backend/infrastructure/cache/leveling_cache.py` - Valkey cache (TTL 7d)
- `backend/api/routes/leveling.py` - POST /generate, GET /plan/{plan_id}

### Frontend

- `frontend/app/pages/leveling.py` - Explicações ordenadas, study timeline
- `frontend/app/components/gap_explanation.py` - Explanation card (why, explanation, example, exercise)
- `frontend/app/components/study_plan.py` - Study timeline

### Testes

- `tests/test_leveling_service.py` - Geração com mock LLM
- `tests/fixtures/leveling_fixtures.py` - Mock content

### Critérios de Aceitação

- Explicações geradas para cada gap
- Study order correto, cache/fallback funcionam

---

## Fase 8: Workflow Orquestrado com LangGraph

**Objetivo:** Workflow end-to-end orquestrado com LangGraph.

### Backend

- `backend/workflows/readiness_graph.py` - LangGraph StateGraph com nodes (extract, assess, evaluate, detect, level)
- `backend/workflows/states.py` - Workflow state models
- `backend/services/workflow_service.py` - execute_workflow, resume, cancellation
- `backend/api/routes/workflow.py` - POST /execute, GET /{workflow_id}, POST /resume, DELETE

### Frontend

- `frontend/app/pages/workflow.py` - Upload + trigger, status em tempo real
- `frontend/app/components/workflow_status.py` - Status visualization
- `frontend/app/components/workflow_progress.py` - Progress tracker

### Testes

- `tests/test_workflow.py` - E2E integration, checkpointing, resume, cancellation

### Critérios de Aceitação

- Workflow executa end-to-end
- State persistido, checkpointing/resume funcionam
- Status atualizado em tempo real

---

## Fase 9: Polimento, Testes Completos e Documentação

**Objetivo:** Projeto production-ready com testes abrangentes.

### Backend

- `tests/integration/test_full_workflow.py` - E2E tests
- `tests/evasion/test_llm_evasion.py` - Security tests
- `backend/infrastructure/resilience/circuit_breaker.py` - Circuit breaker (Groq, DB, Valkey)
- `backend/infrastructure/security/rate_limit.py` - Enhanced rate limiting
- `docs/API.md` - API documentation
- `docs/ARCHITECTURE.md` - Architecture details

### Frontend

- `frontend/app/theme.py` - Theme consistente
- `frontend/app/components/loading.py` - Custom loading states
- `docs/USER_GUIDE.md` - User guide
- `frontend/app/pages/help.py` - Help page

### Testes

- `tests/security/test_security.py` - Injection, XSS
- `tests/performance/test_load.py` - 100 concurrent requests

### Critérios de Aceitação

- Coverage > 80%, todos testes passam
- p95 latency < 5s para workflow
- Circuit breaker e rate limiting funcionam
- Documentação completa (API, User Guide, README)

---

## Resumo das Fases

| Fase | Principal | Backend | Frontend | Critério |
|------|-----------|---------|----------|----------|
| 1 | Fundação | Infraestrutura completa | App base + health | Serviços saudáveis |
| 2 | PDF | Upload + processamento + cache | File uploader + preview | Upload com idempotência |
| 3 | Pré-requisitos | Extração LLM + knowledge graph | Lista + graph viz | Pré-requisitos extraídos |
| 4 | Avaliação | Geração de questões | Lista de questões | Questões balanceadas |
| 5 | Quiz | Avaliação (deterministic + LLM) | Quiz interativo | Score calculado |
| 6 | Readiness | Gap detection + scoring | Score + gaps list | Gaps identificados |
| 7 | Nivelamento | Conteúdo personalizado | Explicações + timeline | Plano gerado |
| 8 | Workflow | LangGraph orquestração | Status em tempo real | E2E funciona |
| 9 | Polimento | Testes + resilience + docs | Theme + help | Production-ready |

---

## Arquitetura de Storage

```
┌─────────────┐
│ PDF Upload  │
└──────┬──────┘
       │
       ▼
┌─────────────────────────┐
│  1. Calcular SHA-256     │
│  2. Verificar cache     │
└────────────┬────────────┘
             │
             ▼
     ┌───────────────┐
     │ Existe no DB? │
     └───┬───────┬───┘
         │ SIM   │ NÃO
         ▼       ▼
    ┌──────┐  ┌─────────────────┐
    │Reuse │  │ Upload S3       │
    └──────┘  │ (Minio)         │
              └────────┬─────────┘
                       ▼
              ┌─────────────────┐
              │ Extrair texto   │
              │ (PyPDF2)        │
              └────────┬─────────┘
                       ▼
              ┌─────────────────┐
              │ Salvar metadata  │
              │ no PostgreSQL   │
              └────────┬─────────┘
                       ▼
              ┌─────────────────┐
              │ Cache Valkey    │
              └─────────────────┘
```

**Vantagens desta arquitetura:**

- **Containers Dedicados**: S3 (Minio) + PostgreSQL + Valkey em containers independentes.
- PDFs no S3: escalável, custo menor, não polui o DB.
- PostgreSQL leve: apenas metadados relacionais.
- Presigned URLs: download seguro com expiração.
- Cache Valkey: evita reprocessamento, protocolo Redis compatível.
- Deploy isolado: portas exclusivas para evitar conflitos locais.

**Configuração Local:**

- S3 endpoint: `http://localhost:9005`
- PostgreSQL: `localhost:5435`
- Valkey: `localhost:6385`
- AWS credentials (Minio): `minioadmin`

---

## LLM Abstraction Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Application Layer                 │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Dependency Injection (DI) Setup                 │
│         (FastAPI Depends + Provider Factory)                │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  Prerequisite│  │ Assessment   │  │   Leveling   │
│   Service    │  │   Service    │  │   Service    │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │
       └─────────────────┼─────────────────┘
                         │
                         ▼
         ┌───────────────┴───────────────┐
         │        ILLMProvider           │  ← Interface Abstrata
         │  (generate_structured()      │
         │   generate_text()            │
         │   stream())                  │
         └───────────────┬───────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  GroqProvider│  │OpenAIProvider│  │AnthropicProv.│
└──────────────┘  └──────────────┘  └──────────────┐
         │               │               │
         └───────────────────────────────┼────────────────┘
                         │
                         ▼
         ┌───────────────────────────────┐
         │    Resilience Layer           │
         │  (Retry, Timeout, Circuit     │
         │   Breaker, Fallback Chain)     │
         └───────────────────────────────┘
```

**Vantagens desta arquitetura:**

- **Provider Independence**: Troca Groq → OpenAI via LLM_PROVIDER=... (sem mudar código)
- **Dependency Injection**: Serviços dependem de ILLMProvider, não de implementações concretas
- **Testabilidade**: MockProvider permite testes sem chamadas reais
- **Resiliência**: Retry, Circuit Breaker, Fallback Chain integrados
- **Configuração Centralizada**: LLM_CONFIG via environment variables

**Interface ILLMProvider:**

```python
class ILLMProvider(ABC):
    @abstractmethod
    async def generate_structured(self, prompt: str, response_model: Type[T]) -> T

    @abstractmethod
    async def generate_text(self, prompt: str) -> str

    @abstractmethod
    def get_provider_name(self) -> str
```

**Configuração:**

```bash
LLM_PROVIDER=groq|openai|anthropic|mock
GROQ_API_KEY=xxx
OPENAI_API_KEY=xxx
ANTHROPIC_API_KEY=xxx
LLM_PRIMARY_MODEL=llama-3.3-70b
LLM_FALLBACK_MODEL=deepseek-r1
```

**Uso em Serviços:**

```python
class PrerequisiteService:
    def __init__(
        self,
        llm: ILLMProvider = Depends(get_llm_provider)  # DI!
    ):
        self._llm = llm

    async def extract_prerequisites(self, text: str):
        # Usa interface abstrata - não sabe se é Groq, OpenAI, etc
        return await self._llm.generate_structured(...)
```

---

## Workflow Completo

```
PDF Lesson
    ↓
Extract Prerequisites (LLM)
    ↓
Build Knowledge Graph
    ↓
Generate Assessment (LLM)
    ↓
Student Quiz (MC=deterministic, SA/Calc=LLM)
    ↓
Calculate Readiness Score (weighted)
    ↓
Detect Gaps & Strengths
    ↓
Generate Leveling Content (LLM)
    ↓
Personalized Study Plan
```

---

## Arquivos Críticos por Fase

**Fase 1:**

- `docker-compose.yml` - Postgres + Valkey + Minio
- `pyproject.toml" - Dependências (incluindo redis-py para Valkey)
- `backend/main.py` - FastAPI entry point
- `backend/infrastructure/telemetry/tracer.py` - OpenTelemetry
- `backend/infrastructure/database.py` - PostgreSQL
- `backend/infrastructure/cache.py` - Valkey client
- `backend/infrastructure/storage.py` - S3 (Minio)

**Fase 2:**

- `backend/domain/models/pdf.py` - PDF model
- `backend/services/pdf_service.py` - PDF processing
- `backend/infrastructure/storage/pdf_storage.py` - S3 operations
- `backend/api/routes/pdf.py` - Upload endpoint

**Fase 3:**

- `backend/domain/models/prerequisite.py` - Prerequisite models
- `backend/llm/providers/groq_provider.py` - Groq integration
- `backend/llm/prompts/prerequisite_extractor_v1.txt` - Prompt

**Fase 8:**

- `backend/workflows/readiness_graph.py` - LangGraph workflow
- `backend/workflows/states.py` - State models

**Fase 9:**

- `tests/integration/test_full_workflow.py` - E2E tests
- `docs/API.md` - API documentation
- `docs/USER_GUIDE.md` - User guide

---

## Cronograma Estimado

- Fase 1: 2-3 dias
- Fase 2: 3-4 dias
- Fase 3: 4-5 dias
- Fase 4: 3-4 dias
- Fase 5: 4-5 dias
- Fase 6: 3-4 dias
- Fase 7: 4-5 dias
- Fase 8: 5-6 dias
- Fase 9: 5-7 dias

**Total:** 33-43 dias (~6-8 semanas)

---

## Próximos Passos

1. Começar pela **Fase 1** (fundação)
2. Seguir sequencialmente pelas fases 2-8
3. Finalizar com **Fase 9** (polimento)
4. Testar cada fase antes de prosseguir
