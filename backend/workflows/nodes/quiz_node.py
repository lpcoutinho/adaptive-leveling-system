async def quiz_node(state: dict) -> dict:
    import uuid

    from backend.infrastructure.repository.assessment_repository import get_assessment_by_pdf_id
    from backend.infrastructure.repository.student_repository import (
        get_quiz_session,
        save_quiz_session,
    )
    from backend.services.quiz_service import start_quiz
    from backend.workflows.states import WorkflowStatus

    pdf_id_raw = state.get("pdf_id")
    assessment_raw = state.get("assessment")

    if not pdf_id_raw:
        return {**state, "error": "pdf_id obrigatório no Quiz", "status": "failed"}

    try:
        pdf_id = uuid.UUID(pdf_id_raw)
    except ValueError:
        return {**state, "error": "pdf_id inválido", "status": "failed"}

    # Recuperação defensiva: se o assessment sumiu do estado, busca no banco
    if not assessment_raw:
        assessment_obj = await get_assessment_by_pdf_id(pdf_id)
        if not assessment_obj:
            return {**state, "error": "Avaliação não encontrada para este PDF", "status": "failed"}
        assessment_raw = assessment_obj.model_dump(mode="json")
        state["assessment"] = assessment_raw

    session_id = state.get("session_id")

    # Se já temos uma sessão, verifica se ela foi concluída
    if session_id:
        try:
            session = await get_quiz_session(uuid.UUID(session_id))
            if session and session.status.value == "completed":
                return {
                    **state,
                    "status": WorkflowStatus.IN_PROGRESS.value,
                    "quiz_session": session.model_dump(mode="json"),
                    "progress": 0.7,
                    "current_node": "quiz",
                }
            else:
                return {**state, "status": "awaiting_input", "current_node": "quiz"}
        except Exception as e:
            return {**state, "error": f"Erro ao validar quiz: {str(e)}", "status": "failed"}

    # Cria nova sessão se necessário
    try:
        student_id = uuid.uuid4()
        session = await start_quiz(
            assessment_id=uuid.UUID(assessment_raw["id"]), student_id=str(student_id)
        )
        await save_quiz_session(session)

        return {
            **state,
            "session_id": str(session.id),
            "quiz_session": session.model_dump(mode="json"),
            "status": "awaiting_input",
            "progress": 0.6,
            "current_node": "quiz",
        }
    except Exception as e:
        return {**state, "error": f"Erro ao criar quiz: {str(e)}", "status": "failed"}
