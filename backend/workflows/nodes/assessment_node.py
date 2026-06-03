async def assessment_node(state: dict) -> dict:
    from backend.services.assessment_service import generate_assessment

    pdf_id = state.get("pdf_id")
    if not pdf_id:
        return {**state, "error": "pdf_id ausente", "status": "failed"}
    try:
        import uuid

        pid = uuid.UUID(pdf_id)
    except ValueError:
        return {**state, "error": "pdf_id inválido", "status": "failed"}
    try:
        assessment = await generate_assessment(pid)
        return {
            **state,
            "assessment": assessment.model_dump(mode="json")
            if hasattr(assessment, "model_dump")
            else assessment,
            "progress": 0.4,
            "current_node": "assessment",
        }
    except ValueError as e:
        return {**state, "error": str(e), "status": "failed"}
