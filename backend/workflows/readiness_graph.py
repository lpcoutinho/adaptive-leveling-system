"""Grafo LangGraph que orquestra o workflow de nivelamento adaptativo.

Define a máquina de estados do processo completo:
extract → assessment → quiz → readiness → (leveling | END)

Cada nó é uma função assíncrona que executa uma etapa do pipeline.
As arestas condicionais decidem o fluxo baseado no estado e resultados.
"""

from langgraph.graph import END, StateGraph  # type: ignore[import-untyped, import-not-found]

from backend.workflows.nodes import (
    assessment_node,
    extract_node,
    leveling_node,
    quiz_node,
    readiness_node,
)


def route_after_extract(state: dict) -> str:
    """Roteia para assessment se a extração foi bem-sucedida, senão encerra."""
    if state.get("status") == "failed":
        return END  # type: ignore[no-any-return]
    return "assessment"


def route_after_assessment(state: dict) -> str:
    """Roteia para readiness após a geração da avaliação."""
    if state.get("status") == "failed":
        return END  # type: ignore[no-any-return]
    return "readiness"


def route_after_quiz(state: dict) -> str:
    """Roteia para readiness se o quiz foi concluído, ou aguarda input."""
    if state.get("status") == "failed":
        return END  # type: ignore[no-any-return]
    if state.get("status") == "awaiting_input":
        return END  # type: ignore[no-any-return]
    return "readiness"


def route_after_readiness(state: dict) -> str:
    """Decide se gera nivelamento ou encerra (se score >= 80)."""
    if state.get("status") == "failed":
        return END  # type: ignore[no-any-return]
    result = state.get("readiness_result", {})
    if result and result.get("overall_score", 0) >= 80:
        return END  # type: ignore[no-any-return]
    return "leveling"


def build_workflow_graph() -> StateGraph:
    """
    Constrói e compila o grafo do workflow.

    Nós:
    - extract: Extrai pré-requisitos do PDF via LLM
    - assessment: Gera questões de avaliação diagnóstica
    - quiz: Cria sessão de quiz e aguarda respostas do aluno
    - readiness: Analisa gaps e forças (determinístico)
    - leveling: Gera conteúdo de nivelamento personalizado (LLM)

    Returns:
        StateGraph compilado (App pronto para invoke/ainvoke).
    """
    workflow = StateGraph(dict)  # type: ignore[type-var]

    workflow.add_node("extract", extract_node)  # type: ignore[type-var]
    workflow.add_node("assessment", assessment_node)  # type: ignore[type-var]
    workflow.add_node("quiz", quiz_node)  # type: ignore[type-var]
    workflow.add_node("readiness", readiness_node)  # type: ignore[type-var]
    workflow.add_node("leveling", leveling_node)  # type: ignore[type-var]

    workflow.set_entry_point("extract")

    workflow.add_conditional_edges("extract", route_after_extract)
    workflow.add_edge("assessment", "quiz")
    workflow.add_conditional_edges("quiz", route_after_quiz)
    workflow.add_conditional_edges(
        "readiness",
        route_after_readiness,
        {
            END: END,
            "leveling": "leveling",
        },
    )
    workflow.add_edge("leveling", END)

    return workflow.compile()  # type: ignore[return-value]


# App compilado pronto para uso (importado por workflow_service)
app = build_workflow_graph()
