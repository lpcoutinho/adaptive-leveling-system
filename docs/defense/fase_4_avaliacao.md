# Defesa Técnica - Fase 4: Geração de Avaliação Diagnóstica

## 1. Visão Geral

A Fase 4 transforma o Grafo de Conhecimento (extraído na Fase 3) em um instrumento de avaliação diagnóstica. O sistema gera questões personalizadas para cada pré-requisito identificado, permitindo medir o nível de prontidão do aluno antes de iniciar a disciplina alvo (Cálculo I).

## 2. Decisões Arquiteturais

### 2.1. Balanceamento de Tipos de Questão

* **Decisão:** Distribuição fixa de tipos: 40% Múltipla Escolha (MC), 30% Resposta Curta (SA), 30% Cálculo (Calc).
* **Racional:** Cada tipo de questão avalia habilidades distintas. MC testa reconhecimento e eliminação, SA testa recall e aplicação direta, Calc testa raciocínio procedural. A distribuição balanceada evita viés de formato e fornece uma medida mais robusta da prontidão do aluno.

### 2.2. Modelo de Questões com Metadados de Dificuldade

* **Decisão:** Cada questão gerada inclui campos de dificuldade, tópico e justificativa da resposta correta.
* **Racional:** Os metadados permitem que o sistema de detecção de gaps (Fase 6) pondere o score do aluno não apenas pela importância do pré-requisito, mas também pela dificuldade da questão. A justificativa viabiliza o feedback explicativo pós-quiz.

### 2.3. Template de Prompt Versionado com Few-Shot

* **Decisão:** O prompt `assessment_generator_v1.txt` inclui exemplos few-shot para cada tipo de questão.
* **Racional:** A geração de questões boas é uma tarefa complexa para LLMs. Exemplos concretos no prompt melhoram significativamente a qualidade e a aderência ao formato esperado, reduzindo a necessidade de pós-processamento.

### 2.4. Cache de Avaliação (TTL 7 dias)

* **Decisão:** Avaliações geradas são cacheadas no Valkey com TTL de 7 dias.
* **Racional:** Para um mesmo conjunto de pré-requisitos, a avaliação deve ser estável. O cache evita regeneração desnecessária e garante consistência durante a sessão do aluno.

## 3. Observabilidade e Testabilidade

* **Tracing:** As chamadas de geração de questões são traceadas no Jaeger com tags para tipo de questão e quantidade.
* **Testes:** O `MockProvider` valida a estrutura e distribuição das questões geradas sem chamadas reais à API.

## 4. Conclusão

A Fase 4 entrega um gerador de avaliações diagnósticas que produz questões estruturadas e balanceadas, prontas para serem apresentadas ao aluno na Fase 5.
