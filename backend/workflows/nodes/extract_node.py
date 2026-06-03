async def extract_node(state: dict) -> dict:
    from backend.services.prerequisite_service import extract_prerequisites

    pdf_id = state.get("pdf_id")
    if not pdf_id:
        return {**state, "error": "pdf_id é obrigatório", "status": "failed"}
    try:
        import uuid

        pid = uuid.UUID(pdf_id)
    except ValueError:
        return {**state, "error": "pdf_id inválido", "status": "failed"}
    try:
        graph = await extract_prerequisites(pid)
        return {
            **state,
            "knowledge_graph": graph.model_dump(mode="json")
            if hasattr(graph, "model_dump")
            else graph,
            "progress": 0.2,
            "current_node": "extract",
        }
    except ValueError as e:
        return {**state, "error": str(e), "status": "failed"}
