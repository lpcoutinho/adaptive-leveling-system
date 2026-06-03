# Fase 3: Extração de Pré-requisitos com LLM

## Contexto

Este plano implementa a **Fase 3** do Adaptive Leveling System: Extração de Pré-requisitos com LLM.

Agora que conseguimos fazer o upload dos PDFs e armazenar o texto extraído no banco de dados (Fase 2), o objetivo desta fase é **dar inteligência ao sistema**. Iremos recuperar esse texto, injetá-lo em um prompt estruturado e enviá-lo à nossa Camada de Abstração de LLM (Groq). O LLM retornará uma saída estruturada (JSON validado via Pydantic) contendo os tópicos da aula e, principalmente, os **pré-requisitos** necessários para entendê-los, formando a base de um Grafo de Conhecimento.

**Objetivo:** Integrar a camada de LLM para analisar textos de aulas e extrair pré-requisitos lógicos de forma estruturada e observável.

---

## Estrutura de Arquivos Planejada

```
adaptive-leveling-system/
├── backend/
│   ├── api/
│   │   ├── routes/
│   │   │   └── prerequisites.py      # Endpoints para iniciar e consultar extrações
│   │   └── schemas/
│   │       └── prerequisite.py       # Pydantic schemas para a API
│   │
│   ├── domain/
│   │   └── models/
│   │       └── prerequisite.py       # Modelos de domínio (ConceptNode, Prerequisite)
│   │
│   ├── infrastructure/
│   │   └── repository/
│   │       └── prerequisite_repository.py # Salvar/Buscar os pré-requisitos extraídos no DB
│   │
│   ├── llm/
│   │   └── prompts/
│   │       └── prerequisite_extractor_v1.txt # Template do prompt para o LLM
│   │
│   └── services/
│       └── prerequisite_service.py   # Orquestração (DB Text -> Prompt -> LLM -> DB Save)
│
├── frontend/
│   └── app/
│       ├── components/
│       │   └── knowledge_graph.py    # Visualização estruturada dos pré-requisitos
│       └── pages/
│           └── prerequisites.py      # Interface para solicitar e exibir a análise
│
├── migrations/
│   └── 002_prerequisites_schema.sql  # Nova tabela para o grafo de conhecimento
│
└── tests/
    ├── test_prerequisite_service.py  # Testes usando MockProvider
    └── test_prerequisite_routes.py   # Testes dos endpoints da API
```

---

## Fluxo de Processamento (Arquitetura)

1. **Requisição:** O usuário solicita a análise fornecendo um `pdf_id`.
2. **Recuperação de Dados:** O serviço busca o `content_text` no banco de dados.
3. **Prompt Engineering:** O texto é formatado dentro do template `prerequisite_extractor_v1.txt`, com instruções claras para ignorar ruídos de PDF.
4. **Chamada LLM (Structured Output):**
   - O `ILLMProvider` chama `generate_structured`.
   - O LLM (Groq) processa e retorna um JSON que obedece ao modelo `KnowledgeGraph`.
5. **Persistência:** Os resultados são salvos na tabela `prerequisites_graph`, associados ao arquivo original.
6. **Observabilidade:** O rastreio é enviado ao Jaeger e o monitoramento de prompts/custos inicia via integração (planejada) com Langfuse.

---

## Tarefas Sequenciais

### Tarefa 1: Modelagem de Domínio e Prompts

- Definir os modelos `Prerequisite`, `ConceptNode` e `KnowledgeGraph` em `backend/domain/models/prerequisite.py`.
- Criar o arquivo de template `backend/llm/prompts/prerequisite_extractor_v1.txt`.

### Tarefa 2: Persistência no Banco de Dados

- Criar a tabela `prerequisites_graph` via migração SQL.
- Implementar `prerequisite_repository.py` para operações CRUD.

### Tarefa 3: Serviço de Orquestração (`prerequisite_service.py`)

- Implementar `extract_prerequisites(pdf_id: UUID)`.
- Lógica de "Noise Tolerance": Instruir o LLM a tratar o texto imperfeito da Fase 2.

### Tarefa 4: Rotas FastAPI

- Criar endpoints `POST /pdf/{pdf_id}/extract` e `GET /pdf/{pdf_id}/prerequisites`.
- Registrar no `main.py`.

### Tarefa 5: Frontend e Visualização

- Desenvolver a página `prerequisites.py`.
- Exibir conceitos e pré-requisitos agrupados por importância (Crítico, Importante, Útil).

### Tarefa 6: Testes Automatizados

- Escrever testes unitários e de integração utilizando o `MockProvider`.

---

## Critérios de Aceitação

- [ ] Tabela de pré-requisitos criada no PostgreSQL.
- [ ] Extração funcional via API com Structured Output (JSON).
- [ ] Idempotência: Se a análise já existe para o `pdf_id`, não chamar o LLM novamente.
- [ ] Interface exibe os resultados de forma clara.
- [ ] Cobertura de testes mantida > 80%.

---

## Decisões Técnicas

1. **Structured Outputs:** Uso obrigatório de `json_mode` para garantir integridade dos dados.
2. **Resiliência:** Implementação de retry automático caso a extração falhe por motivos de rede ou parsing.
3. **Prompting:** Inclusão de "Self-Correction" no prompt para melhorar a extração de fórmulas matemáticas.
