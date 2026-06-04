# Documentação - Adaptive Leveling System

Este diretório contém a documentação técnica e estratégica do projeto, organizada para facilitar a auditoria e a evolução contínua por diferentes perfis (Desenvolvedores, Arquitetos e POs).

## 📁 Estrutura de Diretórios

```text
docs/
├── defense/         # Racional técnico e justificativas por fase (AI Ops)
├── guides/          # Roadmaps detalhados de implementação e execução
├── architecture/    # Visão geral, diagramas e stack tecnológica
└── references/      # Materiais de apoio e descrição do desafio original
```

## 📖 Principais Documentos

### 🏗️ Estratégia e Visão

- **[Plano Diretor (Architecture PLAN)](architecture/PLAN.md)**: A "bíblia" do projeto. Contém o design sistêmico, escolha de tecnologias e visão de longo prazo (pgvector, RAG).
- **[Roadmap de Implementação](guides/IMPLEMENTACAO.md)**: O guia vivo de status. Mostra quais fases foram concluídas e o que está planejado para o futuro da plataforma.

### 🛡️ Defesa Técnica (AI Engineering & Ops)

Para entender o **porquê** das decisões (ex: por que containers reais e não simuladores? por que OpenTelemetry?), consulte o índice de defesas:

- **[Índice de Defesa Técnica](defense/README.md)**

### 🚀 Guias de Execução por Fase

Detalhamento técnico "mão na massa" para replicar os resultados:

1. **[Fase 1: Fundação](guides/fase_1_fundacao.md)** - Infraestrutura, LLM Layer e CI/CD.
2. **[Fase 2: Processamento de PDF](guides/fase_2_upload.md)** - Idempotência e extração textual.
3. **[Fase 3: Inteligência LLM](guides/fase_3_extracao_llm.md)** - Structured outputs e Grafos de Conhecimento.

## 📈 Melhorias e Evolução

O projeto foi desenhado com extensibilidade em mente. Os próximos passos focam em **Escalabilidade** e **Eficiência de IA**:

- Integração com **Langfuse** para observability de prompts.
- Implementação de **Prompt Caching** para redução de latência.
- Migração para **Background Tasks** em extrações longas.

---
*Para dúvidas técnicas sobre como rodar o projeto, consulte o [README.md principal](../../README.md).*
