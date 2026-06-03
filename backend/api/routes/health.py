"""Rotas de monitoramento de saúde do sistema."""

from fastapi import APIRouter

from backend.infrastructure.cache import ping_cache
from backend.infrastructure.database import ping_database
from backend.infrastructure.storage import ping_s3
from backend.llm.factory import LLMFactory

router = APIRouter(prefix="/health", tags=["Monitoring"])


@router.get("/")
async def health_check():
    """Retorna o status geral da API."""
    return {"status": "healthy", "version": "0.1.0"}


@router.get("/detailed")
async def detailed_health_check():
    """Verifica a conectividade com todos os serviços externos."""
    db_ok = await ping_database()
    cache_ok = await ping_cache()
    s3_ok = await ping_s3()

    llm_provider = "unknown"
    llm_configured = False
    try:
        provider = LLMFactory.get_provider()
        llm_provider = provider.get_provider_name()
        llm_configured = LLMFactory.is_configured()
    except Exception:
        llm_provider = "unavailable"

    return {
        "api": "up",
        "database": "connected" if db_ok else "disconnected",
        "cache": "connected" if cache_ok else "disconnected",
        "storage": "connected" if s3_ok else "disconnected",
        "llm_provider": llm_provider,
        "llm_configured": llm_configured,
    }
