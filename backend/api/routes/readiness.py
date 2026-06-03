from uuid import UUID

from fastapi import APIRouter, HTTPException

from backend.api.schemas.readiness import AnalyzeRequest, ReadinessResponse
from backend.infrastructure.repository.readiness_repository import (
    get_readiness_by_session,
)
from backend.services.gap_detection_service import analyze_gaps

router = APIRouter(prefix="/readiness", tags=["Readiness"])


@router.post("/analyze", response_model=ReadinessResponse, status_code=201)
async def trigger_readiness_analysis(request: AnalyzeRequest):
    """Analisa prontidão do aluno a partir dos resultados do quiz."""
    try:
        result = await analyze_gaps(request.session_id, request.pdf_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro na análise de prontidão: {str(e)}"
        ) from e


@router.get("/{session_id}", response_model=ReadinessResponse)
async def get_readiness(session_id: UUID):
    """Recupera o resultado de prontidão de uma sessão de quiz."""
    result = await get_readiness_by_session(session_id)
    if not result:
        raise HTTPException(
            status_code=404, detail="Análise de prontidão não encontrada para esta sessão."
        )
    return result
