async def quiz_node(state: dict) -> dict:
    from backend.infrastructure.repository.student_repository import save_quiz_session
    from backend.services.quiz_service import start_quiz

    pdf_id = state.get("pdf_id")
    assessment = state.get("assessment")
    if not pdf_id or not assessment:
        return {**state, "error": "pdf_id e assessment obrigatórios", "status": "failed"}
    try:
        import uuid

        uuid.UUID(pdf_id)
    except ValueError:
        return {**state, "error": "pdf_id inválido", "status": "failed"}

    if state.get("session_id"):
        return {**state, "progress": 0.6, "current_node": "quiz"}

    try:
        student_id = uuid.uuid4()
        session = await start_quiz(
            assessment_id=uuid.UUID(assessment["id"]), student_id=str(student_id)
        )
        await save_quiz_session(session)
        session_id = str(session.id)
        return {
            **state,
            "session_id": session_id,
            "quiz_session": session.model_dump(mode="json")
            if hasattr(session, "model_dump")
            else {},
            "progress": 0.6,
            "current_node": "quiz",
        }
    except Exception as e:
        return {**state, "error": f"Erro ao criar quiz: {str(e)}", "status": "failed"}
