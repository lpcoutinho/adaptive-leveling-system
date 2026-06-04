# Defesa Técnica - Fase 5: Avaliação do Estudante (LLM-as-a-Judge)

## 1. Visão Geral

A Fase 5 implementa o quiz interativo onde o aluno responde às questões geradas na Fase 4. O sistema utiliza uma abordagem híbrida de correção: questões de Múltipla Escolha são corrigidas deterministicamente (match exato), enquanto Respostas Curtas e Cálculos são avaliados por um LLM atuando como juiz (LLM-as-a-Judge).

## 2. Decisões Arquiteturais

### 2.1. Correção Híbrida (Determinística + LLM)

* **Decisão:** MC corrigida por comparação direta; SA e Calc avaliadas por prompt especializado de avaliação.
* **Racional:** MC não requer julgamento semântico — a resposta é certa ou errada. Já SA e Calc admitem variações legítimas (ex: "2" vs "dois" vs "2 unidades"). Usar LLM para essas avaliações captura equivalência semântica sem criar listas exaustivas de respostas aceitas. Esta abordagem reduz custos de API em ~40% (apenas SA/Calc enviam tokens para avaliação).

### 2.2. Prompt de Avaliação (Rubric-Based)

* **Decisão:** O avaliador LLM recebe a questão, a resposta esperada, a resposta do aluno e uma rubrica explícita com níveis de acerto (0%, 25%, 50%, 75%, 100%).
* **Racional:** Rubricas estruturadas reduzem a variabilidade do LLM e produzem scores mais consistentes. O avaliador deve justificar cada nota, permitindo auditoria e feedback ao aluno.

### 2.3. Sessão com Auto-Save (Valkey + PostgreSQL)

* **Decisão:** O progresso do aluno é salvo no Valkey a cada resposta (TTL 1h) e persistido no PostgreSQL ao finalizar.
* **Racional:** Auto-save em cache previne perda de progresso por falha de conexão. A persistência final no PostgreSQL garante durabilidade para análise posterior (Fase 6).

### 2.4. Timer por Questão e Sessão

* **Decisão:** Timer configurável por questão (padrão 3min MC, 5min SA, 10min Calc) e timer total da sessão.
* **Racional:** Impede que o aluno gaste tempo excessivo em uma única questão e simula condições controladas de avaliação. O timer é puramente informativo (não bloqueante) para reduzir ansiedade.

### 2.5. Avaliação em Lote (Batch Evaluation)

* **Decisão:** Agrupamento de todas as questões discursivas (SA/Calc) para uma única chamada de IA ao final do quiz.
* **Racional:** Diferente de avaliar cada questão individualmente (que aumentaria a latência percebida e o custo de tokens devido ao envio repetitivo do sistema e instruções), a avaliação em lote:
  1. **Reduz Custos**: Minimiza o overhead de tokens de contexto.
  2. **Consistência Pedagógica**: Permite que o LLM avalie o aluno com uma visão holística de seu desempenho no quiz.
  3. **Performance**: O aluno responde fluidamente e a "espera" ocorre apenas uma vez no fechamento.

## 3. Observabilidade e Testabilidade

* **Tracing:** Cada resposta é traceada com tempo gasto, tipo de questão e score obtido.
* **Testes:** Testes unitários validam a correção MC (determinística) e testes com `MockProvider` validam a avaliação SA/Calc.

## 4. Conclusão

A Fase 5 oferece uma experiência de quiz robusta com correção inteligente que combina eficiência (MC determinística) com flexibilidade semântica (LLM-as-a-Judge para SA/Calc).
