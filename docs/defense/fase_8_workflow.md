# Defesa Técnica - Fase 8: Orquestração de Workflow com LangGraph

## 1. Visão Geral

A Fase 8 representa o ápice da maturidade operacional do sistema. Em vez de etapas isoladas, o projeto passa a operar como uma **Agente Inteligente de Fluxo**, onde cada decisão e transição de estado é orquestrada por uma máquina de estados robusta.

## 2. Decisões Arquiteturais

### 2.1. A Escolha do LangGraph

* **Decisão:** Utilização do `StateGraph` como orquestrador central.
* **Racional:** Workflows educacionais são naturalmente cíclicos e dependentes de interação humana (o Quiz). O LangGraph permite modelar essas interações ("Human-in-the-loop") de forma nativa através de pontos de interrupção e persistência de estado.

### 2.2. Checkpointing e Tolerância a Falhas

* **Decisão:** Persistência de cada transição de nó no PostgreSQL.
* **Racional:** Em um workflow longo (upload até nivelamento), falhas de rede ou reinicializações do servidor são fatais para a experiência do usuário. Com checkpointing, o aluno nunca perde o progresso e o sistema se torna resiliente a falhas temporárias de infraestrutura.

### 2.3. Separação em Nós Especializados

* **Decisão:** Cada fase (Extração, Avaliação, etc.) é encapsulada em um nó do grafo.
* **Racional:** Isso garante o princípio de **Responsabilidade Única**. Podemos atualizar a lógica de extração sem afetar a lógica de nivelamento, além de permitir testes unitários em cada nó individualmente.

## 3. Observabilidade e Tracing

* **LangGraph + OpenTelemetry:** A orquestração está integrada ao Jaeger. Isso permite visualizar o "caminho" do aluno através dos estados, identificando onde ele passa mais tempo ou onde ocorrem abandonos.
* **Visibilidade de Estado:** A página de Workflow fornece uma janela para o "cérebro" do sistema, mostrando ao usuário (ou professor) exatamente em que etapa o processamento se encontra.

## 4. Conclusão

A integração com LangGraph eleva o *Adaptive Leveling System* de um conjunto de scripts para uma aplicação de IA de nível profissional, preparada para lidar com fluxos complexos, interrupções e alta disponibilidade.
