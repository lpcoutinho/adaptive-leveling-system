"""Cache de sessão de estudante no Valkey."""

import json
from uuid import UUID

from backend.domain.models.quiz import QuizSession
from backend.infrastructure.cache import cache_delete, cache_get, cache_set

SESSION_TTL = 3600  # 1 hora


async def save_session(session: QuizSession) -> bool:
    """Salva sessão no cache."""
    key = f"quiz:session:{session.id}"
    data = session.model_dump(mode="json", exclude={"created_at", "updated_at"})
    return await cache_set(key, json.dumps(data), ttl=SESSION_TTL)


async def get_session(session_id: UUID) -> QuizSession | None:
    """Recupera sessão do cache."""
    key = f"quiz:session:{session_id}"
    raw = await cache_get(key)
    if not raw:
        return None
    return QuizSession.model_validate(json.loads(raw))


async def delete_session(session_id: UUID) -> bool:
    """Remove sessão do cache."""

    return await cache_delete(f"quiz:session:{session_id}")
