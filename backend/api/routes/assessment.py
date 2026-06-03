"""Endpoints da API para geração e consulta de avaliações diagnósticas."""

from uuid import UUID

from fastapi import APIRouter, HTTPException

from backend.api.schemas.assessment import AssessmentResponse
from backend.infrastructure.repository.assessment_repository import (
    get_assessment_by_id,
    get_assessment_by_pdf_id,
)
from backend.services.assessment_service import generate_assessment

router = APIRouter(prefix="/assessment", tags=["Assessment"])


@router.post("/generate/{pdf_id}", response_model=AssessmentResponse, status_code=201)
async def trigger_assessment_generation(pdf_id: UUID):
    """Gera uma avaliação diagnóstica para um PDF com pré-requisitos extraídos."""
    try:
        assessment = await generate_assessment(pdf_id)
        return assessment
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro na geração da avaliação: {str(e)}"
        ) from e


@router.get("/{assessment_id}", response_model=AssessmentResponse)
async def get_assessment(assessment_id: UUID):
    """Recupera uma avaliação diagnóstica pelo ID."""
    assessment = await get_assessment_by_id(assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Avaliação não encontrada.")
    return assessment


@router.get("/pdf/{pdf_id}", response_model=AssessmentResponse)
async def get_assessment_by_pdf(pdf_id: UUID):
    """Recupera a avaliação associada a um PDF."""
    assessment = await get_assessment_by_pdf_id(pdf_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Nenhuma avaliação encontrada para este PDF.")
    return assessment
