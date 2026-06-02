# Defesa Técnica - Fase 2: Upload e Processamento de PDF

## 1. Visão Geral

A Fase 2 foca na ingestão de dados e na garantia de integridade e eficiência através de técnicas de processamento de documentos e gerenciamento de estado. O objetivo é transformar arquivos binários (PDFs) em texto processável, servindo como a "materia-prima" para a inteligência do sistema.

## 2. Decisões Arquiteturais

### 2.1. Idempotência via SHA-256

* **Decisão:** Utilizar o hash SHA-256 do conteúdo do arquivo como identificador único de integridade.
* **Racional:** Evita o custo computacional e financeiro (tokens de LLM) de reprocessar documentos idênticos. Se o hash já existe no banco, o sistema reutiliza os resultados instantaneamente. Diferentes nomes de arquivo para o mesmo conteúdo resultam no mesmo hash, garantindo unicidade real dos dados.

### 2.2. Extração de Texto com `pypdf`

* **Decisão:** Uso da biblioteca `pypdf` para extração de texto em vez de soluções baseadas em OCR nesta fase.
* **Racional:** `pypdf` é o sucessor moderno e mantido do PyPDF2, oferecendo o equilíbrio ideal entre leveza e precisão para documentos de texto estruturado (como apostilas acadêmicas). É uma biblioteca puramente Python, facilitando a portabilidade e mantendo a baixa latência no processamento.

### 2.3. Armazenamento Híbrido (S3 + Postgres)

* **Decisão:** O arquivo binário original é armazenado no Minio (S3), enquanto o texto extraído e os metadados são persistidos no PostgreSQL.
* **Racional:** O S3 é otimizado para blobs binários de grande porte e escalabilidade. Manter o texto extraído no Postgres (`content_text`) permite buscas rápidas e facilita a integração direta com os serviços de LLM na Fase 3, eliminando a latência de buscar o conteúdo no S3 a cada requisição da IA.

### 2.4. Estratégia de "Abraço ao Ruído" (Noise Tolerance)

* **Decisão:** Aceitar extrações de texto imperfeitas (ruídos de formatação, caracteres estranhos em fórmulas) nesta camada.
* **Racional:** A extração de texto de PDFs é inerentemente imperfeita devido à falta de estrutura semântica do formato. Nossa arquitetura delega a "limpeza inteligente" para a Fase 3, utilizando a capacidade natural dos LLMs modernos (como Llama-3 e GPT-4) de ignorar ruídos e focar no contexto semântico. Isso reduz drasticamente a complexidade da Fase 2 sem comprometer a qualidade da extração de pré-requisitos.

## 3. Observabilidade e Resiliência

* **Jaeger Tracing:** O pipeline de upload é rastreado de ponta a ponta, permitindo medir o tempo gasto em cada etapa (hashing, upload S3, extração, persistência DB).
* **Validação de Integridade:** O sistema valida o cabeçalho do arquivo (`%PDF-`) antes do processamento, protegendo contra uploads de arquivos corrompidos ou maliciosos.

## 4. Evolução Futura

* Para documentos com alta densidade de imagens ou tabelas complexas, a arquitetura está preparada para a substituição modular do `pypdf` por serviços de OCR multi-modais (ex: Amazon Textract) ou modelos Vision-based, sem alterar o fluxo de metadados e idempotência já estabelecido.

## 5. Conclusão

A implementação desta fase garante que o texto das aulas seja coletado de forma confiável, eficiente e inteligente, estabelecendo a ponte necessária entre a infraestrutura tradicional e os agentes de IA.
