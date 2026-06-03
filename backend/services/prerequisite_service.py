"""Serviço para orquestração da extração de inteligência via LLM."""

import os
from uuid import UUID

from backend.domain.models.prerequisite import KnowledgeGraph
from backend.infrastructure.repository.pdf_repository import get_pdf_by_id
from backend.infrastructure.repository.prerequisite_repository import (
    get_knowledge_graph_by_pdf_id,
    save_knowledge_graph,
)
from backend.llm.factory import LLMFactory


def _load_prompt_template() -> str:
    """Carrega o template do prompt do arquivo de texto."""
    prompt_path = os.path.join(
        os.path.dirname(__file__), "..", "llm", "prompts", "prerequisite_extractor_v1.txt"
    )
    with open(prompt_path, encoding="utf-8") as f:
        return f.read()


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
    if existing_graph and (existing_graph.main_concepts or existing_graph.prerequisites):
        return existing_graph

    # 2. Busca o texto extraído do PDF
    pdf_doc = await get_pdf_by_id(pdf_id)
    if not pdf_doc or not pdf_doc.content_text:
        raise ValueError(f"PDF {pdf_id} não encontrado ou sem texto extraído.")

    # 3. Prepara o prompt
    template = _load_prompt_template()
    prompt = template.replace("{{content_text}}", pdf_doc.content_text)

    # 4. Chama o LLM (via Camada de Abstração)
    llm = LLMFactory.get_provider()

    # generate_structured espera o prompt e a classe Pydantic (response_model)
    # Nota: KnowledgeGraph no domínio tem UUIDModel e TimestampModel,
    # mas o LLM só deve preencher main_concepts e prerequisites.
    graph_data = await llm.generate_structured(prompt, response_model=KnowledgeGraph)

    # 5. Vincula o pdf_id e salva no banco
    graph_data.pdf_id = str(pdf_id)
    saved_graph = await save_knowledge_graph(graph_data)

    return saved_graph
