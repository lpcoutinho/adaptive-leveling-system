# Plano de Implementação - Adaptive Leveling System

## Contexto

Este plano implementa o **Case 1 - Nivelamento** do desafio técnico, usando LLM para extrair pré-requisitos de uma aula de Cálculo I, analisar a prontidão do aluno e gerar conteúdo de nivelamento personalizado.

**Estratégia:** Full Stack Vertical (cada fase com backend + frontend + testes + observabilidade completos).

**Status Atual:** As fases 1 a 8 foram concluídas com sucesso, estabelecendo um workflow orquestrado e inteligente.

---

## Roadmap de Execução

| Fase | Título | Status | Destaques Técnicos |
|------|--------|--------|-------------------|
| 1 | Fundação | ✅ | Postgres, Valkey, Minio, OpenTelemetry, CI/CD |
| 2 | Upload PDF | ✅ | Idempotência (SHA-256), S3, Extração `pypdf` |
| 3 | Pré-requisitos | ✅ | LLM Structured Output, Knowledge Graph |
| 4 | Avaliação | ✅ | Geração balanceada 40/30/30 (MC/SA/Calc) |
| 5 | Quiz | ✅ | Correção Híbrida (Batch para SA/Calc) |
| 6 | Readiness | ✅ | Scoring ponderado justo, mapeamento de gaps |
| 7 | Leveling | ✅ | Conteúdo personalizado estrutura WEEE |
| 8 | Workflow | ✅ | LangGraph orquestração e persistência de estado |
| 9 | Polimento | 🏗️ | Circuit Breaker, Performance e Documentação Final |

---

## 🚀 Melhorias de Engenharia e AI Ops (Fases Futuras)

Para evoluir o sistema para um padrão de produção crítica (Enterprise Grade), as seguintes melhorias foram identificadas:

### 1. Engenharia de IA & Eficiência

- **Prompt Caching**: Implementação de cache semântico para evitar chamadas duplicadas ao LLM para tópicos matemáticos idênticos em diferentes aulas.
- **Dynamic Parameters**: Externalização de `temperature`, `top_p` e `seed` para o `.env`, permitindo ajustes de criatividade sem deploys.
- **Feedback Loop**: Interface para o professor "curar" os pré-requisitos extraídos, servindo de dataset para fine-tuning futuro.

### 2. Observabilidade de LLM

- **Langfuse Integration**: Monitoramento de traces de agentes, controle de custos por token e comparação de performance entre versões de prompts.
- **Detailed Metrics**: Painel de latência por nó do LangGraph no Jaeger/Grafana.

### 3. Resiliência Operacional

- **Fallback Chain**: Chaveamento automático entre provedores (Groq → OpenAI → local LLM) em caso de indisponibilidade ou rate limiting.
- **Circuit Breaker**: Proteção contra falhas em cascata em serviços de infraestrutura (Cache/DB).
- **Asynchronous Processing**: Migração de tarefas de longa duração (extração de PDF e LLM) para filas (Celery) com WebSockets para notificação do frontend.

### 4. Escalabilidade de Dados

- **pgvector**: Transição do `content_text` simples para um sistema de busca semântica (RAG) permitindo processar livros inteiros em vez de apenas slides.
- **OCR Multi-modal**: Integração com modelos Vision para leitura de gráficos e equações desenhadas à mão em PDFs escaneados.

---

## Guia por Fase (Detalhado)

Consulte os arquivos específicos para o detalhamento técnico de cada etapa:

- [Fase 1: Fundação](fase_1_fundacao.md)
- [Fase 2: Upload e Processamento](fase_2_upload.md)
- [Fase 3: Extração com LLM](fase_3_extracao_llm.md)
- [Fase 4+: Consultar código-fonte e testes]

---

## Critérios de Qualidade Transversais

Em todas as fases, os seguintes padrões são obrigatórios:

- **Type Checking**: 100% aprovado no MyPy.
- **Linting**: 0 avisos no Ruff.
- **Testing**: Cobertura > 80% (unitários + integração).
- **Surgical Commits**: Commits granulares e mensagens semânticas.

---
*Nota: Este documento é o guia vivo de evolução do projeto Adaptive Leveling System.*
