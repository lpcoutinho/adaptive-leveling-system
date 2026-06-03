async def readiness_node(state: dict) -> dict:
    from backend.services.gap_detection_service import analyze_gaps

    session_id = state.get("session_id")
    pdf_id = state.get("pdf_id")
    if not pdf_id:
        return {**state, "error": "pdf_id obrigatório", "status": "failed"}
    try:
        import uuid

        pid = uuid.UUID(pdf_id)
    except ValueError:
        return {**state, "error": "pdf_id inválido", "status": "failed"}

    if session_id:
        try:
            sid = uuid.UUID(session_id)
        except ValueError:
            return {**state, "error": "session_id inválido", "status": "failed"}
    else:
        sid = pid

    try:
        result = await analyze_gaps(sid, pid)
        return {
            **state,
            "readiness_result": result.model_dump(mode="json")
            if hasattr(result, "model_dump")
            else result,
            "readiness_id": str(result.id) if hasattr(result, "id") else "",
            "progress": 0.8,
            "current_node": "readiness",
        }
    except ValueError as e:
        return {**state, "error": str(e), "status": "failed"}
