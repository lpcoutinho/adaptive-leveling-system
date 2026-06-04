"""Nó do LangGraph responsável pela etapa de quiz do workflow.

Gerencia o ciclo de vida da sessão de quiz:
1. Cria uma nova sessão se não existir → pausa para input do aluno
2. Verifica se a sessão existente foi concluída → avança para readiness
3. Se ainda está em andamento → mantém pausa (awaiting_input)
"""


async def quiz_node(state: dict) -> dict:
    """
    Nó do workflow que gerencia o quiz do aluno.

    Comportamento:
    - Se não há session_id: cria nova sessão de quiz e pausa (awaiting_input)
    - Se há sessão não concluída: mantém pausa
    - Se há sessão concluída: avança para o próximo nó (readiness)

    Args:
        state: Estado atual do workflow contendo pdf_id e assessment.

    Returns:
        Estado atualizado com status e dados da sessão do quiz.
    """
    from backend.infrastructure.repository.student_repository import (
        get_quiz_session,
        save_quiz_session,
    )
    from backend.services.quiz_service import start_quiz
    from backend.workflows.states import WorkflowStatus

    pdf_id = state.get("pdf_id")
    assessment = state.get("assessment")
    if not pdf_id or not assessment:
        return {**state, "error": "pdf_id e assessment obrigatórios", "status": "failed"}
    try:
        import uuid

        uuid.UUID(pdf_id)
    except ValueError:
        return {**state, "error": "pdf_id inválido", "status": "failed"}

    session_id = state.get("session_id")

    # 1. Se já temos uma sessão, verifica se ela foi concluída
    if session_id:
        try:
            session = await get_quiz_session(uuid.UUID(session_id))
            if session and session.status.value == "completed":
                # Quiz finalizado! Avançamos para o próximo nó
                return {
                    **state,
                    "status": WorkflowStatus.IN_PROGRESS.value,
                    "quiz_session": session.model_dump(mode="json"),
                    "progress": 0.7,
                    "current_node": "quiz",
                }
            else:
                # Ainda esperando o aluno responder
                return {**state, "status": "awaiting_input", "current_node": "quiz"}
        except Exception as e:
            return {**state, "error": f"Erro ao validar quiz: {str(e)}", "status": "failed"}

    # 2. Se não temos sessão, cria uma nova e pausa para o aluno responder
    try:
        student_id = uuid.uuid4()
        session = await start_quiz(
            assessment_id=uuid.UUID(assessment["id"]), student_id=str(student_id)
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
