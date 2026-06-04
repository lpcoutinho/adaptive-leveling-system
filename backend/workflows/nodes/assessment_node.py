async def assessment_node(state: dict) -> dict:
    from backend.infrastructure.repository.assessment_repository import get_assessment_by_pdf_id
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
        # Tenta recuperar do banco primeiro (idempotência defensiva)
        assessment = await get_assessment_by_pdf_id(pid)
        if not assessment:
            assessment = await generate_assessment(pid)

        return {
            **state,
            "assessment": assessment.model_dump(mode="json")
            if hasattr(assessment, "model_dump")
            else assessment,
            "progress": 0.4,
            "current_node": "assessment",
            "status": "in_progress",  # Garante que o status não seja perdido
        }
    except Exception as e:
        return {**state, "error": f"Erro no assessment: {str(e)}", "status": "failed"}
