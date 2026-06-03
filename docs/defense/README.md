# Defesa Técnica - Índice

Este diretório contém a documentação de defesa técnica para o **Adaptive Leveling System**, organizada por fases de implementação. O objetivo destes documentos é detalhar o racional técnico, as decisões arquiteturais e as práticas de **AI Engineering** e **AI Ops** aplicadas ao longo do desenvolvimento.

## Índice de Defesas por Fase

### 🏗️ Base e Infraestrutura

* **[Fase 1: Fundação & Infraestrutura](fase_1_fundacao.md)**
  * *Foco:* Arquitetura Local com Containers Dedicados (Postgres, Valkey, Minio).
  * *Destaques:* Camada Agnóstica de LLM (DI), OpenTelemetry (Jaeger), CI/CD (GitHub Actions), Logs Estruturados (Loguru), Testes Automatizados (81% coverage).

### 📄 Processamento de Dados

* **[Fase 2: Upload e Processamento de PDF](fase_2_upload.md)**
  * *Foco:* Idempotência (SHA-256), S3 Integration, Extração Textual com `pypdf`.

### 🧠 Engenharia de IA

* **[Fase 3: Extração de Pré-requisitos com LLM](fase_3_extracao_llm.md)**
  * *Foco:* Structured Outputs, Knowledge Graph, Prompt Engineering com Noise Tolerance, Classificação de Importância (Critical/Important/Helpful).
* **[Fase 4: Geração de Avaliação Diagnóstica](fase_4_avaliacao.md)**
  * *Foco:* Geração balanceada de questões (MC, SA, Calc), templates versionados, validação de distribuição.
* **[Fase 5: Avaliação do Estudante (LLM-as-a-Judge)](fase_5_quiz.md)**
  * *Foco:* Correção híbrida (determinística para MC, LLM para SA/Calc), sessão com auto-save.
* **[Fase 6: Detecção de Gaps e Análise de Prontidão](fase_6_readiness.md)**
  * *Foco:* Scoring ponderado (Critical 3x, Important 2x, Helpful 1x), thresholds de nivelamento.
* **[Fase 7: Geração de Conteúdo de Nivelamento](fase_7_leveling.md)**
  * *Foco:* Conteúdo personalizado por gap, estudo ordenado por criticidade.

### ⚙️ Orquestração e Qualidade

* **[Fase 8: Orquestração de Workflow (LangGraph)](fase_8_workflow.md)**
  * *Foco:* StateGraph, checkpointing, resumo de workflows, paralelismo.
* **[Fase 9: Polimento e Testes E2E](fase_9_polimento.md)**
  * *Foco:* Testes de segurança, performance (p95 < 5s), documentação completa.

---

*Nota ao Avaliador: Esta documentação é um reflexo do compromisso com a transparência técnica e a maturidade de engenharia de software aplicada a projetos de Inteligência Artificial.*
