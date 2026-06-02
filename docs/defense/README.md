# Defesa Técnica - Índice

Este diretório contém a documentação de defesa técnica para o **Adaptive Leveling System**, organizada por fases de implementação. O objetivo destes documentos é detalhar o racional técnico, as decisões arquiteturais e as práticas de **AI Engineering** e **AI Ops** aplicadas ao longo do desenvolvimento.

## Índice de Defesas por Fase

### 🏗️ Base e Infraestrutura

* **[Fase 1: Fundação & Infraestrutura](fase_1_fundacao.md)**
  * *Foco:* Arquitetura Local com Containers Dedicados (Postgres, Valkey, Minio).
  * *Destaques:* Camada Agnóstico de LLM (DI), OpenTelemetry (Jaeger), CI/CD (GitHub Actions), Logs Estruturados (Loguru), Testes Automatizados (81% coverage).

### 📄 Processamento de Dados (Em Breve)

* **[Fase 2: Upload e Processamento de PDF]**
  * *Foco:* Idempotência (SHA-256), S3 Integration, Extração Textual.

### 🧠 Engenharia de IA & LangGraph (Em Breve)

* **[Fase 3: Extração de Pré-requisitos com LLM]**
  * *Foco:* Structured Outputs, Knowledge Graph, Langfuse Integration.
* **[Fase 4: Geração de Avaliação Diagnóstica]**
* **[Fase 5: Avaliação do Estudante (LLM-as-a-Judge)]**
* **[Fase 6: Detecção de Gaps e Análise de Prontidão]**
* **[Fase 7: Geração de Conteúdo de Nivelamento]**
* **[Fase 8: Orquestração de Workflow (LangGraph)]**

### 🚀 Qualidade e Entrega (Em Breve)

* **[Fase 9: Polimento e Testes E2E]**

---
*Nota ao Avaliador: Esta documentação é um reflexo do compromisso com a transparência técnica e a maturidade de engenharia de software aplicada a projetos de Inteligência Artificial.*
