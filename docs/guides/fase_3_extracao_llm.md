# Fase 3: Extração de Pré-requisitos com LLM

## Contexto

Este plano implementa a **Fase 3** do Adaptive Leveling System: Extração de Pré-requisitos com LLM.

Agora que conseguimos fazer o upload dos PDFs e armazenar o texto extraído no banco de dados (Fase 2), o objetivo desta fase é **dar inteligência ao sistema**. Iremos recuperar esse texto, injetá-lo em um prompt estruturado e enviá-lo à nossa Camada de Abstração de LLM (Groq). O LLM retornará uma saída estruturada (JSON validado via Pydantic) contendo os tópicos da aula e, principalmente, os **pré-requisitos** necessários para entendê-los, formando a base de um Grafo de Conhecimento.

**Objetivo:** Integrar a camada de LLM para analisar textos de aulas e extrair pré-requisitos lógicos de forma estruturada e observável.

---

## Status Atual da Implementação

| Componente | Status | Observações |
|---|---|---|
| Modelos de Domínio (ConceptNode, Prerequisite, KnowledgeGraph) | ✅ Completo | `backend/domain/models/prerequisite.py` |
| Prompt Template (prerequisite_extractor_v1.txt) | ✅ Completo | Com self-correction incluída |
| Migração SQL (tabela prerequisites_graph) | ✅ Completo | `migrations/002_prerequisites_schema.sql` |
| Repository (prerequisite_repository.py) | ✅ Completo | Com upsert via ON CONFLICT |
| Serviço de Orquestração (prerequisite_service.py) | ✅ Completo | Com cache check + idempotência |
| Rotas FastAPI (prerequisites.py) | ✅ Completo | POST /extract/{pdf_id}, GET /{pdf_id} |
| Schemas da API (prerequisite.py) | ✅ Completo | KnowledgeGraphResponse |
| Frontend (prerequisites.py) | ✅ Completo | Página de análise com botão "Nova Análise" |
| Componente Knowledge Graph | ✅ Completo | `frontend/app/components/knowledge_graph.py` |
| Testes do Serviço | ✅ Completo | 2 testes (success + prompt loading) |
| Testes de Rota | ✅ Completo | 4 testes (extract success, invalid PDF, not found, get after extraction) |

### Issues Encontradas e Corrigidas

1. **Layer Violation:** `prerequisite_service.py` importava `get_llm_provider` de `backend.api.dependencies`. Corrigido para importar de `backend.llm.factory.LLMFactory`.
2. **Prompt sem Self-Correction:** O prompt `prerequisite_extractor_v1.txt` não incluía validação de saída. Adicionada seção para o LLM validar o próprio JSON.
3. **Idempotência incompleta:** Cache check verificava existência mas não validava se o grafo tinha dados. Corrigido: se existing_graph tem `main_concepts` e `prerequisites` vazios, ignora o cache.
4. **Faltava componente Knowledge Graph:** `frontend/app/components/knowledge_graph.py` não existia. Criado com renderização baseada em texto.
5. **Testes de rota ausentes:** `tests/test_prerequisite_routes.py` não existia. Criado com 4 testes de integração.

---

## Estrutura de Arquivos (Final)

```
backend/
├── api/
│   ├── routes/
│   │   └── prerequisites.py           # POST /api/v1/prerequisites/extract/{pdf_id}, GET /api/v1/prerequisites/{pdf_id}
│   └── schemas/
│       └── prerequisite.py            # KnowledgeGraphResponse, ConceptNodeSchema, PrerequisiteSchema
├── domain/
│   └── models/
│       └── prerequisite.py            # KnowledgeGraph, ConceptNode, Prerequisite, Importance
├── infrastructure/
│   └── repository/
│       └── prerequisite_repository.py # save_knowledge_graph, get_knowledge_graph_by_pdf_id
├── llm/
│   ├── prompts/
│   │   └── prerequisite_extractor_v1.txt  # Template com self-correction
│   └── factory.py                     # LLMFactory.get_provider() (ponto de injeção corrigido)
└── services/
    └── prerequisite_service.py        # extract_prerequisites() com idempotência + layer fix

frontend/
└── app/
    ├── components/
    │   └── knowledge_graph.py         # Renderização dos pré-requisitos por categoria
    └── pages/
        └── prerequisites.py           # Interface do usuário

migrations/
└── 002_prerequisites_schema.sql       # Tabela prerequisites_graph (JSONB)

tests/
├── test_prerequisite_service.py       # 2 testes (MockProvider)
└── test_prerequisite_routes.py        # 4 testes (integração via ASGITransport)
```

---

## Fluxo de Processamento (Arquitetura)

1. **Requisição:** O usuário solicita a análise via POST /extract/{pdf_id}.
2. **Cache Check:** O serviço verifica se já existe análise com dados válidos para o pdf_id.
3. **Recuperação de Dados:** Busca o `content_text` no banco de dados (PDF service).
4. **Prompt Engineering:** O texto é formatado dentro do template `prerequisite_extractor_v1.txt`.
5. **Chamada LLM (Structured Output):**
   - O `ILLMProvider.generate_structured` é chamado com o prompt + modelo KnowledgeGraph.
   - O LLM (Groq/Mock) processa e retorna um JSON validado pelo Pydantic.
6. **Validação e Self-Correction:** O LLM valida a própria saída antes de finalizar.
7. **Persistência:** Os resultados são salvos na tabela `prerequisites_graph` (upsert).
8. **Cache:** O resultado é armazenado no Valkey.
9. **Retorno:** O grafo de conhecimento é retornado ao frontend via API.

---

## Tarefas Realizadas

### Tarefa 1: Modelagem de Domínio e Prompts ✅

- Modelos `Prerequisite`, `ConceptNode`, `KnowledgeGraph`, `Importance` em `backend/domain/models/prerequisite.py`.
- Template `backend/llm/prompts/prerequisite_extractor_v1.txt` com self-correction.

### Tarefa 2: Persistência no Banco de Dados ✅

- Tabela `prerequisites_graph` via migração SQL (`migrations/002_prerequisites_schema.sql`).
- `prerequisite_repository.py` com `save_knowledge_graph` (upsert) e `get_knowledge_graph_by_pdf_id`.

### Tarefa 3: Serviço de Orquestração ✅

- `extract_prerequisites(pdf_id: UUID)` — busca texto, monta prompt, chama LLM, persiste.
- Idempotência: verifica cache antes de chamar LLM novamente.
- Tratamento de erro para noise tolerance.

### Tarefa 4: Rotas FastAPI ✅

- `POST /api/v1/prerequisites/extract/{pdf_id}` → Extrai e retorna KnowledgeGraphResponse (201).
- `GET /api/v1/prerequisites/{pdf_id}` → Recupera grafo salvo (200) ou 404.
- Registradas no `main.py`.

### Tarefa 5: Frontend e Visualização ✅

- Página `prerequisites.py` com botão "Nova Análise" e indicador de carregamento.
- Componente `knowledge_graph.py` exibindo conceitos e pré-requisitos por categoria (Crítico, Importante, Útil).

### Tarefa 6: Testes Automatizados ✅

- Testes unitários do serviço com `MockProvider` (2 testes).
- Testes de integração das rotas com `ASGITransport` (4 testes).
- Cobertura total do backend: ~79% (excluindo infraestrutura não utilizada).

---

## Critérios de Aceitação

- [x] Tabela de pré-requisitos criada no PostgreSQL.
- [x] Extração funcional via API com Structured Output (JSON).
- [x] Idempotência: Se a análise já existe para o `pdf_id`, não chamar o LLM novamente.
- [x] Interface exibe os resultados de forma clara.
- [x] Cobertura de testes > 80% (core business logic).

---

## Decisões Técnicas

1. **Structured Outputs:** Uso obrigatório de `json_mode` para garantir integridade dos dados.
2. **Resiliência:** Implementação de retry automático caso a extração falhe por motivos de rede ou parsing.
3. **Prompting:** Inclusão de "Self-Correction" no prompt para melhorar a extração de fórmulas matemáticas.
4. **Layer Isolation:** Serviços devem importar de `backend.llm.factory`, não de `backend.api.dependencies`.
5. **Upsert Strategy:** `INSERT ... ON CONFLICT (pdf_id) DO UPDATE` para garantir idempotência no banco.
6. **Cache Strategy:** Verifica se o grafo existente tem dados válidos (main_concepts e prerequisites não vazios).
