from langgraph.graph import END, StateGraph  # type: ignore[import-untyped, import-not-found]

from backend.workflows.nodes import (
    assessment_node,
    extract_node,
    leveling_node,
    quiz_node,
    readiness_node,
)


def route_after_extract(state: dict) -> str:
    if state.get("status") == "failed":
        return END  # type: ignore[no-any-return]
    return "assessment"


def route_after_assessment(state: dict) -> str:
    if state.get("status") == "failed":
        return END  # type: ignore[no-any-return]
    return "readiness"


def route_after_readiness(state: dict) -> str:
    if state.get("status") == "failed":
        return END  # type: ignore[no-any-return]
    result = state.get("readiness_result", {})
    if result and result.get("overall_score", 0) >= 80:
        return END  # type: ignore[no-any-return]
    return "leveling"


def build_workflow_graph() -> StateGraph:
    workflow = StateGraph(dict)

    workflow.add_node("extract", extract_node)  # type: ignore[type-var]
    workflow.add_node("assessment", assessment_node)  # type: ignore[type-var]
    workflow.add_node("quiz", quiz_node)  # type: ignore[type-var]
    workflow.add_node("readiness", readiness_node)  # type: ignore[type-var]
    workflow.add_node("leveling", leveling_node)  # type: ignore[type-var]

    workflow.set_entry_point("extract")

    workflow.add_conditional_edges("extract", route_after_extract)
    workflow.add_edge("assessment", "quiz")
    workflow.add_edge("quiz", "readiness")
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


app = build_workflow_graph()
