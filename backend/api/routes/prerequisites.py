"""Endpoints da API para extração e consulta de pré-requisitos."""

from uuid import UUID

from fastapi import APIRouter, HTTPException

from backend.api.schemas.prerequisite import KnowledgeGraphResponse
from backend.infrastructure.repository.prerequisite_repository import get_knowledge_graph_by_pdf_id
from backend.services.prerequisite_service import extract_prerequisites

router = APIRouter(prefix="/prerequisites", tags=["Intelligence"])


@router.post("/extract/{pdf_id}", response_model=KnowledgeGraphResponse, status_code=201)
async def trigger_extraction(pdf_id: UUID):
    """
    Solicita a extração de conceitos e pré-requisitos de um PDF já processado.

    Este endpoint aciona o LLM para analisar o texto e estruturar o conhecimento.
    """
    try:
        graph = await extract_prerequisites(pdf_id)
        return graph
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na extração via LLM: {str(e)}") from e


@router.get("/{pdf_id}", response_model=KnowledgeGraphResponse)
async def get_prerequisites(pdf_id: UUID):
    """
    Recupera a análise de pré-requisitos já realizada para um PDF.
    """
    graph = await get_knowledge_graph_by_pdf_id(pdf_id)
    if not graph:
        raise HTTPException(status_code=404, detail="Análise não encontrada para este PDF.")
    return graph
