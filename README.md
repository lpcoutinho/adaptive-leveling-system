# Adaptive Leveling System

[![CI](https://github.com/lpcoutinho/adaptive-leveling-system/actions/workflows/ci.yml/badge.svg)](https://github.com/lpcoutinho/adaptive-leveling-system/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/lpcoutinho/adaptive-leveling-system/branch/main/graph/badge.svg)](https://codecov.io/gh/lpcoutinho/adaptive-leveling-system)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

Sistema de nivelamento adaptativo powered by IA para avaliação de prontidão educacional e geração de conteúdo personalizado em educação superior.

## 🎯 Visão Geral

O **Adaptive Leveling System** é uma plataforma que utiliza Large Language Models (LLMs) para:

- **Analisar** aulas em PDF e extrair pré-requisitos fundamentais.
- **Avaliar** a prontidão de estudantes através de quizes diagnósticos gerados sob medida.
- **Identificar** gaps de conhecimento com análise ponderada por importância.
- **Gerar** conteúdo de nivelamento personalizado (Explicação + Exemplo + Exercício) para cada gap.

## 🏗️ Arquitetura e AI Ops

```
Streamlit (Frontend) → FastAPI (API Layer)
                                ↓
                      Services (Business Logic) ↔ LangGraph (Orchestration)
                                ↓
      PostgreSQL 16 + Valkey 8 + Minio (S3) + LLM Providers (Groq/OpenAI)
```

### Decisões de Engenharia

- **LLM Abstraction Layer**: Interface agnóstica permitindo troca de modelos e testes via **MockProvider** sem custo de API.
- **LangGraph Orchestration**: Gerenciamento de estado complexo com suporte a interrupção (Human-in-the-loop) e retomada de processos.
- **Idempotência & Cache**: Hashing SHA-256 para PDFs e cache em Valkey para evitar reprocessamento de inteligência.
- **Observabilidade Enterprise**: Telemetria distribuída nativa via **OpenTelemetry** e rastreamento de spans no **Jaeger**.

## 🚀 Quick Start

### Pré-requisitos

- Docker e Docker Compose
- Python 3.12
- Poetry

### Execução Rápida

```bash
# Clone e Setup (infra + dependências + migrations)
git clone https://github.com/lpcoutinho/adaptive-leveling-system.git
cd adaptive-leveling-system
make setup

# Iniciar aplicações (Terminais separados)
make backend
make frontend

# Ver saúde e telemetria
make health
# Jaeger UI: http://localhost:16686
```

## 🔧 Configuração e Chaves de API

O sistema utiliza o arquivo `.env` para gerenciar segredos.

### 🔑 Chave de Avaliação (Groq)

Para facilitar a avaliação técnica via Groq, disponibilizamos uma chave temporária:

```bash
LLM_PROVIDER=groq
GROQ_API_KEY=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
```

*Aviso: Esta chave expira em **11/06/2026**. Documentada exclusivamente para fins de avaliação.*

## 📦 Serviços e Infraestrutura

| Serviço | Porta | Descrição |
|---------|-------|-----------|
| Backend (FastAPI) | 8000 | API REST, Documentação (/docs) e Orquestração |
| Frontend (Streamlit) | 8501 | Interface unificada (Home, Quiz e Diagnóstico) |
| PostgreSQL 16 | 5435 | Persistência de metadados, inteligência e checkpoints |
| Valkey 8 | 6385 | Cache distribuído e gerenciamento de sessões |
| Minio S3 | 9005 | Armazenamento persistente de documentos PDF |
| Jaeger | 16686 | Visualização de traces distribuídos (OpenTelemetry) |

## 🎯 Status do Desenvolvimento

| Fase | Status | Destaque |
|------|--------|----------|
| 1. Fundação | ✅ | Infraestrutura Real (Containers), CI/CD e OTel |
| 2. Upload | ✅ | Processamento Idempotente e Extração Textual |
| 3. Inteligência | ✅ | Extração de Pré-requisitos com Structured Output |
| 4. Avaliação | ✅ | Geração balanceada de questões diagnósticas |
| 5. Quiz | ✅ | Motor de correção híbrido (Determinístico + IA) |
| 6. Prontidão | ✅ | Diagnóstico ponderado e mapeamento de forças |
| 7. Nivelamento | ✅ | Conteúdo estruturado WEEE (Why, Explanation, Example, Exercise) |
| 8. Orquestração | ✅ | Workflow Automático via LangGraph com Quiz embutido |
| 9. Polimento | 🏗️ | Resiliência (Circuit Breaker) e Documentação Final |

## 📈 Próximos Passos (Roadmap de Escala)

- **Monitoramento de Prompt (Langfuse)**: Auditagem de qualidade, custos por token e detecção de alucinações.
- **Painéis Operacionais (Grafana)**: Dashboards de latência p99, taxas de erro de LLM e métricas de infraestrutura.
- **Processamento em Background (Celery)**: Migração de tarefas pesadas de IA para filas assíncronas para suportar alta concorrência.
- **RAG & pgvector**: Evolução para busca semântica em repositórios de aulas em larga escala.

## 🧪 Qualidade

```bash
# Executar suíte de testes (Unitários + Integração)
make test

# Verificar cobertura (Atualmente ~81%)
make test-cov
```

---
**Desenvolvido como parte de avaliação técnica em Engenharia de IA.**
