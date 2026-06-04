"""Serviço para orquestração da geração de avaliações diagnósticas via LLM."""

import json
from uuid import UUID

from loguru import logger
from pydantic import BaseModel

from backend.domain.models.assessment import Assessment, QuizQuestion
from backend.infrastructure.repository.assessment_repository import (
    get_assessment_by_pdf_id,
    save_assessment,
)
from backend.infrastructure.repository.prerequisite_repository import (
    get_knowledge_graph_by_pdf_id,
)
from backend.llm.factory import LLMFactory
from backend.llm.prompt_router import PromptUseCase, get_prompt_router


class AssessmentPrompt(BaseModel):
    """Modelo interno para structured output do LLM (apenas questions)."""

    questions: list[QuizQuestion]


async def generate_assessment(pdf_id: UUID) -> Assessment:
    """Gera uma avaliação diagnóstica para os pré-requisitos de um PDF.

    Args:
        pdf_id: UUID do PDF com pré-requisitos extraídos.

    Returns:
        Assessment: Avaliação com questões geradas.

    Raises:
        ValueError: Se o PDF não tiver pré-requisitos extraídos.
    """
    logger.info(f"Iniciando geração de avaliação para PDF {pdf_id}...")
    existing = await get_assessment_by_pdf_id(pdf_id)
    if existing and existing.questions:
        logger.info(f"Avaliação existente encontrada para PDF {pdf_id}. Reutilizando...")
        return existing

    graph = await get_knowledge_graph_by_pdf_id(pdf_id)
    if not graph or not graph.prerequisites:
        logger.error(f"Nenhum pré-requisito encontrado para o PDF {pdf_id}.")
        raise ValueError(
            f"Nenhum pré-requisito encontrado para o PDF {pdf_id}. "
            "Execute a extração de pré-requisitos primeiro."
        )

    router = get_prompt_router()
    template = router.get_prompt(PromptUseCase.ASSESSMENT_GENERATOR)
    prerequisites_json = json.dumps(
        [p.model_dump() for p in graph.prerequisites], indent=2, ensure_ascii=False
    )
    prompt = template.replace("{{prerequisites_json}}", prerequisites_json)

    llm = LLMFactory.get_provider()
    result = await llm.generate_structured(prompt, response_model=AssessmentPrompt)

    assessment = Assessment(
        pdf_id=str(pdf_id),
        questions=result.questions,
    )
    saved = await save_assessment(assessment)
    logger.success(f"Avaliação gerada com sucesso para o PDF {pdf_id}.")
    return saved
