# Fase 1: Fundação e Infraestrutura Base

## Contexto

Este plano implementa a **Fase 1** do Adaptive Leveling System: Fundação e Infraestrutura Base. O projeto está atualmente vazio (apenas documentação), então começaremos do zero.

**Objetivo:** Estabelecer toda a fundação técnica com infraestruturas críticas configuradas e testadas.

**Stack:**

- Python 3.12 com Poetry/pip
- FastAPI (backend API)
- Streamlit (frontend)
- Postgres + Valkey + Minio
- OpenTelemetry + Loguru (observabilidade)
- Jaeger (tracing distribuído)
- LLM Abstraction Layer (Groq, Mock)

---

## Estrutura de Arquivos

```
adaptive-leveling-system/
├── pyproject.toml                    # Dependências
├── poetry.lock                       # Lock file
├── docker-compose.yml                # Containers
├── .env.example                      # Exemplo de env vars
├── .gitignore                        # (já criado)
├── .pre-commit-config.yaml          # Pre-commit hooks
├── Makefile                          # Comandos de desenvolvimento
├── .github/workflows/ci.yml          # CI/CD pipeline
│
├── backend/
│   ├── __init__.py
│   ├── main.py                       # FastAPI app factory
│   ├── config.py                     # Config centralizada
│   │
│   ├── llm/                         # LLM Abstraction Layer
│   │   ├── __init__.py
│   │   ├── base/
│   │   │   ├── __init__.py
│   │   │   └── interface.py          # ILLMProvider
│   │   ├── config.py                 # LLMConfig
│   │   ├── factory.py                # Provider factory
│   │   ├── providers/
│   │   │   ├── __init__.py
│   │   │   ├── groq_provider.py     # Groq implementation
│   │   │   └── mock_provider.py     # Mock for tests
│   │   └── prompts/
│   │       └── .gitkeep
│   │
│   ├── infrastructure/
│   │   ├── __init__.py
│   │   ├── database.py               # PostgreSQL connection
│   │   ├── cache.py                  # Valkey client
│   │   ├── storage.py                # S3 client
│   │   ├── security.py               # Validation, rate limit
│   │   └── telemetry/
│   │       ├── __init__.py
│   │       ├── tracer.py             # OpenTelemetry
│   │       ├── metrics.py            # Custom metrics
│   │       └── logger.py             # Loguru wrapper
│   │
│   └── api/
│       ├── __init__.py
│       ├── dependencies/
│       │   ├── __init__.py
│       │   └── llm.py                 # FastAPI dependencies
│       └── routes/
│           ├── __init__.py
│           └── health.py              # Health check
│
├── migrations/
│   └── 001_initial_schema.sql
│
├── frontend/
│   └── app/                          # Renomeado de 'streamlit' para evitar conflitos
│       ├── __init__.py
│       ├── app.py                    # Main app
│       ├── config.py                 # Frontend config
│       └── pages/
│           ├── __init__.py
│           └── health.py              # Health page
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                   # Fixtures
│   ├── test_infrastructure.py        # Infraestrutura geral
│   ├── test_database_connection.py   # Testes específicos de DB
│   ├── test_cache_connection.py      # Testes específicos de Cache
│   ├── test_storage_connection.py    # Testes específicos de S3
│   ├── test_llm_interface.py         # Testes da interface LLM
│   └── test_api_health.py            # Health endpoints
│
└── docs/
    └── defense/                      # Documentação de defesa técnica
        ├── README.md
        └── fase_1_fundacao.md
```

---

## Tarefas Sequenciais

### Tarefa 1: Configuração Inicial

**Arquivos:**

- `pyproject.toml` - Dependências completas
- `.env.example` - Template de environment variables
- `docker-compose.yml` - Infrastructure configuration (Postgres, Valkey, Minio)

**Dependências do pyproject.toml:**

```toml
[tool.poetry.dependencies]
python = "^3.12"
fastapi = "^0.115.0"
uvicorn = {extras = ["standard"], version = "^0.32.0"}
pydantic = "^2.10.0"
pydantic-settings = "^2.6.0"
pydantic-ai = "^0.0.14"
groq = "^0.11.0"
boto3 = "^1.35.0"
redis = {extras = ["valkey"], version = "^5.2.0"}
psycopg2-binary = "^2.9.10"
opentelemetry-api = "^1.28.0"
opentelemetry-sdk = "^1.28.0"
opentelemetry-instrumentation-fastapi = "^0.49b0"
opentelemetry-exporter-otlp = "^1.28.0"
loguru = "^0.7.2"
python-multipart = "^0.0.12"
aiofiles = "^24.1.0"
httpx = "^0.28.0"
pytest = "^8.3.0"
pytest-asyncio = "^0.24.0"
pytest-cov = "^6.0.0"
```

---

### Tarefa 2: LLM Abstraction Layer

**Arquivos:**

1. `backend/llm/base/interface.py` - Interface ILLMProvider
2. `backend/llm/config.py` - LLMConfig (pydantic-settings)
3. `backend/llm/factory.py` - Provider factory
4. `backend/llm/providers/groq_provider.py` - Groq implementation
5. `backend/llm/providers/mock_provider.py` - Mock for tests
6. `backend/api/dependencies/llm.py` - FastAPI dependencies

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

---

### Tarefa 3: Configuração Centralizada

**Arquivos:**

1. `backend/config.py` - Settings (pydantic-settings)

**Configurações:**

```python
class Settings(BaseSettings):
    # App
    APP_NAME: str = "Adaptive Leveling System"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database (PostgreSQL)
    DATABASE_URL: str = "postgresql://postgres:postgres@127.0.0.1:5435/postgres?sslmode=disable"

    # Cache (Valkey)
    REDIS_URL: str = "redis://127.0.0.1:6385/0"

    # Storage (S3/Minio)
    AWS_ACCESS_KEY_ID: str = "minioadmin"
    AWS_SECRET_ACCESS_KEY: str = "minioadmin"
    AWS_REGION: str = "us-east-1"
    S3_ENDPOINT_URL: str = "http://127.0.0.1:9005"
    S3_BUCKET: str = "als-documents"

    # LLM
    LLM_PROVIDER: str = "groq"
    GROQ_API_KEY: str = ""

    # OpenTelemetry
    OTEL_EXPORTER_OTLP_ENDPOINT: str = "http://localhost:4318"
```

---

### Tarefa 4: Infraestrutura de Telemetria

**Arquivos:**

1. `backend/infrastructure/telemetry/tracer.py` - OpenTelemetry setup
2. `backend/infrastructure/telemetry/metrics.py` - Custom metrics
3. `backend/infrastructure/telemetry/logger.py` - Loguru wrapper

**Tracer:**

```python
def setup_telemetry(service_name: str) -> None:
    # Configure OpenTelemetry with OTLP exporter
    # Auto-instrument FastAPI, HTTP, asyncio
```

---

### Tarefa 5: Infraestrutura de Dados

**Arquivos:**

1. `backend/infrastructure/database.py` - PostgreSQL connection pool
2. `backend/infrastructure/cache.py" - Valkey client com serialization
3. `backend/infrastructure/storage.py` - S3 client (Minio) com presigned URLs
4. `migrations/001_initial_schema.sql` - Schema inicial

**Schema SQL:**

```sql
CREATE TABLE IF NOT EXISTS pdf_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hash VARCHAR(64) UNIQUE NOT NULL,
    filename VARCHAR(255) NOT NULL,
    size BIGINT NOT NULL,
    bucket_key VARCHAR(500) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_pdf_documents_hash ON pdf_documents(hash);
```

---

### Tarefa 6: FastAPI Application

**Arquivos:**

1. `backend/main.py` - App factory com middleware
2. `backend/api/routes/health.py` - Health check endpoint
3. `backend/infrastructure/security.py` - Input validation, rate limiting

**main.py:**

```python
def create_app() -> FastAPI:
    app = FastAPI(title="Adaptive Leveling System")
    setup_cors(app)
    setup_telemetry(settings.APP_NAME)
    setup_exception_handlers(app)
    include_routes(app)
    return app
```

---

### Tarefa 7: Frontend Streamlit

**Arquivos:**

1. `frontend/app/app.py` - Main app com sidebar
2. `frontend/app/config.py` - Frontend config
3. `frontend/app/pages/health.py` - Health status page

**app.py:**

```python
def main():
    st.set_page_config(page_title="Adaptive Leveling System")
    sidebar = st.sidebar
    # Navigation, API status display
```

---

### Tarefa 8: Testes de Infraestrutura

**Arquivos:**

1. `tests/conftest.py` - Fixtures para DB, cache, HTTP client
2. `tests/test_infrastructure.py` - Testes de conexão
3. `tests/test_api_health.py` - Testes de health endpoint

**conftest.py:**

```python
@pytest.fixture
async def db_connection():
    # Test PostgreSQL connection

@pytest.fixture
async def cache_client():
    # Test Valkey connection

@pytest.fixture
async def http_client():
    async with httpx.AsyncClient() as client:
        yield client
```

---

## Ordem de Execução

1. **Setup** (30min): pyproject.toml, docker-compose.yml, .env.example
2. **LLM Layer** (2h): interface, config, factory, providers, DI
3. **Config** (30min): backend/config.py
4. **Telemetry** (1h): tracer, metrics, logger
5. **Infrastructure** (1.5h): database, cache, storage, security
6. **FastAPI** (1h): main.py, health.py
7. **Frontend** (1h): Streamlit app + health page
8. **Tests** (1h): conftest, test_infrastructure, test_api_health
9. **Quality** (1h): Pre-commit, Makefile, CI/CD, Type Checking
10. **Integration** (30min): docker-compose up, test end-to-end

**Total estimado:** ~9-10 horas

---

## Ferramentas de Desenvolvimento

### Makefile

Comandos essenciais para desenvolvimento:

```bash
make help          # Lista todos os comandos
make setup         # Setup completo (install + up + migrate + pre-commit)
make up            # Sobe containers
make down          # Para containers
make test          # Executa testes
make check         # Lint + type-check
make backend       # Inicia backend
make frontend      # Inicia frontend
make health        # Verifica saúde dos serviços
make clean         # Limpa caches e arquivos temporários
make clean-poetry  # Remove o virtualenv do Poetry
make clean-all     # Limpeza total (arquivos + venv + docker volumes)
```

### Pre-commit Hooks

Verificações automáticas antes de cada commit:

- Ruff (linting + formatting)
- MyPy (type checking)
- Bandit (security)
- Markdown lint

Instalação:

```bash
pip install pre-commit
pre-commit install
```

### CI/CD (GitHub Actions)

Pipeline automatizado que executa:

1. **Lint Job**: Ruff check + format verification
2. **Type-check Job**: MyPy com Pydantic plugins
3. **Test Job**: Sobe infraestrutura, executa migrations, roda testes com coverage

---

## Critérios de Aceitação

- [x] Backend inicia sem erros (`uvicorn backend.main:app`)
- [x] Health check retorna 200 (`GET /health`)
- [x] Containers (S3, DB, Cache) conectam
- [x] Traces visíveis no console (OpenTelemetry)
- [x] Frontend Streamlit inicia e mostra status
- [x] Upload/download no Minio funciona
- [x] Valkey cache operations funcionam
- [x] Todos os testes passam
- [x] Pre-commit hooks configurados
- [x] CI/CD pipeline funcionando
- [x] MyPy type checking passando
- [x] 81% de cobertura de testes

**Status: FASE 1 COMPLETA ✅**

---

## Verificação Final

### Via Makefile (Recomendado)

```bash
# Setup completo
make setup

# Verificar saúde dos serviços
make health

# Executar testes com coverage
make test-cov

# Verificar código
make check

# Iniciar aplicações
make backend    # Terminal 1
make frontend   # Terminal 2
```

### Manualmente

```bash
# 1. Iniciar containers
docker-compose up -d

# 2. Instalar dependências
poetry install

# 3. Configurar pre-commit
pre-commit install

# 4. Configurar environment
cp .env.example .env
# Editar .env com chaves API

# 5. Rodar migrations (porta 5435)
make migrate

# 6. Iniciar backend
LLM_PROVIDER=mock uvicorn backend.main:app --reload

# 7. Testar health
curl http://localhost:8000/health

# 8. Acessar Traces (Jaeger)
# Abra no navegador: http://localhost:16686

# 9. Iniciar frontend
streamlit run frontend/app/app.py

# 10. Rodar testes
pytest tests/ -v --cov=backend
```

---

## Arquivos Críticos

**Infraestrutura:**

- `docker-compose.yml` - Postgres + Valkey + Minio
- `pyproject.toml` - Dependências

**LLM Abstraction:**

- `backend/llm/base/interface.py` - Interface ILLMProvider
- `backend/llm/config.py` - LLMConfig
- `backend/llm/factory.py` - Provider factory
- `backend/llm/providers/groq_provider.py` - Groq implementation
- `backend/api/dependencies/llm.py` - FastAPI DI

**Core:**

- `backend/config.py` - Settings
- `backend/main.py` - FastAPI app
- `backend/infrastructure/database.py` - PostgreSQL
- `backend/infrastructure/cache.py` - Valkey
- `backend/infrastructure/storage.py` - S3 (Minio)

**Telemetria:**

- `backend/infrastructure/telemetry/tracer.py` - OpenTelemetry
- `backend/infrastructure/telemetry/logger.py` - Loguru

**Testes:**

- `tests/conftest.py` - Fixtures
- `tests/test_infrastructure.py` - DB, cache, storage
- `tests/test_api_health.py` - Health endpoint

---

## Próximos Passos

Após completar a Fase 1:

1. Validar todos os critérios de aceitação
2. Documentar aprendizados
3. Seguir para **Fase 2: Upload e Processamento de PDF**
