"""Serviço para orquestração da extração de inteligência via LLM."""

from uuid import UUID

from pydantic import BaseModel

from backend.api.dependencies.llm import get_llm_provider
from backend.domain.models.prerequisite import ConceptNode, KnowledgeGraph, Prerequisite
from backend.infrastructure.repository.pdf_repository import get_pdf_by_id
from backend.infrastructure.repository.prerequisite_repository import (
    get_knowledge_graph_by_pdf_id,
    save_knowledge_graph,
)
from backend.llm.prompt_router import PromptUseCase, get_prompt_router


class LLMExtractionSchema(BaseModel):
    """Schema simplificado para o LLM preencher."""

    main_concepts: list[ConceptNode]
    prerequisites: list[Prerequisite]


async def extract_prerequisites(pdf_id: UUID) -> KnowledgeGraph:
    """
    Extrai conceitos e pré-requisitos de um PDF usando LLM.

    Args:
        pdf_id: UUID do documento PDF já processado.

    Returns:
        KnowledgeGraph: O grafo de conhecimento extraído.
    """
    # 1. Verifica se já existe análise no banco (Idempotência)
    existing_graph = await get_knowledge_graph_by_pdf_id(pdf_id)
    if existing_graph:
        return existing_graph

    # 2. Busca o texto extraído do PDF
    pdf_doc = await get_pdf_by_id(pdf_id)
    if not pdf_doc or not pdf_doc.content_text:
        raise ValueError(f"PDF {pdf_id} não encontrado ou sem texto extraído.")

    # 3. Prepara o prompt via PromptRouter
    router = get_prompt_router()
    template = router.get_prompt(PromptUseCase.PREREQUISITE_EXTRACTOR)
    prompt = template.replace("{{content_text}}", pdf_doc.content_text)

    # 4. Chama o LLM (via Camada de Abstração)
    llm = get_llm_provider()

    # Usamos LLMExtractionSchema para evitar erros com campos de ID/Timestamp do domínio
    extracted_data = await llm.generate_structured(prompt, response_model=LLMExtractionSchema)

    # 5. Vincula o pdf_id e salva no banco
    graph = KnowledgeGraph(
        pdf_id=pdf_id,
        main_concepts=extracted_data.main_concepts,
        prerequisites=extracted_data.prerequisites,
    )

    saved_graph = await save_knowledge_graph(graph)

    return saved_graph
