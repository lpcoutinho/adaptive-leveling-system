"""Rotas de monitoramento de saúde do sistema."""
from fastapi import APIRouter, Depends
from backend.infrastructure.database import ping_database
from backend.infrastructure.cache import ping_cache
from backend.infrastructure.storage import ping_s3
from backend.llm.base.interface import ILLMProvider
from backend.api.dependencies.llm import get_llm_provider

router = APIRouter(prefix="/health", tags=["Monitoring"])


@router.get("/")
async def health_check():
    """Retorna o status geral da API."""
    return {"status": "healthy", "version": "0.1.0"}


@router.get("/detailed")
async def detailed_health_check(
    llm: ILLMProvider = Depends(get_llm_provider)
):
    """Verifica a conectividade com todos os serviços externos."""
    db_ok = await ping_database()
    cache_ok = await ping_cache()
    s3_ok = await ping_s3()
    
    return {
        "api": "up",
        "database": "connected" if db_ok else "disconnected",
        "cache": "connected" if cache_ok else "disconnected",
        "storage": "connected" if s3_ok else "disconnected",
        "llm_provider": llm.get_provider_name()
    }
