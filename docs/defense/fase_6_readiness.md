# Defesa Técnica - Fase 6: Detecção de Gaps e Análise de Prontidão

## 1. Visão Geral

A Fase 6 analisa o desempenho do aluno no quiz (Fase 5) para calcular um score de prontidão, identificar gaps de conhecimento e classificar o nível de preparação para a disciplina alvo (Cálculo I). Esta fase transforma respostas brutas em insights acionáveis de aprendizado.

## 2. Decisões Arquiteturais

### 2.1. Scoring Ponderado por Importância

* **Decisão:** Pesos diferenciados por nível de importância do pré-requisito: Critical = 3x, Important = 2x, Helpful = 1x.
* **Racional:** Nem todo conhecimento prévio tem o mesmo impacto no sucesso do aluno. Um gap em um pré-requisito Critical (ex: Funções) impede o avanço, enquanto um gap Helpful (ex: Trigonometria) pode ser contornado. A ponderação reflete essa hierarquia no score final.

### 2.2. Thresholds de Prontidão (Três Níveis)

* **Decisão:** Três níveis de saída: **Ready** (score >= 80%), **Needs Review** (50-79%), **Not Ready** (< 50%).
* **Racional:** Categorias discretas facilitam a comunicação com o aluno e orientam a ação do sistema. Alunos "Ready" progridem para a disciplina; "Needs Review" recebem nivelamento seletivo; "Not Ready" recebem nivelamento completo.

### 2.3. Priorização de Gaps por Severidade

* **Decisão:** Gaps são ordenados por: (1) Importância do pré-requisito, (2) Score mais baixo, (3) Dependência entre conceitos.
* **Racional:** Ensina-se primeiro o que é mais crítico e mais deficitário. A ordenação por dependência garante que conceitos base sejam nivelados antes dos que dependem deles.

### 2.4. Análise de Forças (Strengths)

* **Decisão:** Pré-requisitos com score >= 80% são classificados como "Strengths" e destacados positivamente.
* **Racional:** O feedback positivo é psicologicamente importante para engajamento. Identificar forças também permite que o sistema de nivelamento (Fase 7) personalize o conteúdo com exemplos que conectem o conhecido ao novo.

## 3. Observabilidade e Testabilidade

* **Tracing:** O pipeline de scoring é traceado com breakdown por importância e threshold aplicado.
* **Testes:** Testes unitários validam o cálculo ponderado, a classificação por threshold e a ordenação de gaps.

## 4. Conclusão

A Fase 6 implementa um motor de análise educacional que transforma dados brutos de quiz em um diagnóstico estruturado, pavimentando o caminho para a geração de conteúdo personalizado na Fase 7.
