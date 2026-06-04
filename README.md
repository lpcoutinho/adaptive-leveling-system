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
                              PostgreSQL 16 + Valkey 8 + Minio (S3) + LLM Providers
```

### Decisões Arquiteturais

- **LLM Abstraction Layer**: Interface agnóstica com suporte a Groq, OpenAI, Anthropic e Mock.
- **LangGraph**: Orquestração explícita de workflows com gerenciamento de estado e checkpointing.
- **Idempotência via SHA-256**: Cache de resultados no DB para evitar reprocessamento e custos de API.
- **OpenTelemetry**: Telemetria distribuída nativa (Jaeger) para monitoramento de latência e debug de agentes.
- **Dedicated Infrastructure**: Containers reais (não simulados) para garantir paridade com produção.

## 🚀 Quick Start

### Pré-requisitos

- Docker e Docker Compose
- Python 3.12
- Poetry

### Setup e Execução

```bash
# Clone o repositório
git clone https://github.com/lpcoutinho/adaptive-leveling-system.git
cd adaptive-leveling-system

# Setup completo (infra + dependências + migrations + pre-commit)
make setup

# Iniciar aplicações (em terminais separados)
make backend
make frontend

# Ver saúde dos serviços
make health
```

## 📦 Serviços e Portas

| Serviço | Porta | Descrição |
|---------|-------|-----------|
| Backend (FastAPI) | 8000 | API REST e Documentação (/docs) |
| Frontend (Streamlit) | 8501 | Interface do Aluno |
| PostgreSQL | 5435 | Banco de Dados (Metadados e Inteligência) |
| Valkey | 6385 | Cache e Sessões |
| Minio S3 | 9005/9006 | Armazenamento de PDFs (API/Console) |
| Jaeger | 16686 | UI de Tracing |

## 🎯 Status das Fases

| Fase | Status | Descrição |
|------|--------|-----------|
| 1. Fundação | ✅ Completo | Infraestrutura base, LLM Abstraction, CI/CD |
| 2. Upload PDF | ✅ Completo | Idempotência (SHA-256), S3 Integration, Extração |
| 3. Pré-requisitos| ✅ Completo | Extração estruturada (JSON) e Knowledge Graph |
| 4. Avaliação | ✅ Completo | Geração balanceada de questões diagnósticas |
| 5. Quiz Estudante| ✅ Completo | Interface interativa + Avaliação em lote (Batch) |
| 6. Gap Detection | ✅ Completo | Scoring ponderado e análise de prontidão justa |
| 7. Leveling | ✅ Completo | Conteúdo personalizado (WEEE) e plano de estudo |
| 8. LangGraph | ✅ Completo | Orquestração end-to-end do workflow educacional |
| 9. Polimento | 🏗️ Em Progresso | Resiliência (Circuit Breaker), Performance e Docs |

## 🚀 Melhorias Futuras e AI Ops

Para elevar o projeto ao nível Enterprise, os seguintes pontos estão mapeados no roadmap:

### 1. Observabilidade Avançada (Langfuse/LangSmith)

- Integração com **Langfuse** para monitoramento específico de LLM (custo por aluno, versões de prompt e feedback loop de qualidade).

### 2. Eficiência e Custos (Prompt Cache)

- Implementação de **Prompt Caching** e **Semantic Caching** no Valkey para reutilizar respostas de LLM em sub-tópicos comuns entre diferentes aulas.

### 3. Engenharia de IA (Hiperparâmetros)

- Externalização de hiperparâmetros do LLM (`temperature`, `top_p`, `max_tokens`) para o `.env`, permitindo ajustes finos por tópico sem alteração de código.

### 4. Resiliência e Escalabilidade

- **Fallback Chain**: Implementação de failover automático (ex: se Groq atingir rate limit, chaveia para OpenAI).
- **Background Tasks**: Migração de extrações pesadas para processos em segundo plano (Celery/RabbitMQ) para evitar timeouts em PDFs gigantes.
- **Circuit Breaker**: Bloqueio de chamadas a serviços externos instáveis para proteger a integridade do sistema.

### 5. Extração Multi-modal

- Evolução do extrator `pypdf` para modelos **Vision** (ex: GPT-4o) ou **Amazon Textract** para processar diagramas e fórmulas matemáticas complexas em imagens.

## 🧪 Qualidade e Testes

```bash
# Executar todos os testes
make test

# Verificar cobertura detalhada
make test-cov
```

**Cobertura atual**: ~81% (Foco em lógica de negócio e integração)

---
**Desenvolvido como parte de avaliação técnica em Engenharia de IA.**
