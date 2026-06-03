async def leveling_node(state: dict) -> dict:
    from backend.llm.factory import LLMFactory
    from backend.services.leveling_service import generate_leveling_plan

    session_id = state.get("session_id")
    readiness_id = state.get("readiness_id")
    if not readiness_id and not session_id:
        return {**state, "error": "readiness_id ou session_id obrigatório", "status": "failed"}
    try:
        import uuid

        rid = uuid.UUID(readiness_id) if readiness_id else uuid.UUID(session_id)
        sid = uuid.UUID(session_id) if session_id else rid
    except ValueError:
        return {**state, "error": "UUID inválido", "status": "failed"}
    try:
        llm = LLMFactory.get_provider()
        plan = await generate_leveling_plan(session_id=sid, readiness_id=rid, llm=llm)
        return {
            **state,
            "leveling_plan": plan.model_dump(mode="json") if hasattr(plan, "model_dump") else plan,
            "progress": 1.0,
            "current_node": "leveling",
            "status": "completed",
        }
    except ValueError as e:
        return {**state, "error": str(e), "status": "failed"}
