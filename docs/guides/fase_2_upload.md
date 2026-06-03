# Fase 2: Upload e Processamento de PDF

## Contexto

Este plano implementa a **Fase 2** do Adaptive Leveling System: Upload e Processamento de PDF.

Com a infraestrutura e a fundação técnica consolidadas na Fase 1, o objetivo desta fase é permitir que os usuários façam o upload de aulas em formato PDF, extrair o conteúdo textual e armazená-lo de forma eficiente. O foco principal é a **idempotência** (não reprocessar o mesmo arquivo) utilizando hash SHA-256, garantindo performance e economia de recursos nas futuras interações com o LLM.

**Objetivo:** Upload de PDF com processamento (extração de texto), armazenamento inteligente (S3 + DB) e estratégia de cache.

---

## Estrutura de Arquivos Planejada

```
adaptive-leveling-system/
├── backend/
│   ├── api/
│   │   ├── routes/
│   │   │   └── pdf.py                # Endpoints de upload e consulta de PDFs
│   │   └── schemas/
│   │       └── pdf.py                # Pydantic schemas (requests/responses)
│   │
│   ├── domain/
│   │   └── models/
│   │       ├── common.py             # Modelos base (ex: Timestamps)
│   │       └── pdf.py                # Modelos de domínio (PDFDocument, PDFMetadata)
│   │
│   ├── infrastructure/
│   │   ├── repository/
│   │   │   ├── __init__.py
│   │   │   └── pdf_repository.py     # Lógica de banco de dados (Salvar/Buscar metadata)
│   │   ├── storage/
│   │   │   └── pdf_storage.py        # Integração S3 específica para PDFs (Upload/Presigned URL)
│   │   └── cache/
│   │       └── pdf_cache.py          # Lógica de cache via Valkey (ex: texto extraído)
│   │
│   └── services/
│       └── pdf_service.py            # Lógica de negócio (Hash, Extração pypdf, Orquestração)
│
├── frontend/
│   └── app/
│       ├── components/
│       │   ├── pdf_preview.py        # Componente visual para prévia do PDF
│       │   └── pdf_download.py       # Botão para download via presigned URL
│       └── pages/
│           └── upload.py             # Interface principal de upload de aulas
│
└── tests/
    ├── fixtures/
    │   └── calculus_1.pdf            # PDF de exemplo para testes
    ├── test_pdf_service.py           # Testes da lógica de extração e idempotência
    ├── test_pdf_routes.py            # Testes de integração da API
    ├── test_pdf_storage.py           # Testes específicos do S3
    └── test_pdf_cache.py             # Testes específicos de cache
```

---

## Fluxo de Processamento (Arquitetura)

O processo de upload seguirá um fluxo otimizado para evitar duplicação de processamento:

1. **Upload via Frontend:** O usuário seleciona um PDF no Streamlit.
2. **Recepção na API (`POST /upload`):** O FastAPI recebe o arquivo.
3. **Cálculo de Hash SHA-256:** O serviço calcula o hash do conteúdo do PDF na memória.
4. **Verificação de Idempotência (Banco de Dados):**
   - Se o hash **já existe** no banco de dados, a API retorna sucesso imediatamente com os metadados existentes (reuso total).
   - Se o hash **não existe**, o processamento continua.
5. **Armazenamento Seguro (Minio S3):** O arquivo original é salvo no S3. O `bucket_key` é gerado.
6. **Extração de Texto (`pypdf`):** O texto é extraído das páginas do PDF de forma assíncrona.
7. **Persistência de Metadados (PostgreSQL):** Dados como `filename`, `hash`, `size`, `bucket_key` e o próprio texto extraído (`content_text`) são salvos na tabela `pdf_documents`.
8. **Cache (Valkey):** Resultados temporários ou dados de requisições recentes podem ser cacheados.

---

## Tarefas Sequenciais

### Tarefa 1: Modelos de Domínio e Schemas (Pydantic)

- Criar classes em `backend/domain/models/pdf.py` para mapear os dados do banco.
- Criar schemas em `backend/api/schemas/pdf.py` para requisições/respostas da API.

### Tarefa 2: Camada de Infraestrutura (Storage, Repository)

- **Storage (`pdf_storage.py`)**: Implementar funções auxiliares que utilizam o cliente S3 para subir arquivos PDF e gerar presigned URLs.
- **Repository (`pdf_repository.py`)**: Implementar CRUD básico usando `asyncpg` para salvar e consultar metadados pelo hash.

### Tarefa 3: Serviço de Negócio (`pdf_service.py`)

- Implementar a lógica central `process_pdf(file_bytes, filename)`.
- Integrar a biblioteca `pypdf` para extração do texto.
- Orquestrar a checagem de hash -> S3 -> Extração -> DB.

### Tarefa 4: Rotas FastAPI (`pdf.py`)

- Criar endpoint `POST /upload` usando `UploadFile`.
- Criar endpoints `GET /{pdf_id}` e `GET /hash/{hash}`.
- Integrar as rotas no `main.py`.

### Tarefa 5: Frontend (Upload Page & Components)

- Desenvolver `frontend/app/pages/upload.py` usando `st.file_uploader`.
- Mostrar status de progresso, hash gerado e sucesso.

### Tarefa 6: Testes Automatizados

- Escrever testes unitários para a extração de hash e processamento (`test_pdf_service.py`).
- Escrever testes de API simulando uploads (`test_pdf_routes.py`).

---

## Critérios de Aceitação

- [x] Arquivo de testes PDF (ex: `calculus_1.pdf`) disponível.
- [x] Endpoint de upload funcional e seguro.
- [x] O arquivo recebido é efetivamente salvo no Minio/S3.
- [x] Metadados do arquivo (e hash SHA-256) salvos no PostgreSQL.
- [x] Idempotência verificada via hash (não duplicar arquivos idênticos).
- [x] Extração de texto implementada e funcional.
- [x] Interface de upload no Streamlit amigável.
- [x] Testes passando e cobertura mantida > 80%.

**Status: FASE 2 COMPLETA ✅**

---

## Decisões Técnicas

1. **Extração de Texto:** Utilizaremos o pacote `pypdf` por ser o sucessor moderno e performático do PyPDF2.
2. **Armazenamento de Texto:** O texto extraído será armazenado na coluna `content_text` do PostgreSQL para facilitar o acesso rápido pela LLM nas próximas fases.
