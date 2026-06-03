# Defesa Técnica - Fase 3: Extração de Pré-requisitos com LLM

## 1. Visão Geral

A Fase 3 representa a transição do sistema de uma ferramenta de armazenamento para uma plataforma de **Inteligência Educacional**. O foco foi transformar texto bruto e ruidoso em uma estrutura de dados semântica (Grafo de Conhecimento).

## 2. Decisões Arquiteturais

### 2.1. Engenharia de Prompt e Tolerância a Ruído

* **Decisão:** Inclusão de instruções explícitas de "Noise Tolerance" no prompt template.
* **Racional:** Documentos PDF, especialmente de áreas exatas como Cálculo I, geram extrações textuais imperfeitas. Instruir o LLM a focar no sentido semântico e ignorar artefatos de formatação permite que o sistema seja resiliente sem a necessidade de pré-processadores complexos e caros.

### 2.2. Structured Outputs (JSON Mode)

* **Decisão:** Utilização do método `generate_structured` integrado com validação Pydantic.
* **Racional:** Para que os dados extraídos pela IA sejam úteis em outras partes do sistema (como na geração automática de avaliações na Fase 4), a saída deve ser determinística. O uso de schemas estritos garante que a IA nunca devolva texto livre quando uma estrutura de dados é esperada.

### 2.3. Persistência de Inteligência (Conhecimento Derivado)

* **Decisão:** Armazenamento do Grafo de Conhecimento em formato JSONB associado ao `pdf_id`.
* **Racional:** A extração via LLM é uma operação cara em termos de latência e custo de API. Persistir o resultado permite que o sistema forneça acesso instantâneo à análise após a primeira execução, economizando tokens e tempo do usuário.

### 2.4. Classificação de Importância (Taxonomia de Aprendizado)

* **Decisão:** Implementação de uma taxonomia de três níveis para pré-requisitos: *Critical*, *Important* e *Helpful*.
* **Racional:** Nem todo conhecimento prévio tem o mesmo peso. Essa granularidade permite que o sistema de nivelamento (Fase 7) priorize o que realmente impedirá o progresso do aluno, otimizando o percurso de aprendizagem.

## 3. Observabilidade e Testabilidade

* **Tracing:** As chamadas ao serviço de extração são integradas ao Jaeger, permitindo monitorar a latência das chamadas externas à API do Groq.
* **Mocking:** A suíte de testes unitários utiliza o `MockProvider`, garantindo que o pipeline de CI/CD valide a orquestração do serviço sem custos ou dependência de chaves de API.

## 4. Conclusão

A Fase 3 consolida a inteligência do sistema. Com os pré-requisitos extraídos e classificados, o *Adaptive Leveling System* agora possui a base de conhecimento necessária para gerar diagnósticos precisos e percursos de estudo personalizados.
