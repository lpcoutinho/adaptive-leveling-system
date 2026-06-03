# Defesa Técnica - Fase 7: Geração de Conteúdo de Nivelamento

## 1. Visão Geral

A Fase 7 gera conteúdo educacional personalizado para cada gap identificado na Fase 6. Para cada pré-requisito deficitário, o sistema produz uma explicação contextualizada com a disciplina alvo, exemplos práticos e exercícios de fixação, organizados em um plano de estudo sequencial.

## 2. Decisões Arquiteturais

### 2.1. Estrutura Padronizada de Conteúdo (Why-Explanation-Example-Exercise)

* **Decisão:** Cada gap é explicado com quatro seções obrigatórias: (1) Por que isso é importante?, (2) Explicação do conceito, (3) Exemplo prático relacionado a Cálculo I, (4) Exercício de fixação.
* **Racional:** A estrutura WEEE (Why, Explanation, Example, Exercise) é baseada em princípios de aprendizagem multimídia e garante consistência entre todos os conteúdos gerados. A conexão explícita com Cálculo I (ex: "limites de funções polinomiais") motiva o aluno ao mostrar relevância imediata.

### 2.2. Prompt com Contexto do Perfil do Aluno

* **Decisão:** O prompt de geração inclui o score do aluno, os gaps identificados e seus strengths.
* **Racional:** Conteúdo adaptativo de verdade requer contexto do aprendiz. Se o aluno é forte em álgebra mas fraco em trigonometria, os exemplos devem usar notação algébrica familiar para reduzir carga cognitiva.

### 2.3. Ordenação Topológica do Plano de Estudo

* **Decisão:** O plano de estudo respeita a ordem de dependência: conceitos base antes dos derivados.
* **Racional:** Ensinar derivação antes de limites é pedagogicamente inviável. A ordenação topológica garante que o aluno construa conhecimento de forma incremental.

### 2.4. Cache de Conteúdo (TTL 7 dias)

* **Decisão:** Conteúdos gerados são cacheados por gap + perfil do aluno, com TTL de 7 dias.
* **Racional:** Para um mesmo gap e perfil similar, o conteúdo deve ser reutilizável. O cache reduz custos de API e acelera o carregamento.

## 3. Observabilidade e Testabilidade

* **Tracing:** Cada geração de conteúdo é traceada com métricas de tokens consumidos e tempo de resposta.
* **Testes:** O `MockProvider` valida a estrutura dos conteúdos gerados e a ordenação do plano de estudo.

## 4. Conclusão

A Fase 7 entrega conteúdo educacional personalizado, pedagogicamente estruturado e conectado ao contexto do aluno, maximizando a eficácia do nivelamento.
