# Adaptive Leveling System

[![CI](https://github.com/lpcoutinho/adaptive-leveling-system/actions/workflows/ci.yml/badge.svg)](https://github.com/lpcoutinho/adaptive-leveling-system/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/lpcoutinho/adaptive-leveling-system/branch/main/graph/badge.svg)](https://codecov.io/gh/lpcoutinho/adaptive-leveling-system)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

Sistema de nivelamento adaptativo powered by IA para avaliação de prontidão educacional e geração de conteúdo personalizado em educação superior.

## 🎯 Visão Geral

O **Adaptive Leveling System** é uma plataforma que utiliza Large Language Models (LLMs) para:

- Extrair pré-requisitos de aulas de Cálculo I a partir de PDFs
- Avaliar a prontidão de estudantes através de questionários diagnósticos
- Identificar gaps de conhecimento com análise detalhada
- Gerar conteúdo de nivelamento personalizado para cada gap detectado

## 🏗️ Arquitetura

```
Streamlit (Frontend) → FastAPI (API Layer) → LangGraph (Workflow Orchestration)
                                                              ↓
                                                    Services (Business Logic)
                                                              ↓
                              PostgreSQL + Valkey + S3 + LLM Providers
```

### Decisões Arquiteturais

- **LLM Abstraction Layer**: Interface agnóstica com suporte a Groq, OpenAI, Anthropic e Mock
- **LangGraph**: Orquestração explícita de workflows com gerenciamento de estado
- **Idempotência via SHA-256**: Cache de resultados para evitar reprocessamento
- **OpenTelemetry**: Telemetria distribuída desde o primeiro dia (Jaeger)

## 🚀 Quick Start

### Pré-requisitos

- Docker e Docker Compose
- Python 3.12
- Poetry

### Setup

```bash
# Clone o repositório
git clone https://github.com/lpcoutinho/adaptive-leveling-system.git
cd adaptive-leveling-system

# Setup completo (infra + dependências + migrations + pre-commit)
make setup

# Ou manualmente
poetry install
docker-compose up -d
make migrate
pre-commit install
```

### Desenvolvimento

```bash
# Ver saúde dos serviços
make health

# Executar testes
make test

# Lint + type-check
make check

# Iniciar backend
make backend

# Iniciar frontend
make frontend
```

## 📦 Serviços

| Serviço | Porta | Descrição |
|---------|-------|-----------|
| Backend (FastAPI) | 8000 | API REST |
| Frontend (Streamlit) | 8501 | Interface web |
| PostgreSQL | 5435 | Banco de dados |
| Valkey | 6385 | Cache |
| Minio S3 | 9005/9006 | Armazenamento |
| Jaeger | 16686 | Tracing UI |

## 🧪 Testes

```bash
# Testes unitários e integração
make test

# Testes com coverage
make test-cov

# Testes específicos
pytest tests/test_database_connection.py -v
pytest tests/test_llm_interface.py -v
```

**Cobertura atual**: 81%

## 🔧 Configuração

Crie um arquivo `.env` a partir do `.env.example`:

```bash
cp .env.example .env
```

Configure as variáveis de ambiente:

```bash
# LLM Provider (groq|openai|anthropic|mock)
LLM_PROVIDER=mock

# API Keys
GROQ_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
```

## 📚 Documentação

- [Plano de Implementação](docs/guides/IMPLEMENTACAO.md) - Roadmap completo do projeto
- [Fase 1: Fundação](docs/guides/fase_1_fundacao.md) - Detalhes da fase atual
- [Defesa Técnica](docs/defense/README.md) - Decisões arquiteturais e racional

## 🧪 Makefile

Comandos úteis para desenvolvimento:

```bash
make help           # Lista todos os comandos disponíveis
make up             # Sobe containers
make down           # Para containers
make logs           # Logs dos containers
make db-shell       # Shell PostgreSQL
make cache-shell    # Shell Valkey
make clean          # Limpa arquivos gerados
make ci             # Simula pipeline CI completo
```

## 🎯 Fases de Implementação

| Fase | Status | Descrição |
|------|--------|-----------|
| 1. Fundação | ✅ Completo | Infraestrutura base, LLM Abstraction, CI/CD |
| 2. Upload PDF | ⏳ Planejado | Idempotência, S3, extração textual |
| 3. Pré-requisitos | ⏳ Planejado | LLM structured outputs, knowledge graph |
| 4. Avaliação | ⏳ Planejado | Geração de quiz diagnóstico |
| 5. Quiz Estudante | ⏳ Planejado | Interface + LLM-as-a-Judge |
| 6. Gap Detection | ⏳ Planejado | Análise de prontidão |
| 7. Leveling | ⏳ Planejado | Conteúdo personalizado |
| 8. LangGraph | ⏳ Planejado | Orquestração de workflow |
| 9. Polimento | ⏳ Planejado | E2E tests, resiliência |

## 🛡️ Qualidade

### CI/CD Pipeline

- **Lint**: Ruff (PEP 8, detecção de bugs)
- **Type Check**: MyPy com plugins Pydantic
- **Tests**: Pytest com infraestrutura real no GitHub
- **Coverage**: Codecov integration

### Pre-commit Hooks

- Formatação automática com Ruff
- Type checking antes do commit
- Verificação de segurança com Bandit

## 📖 Stack Tecnológica

**Backend**:

- Python 3.12 + FastAPI
- PostgreSQL 16 + Valkey 8
- Minio (S3-compatible)
- OpenTelemetry + Jaeger

**Frontend**:

- Streamlit
- Python 3.12

**LLM**:

- Groq (primary)
- OpenAI / Anthropic (alternativos)
- Mock (testes)

## 🤝 Contribuindo

Este é um projeto acadêmico em desenvolvimento. Para sugestões ou questões, abra uma issue.

## 📄 Licença

MIT License - Ver [LICENSE](LICENSE) para detalhes.

---

**Desenvolvido como parte de avaliação técnica em Engenharia de IA.**
