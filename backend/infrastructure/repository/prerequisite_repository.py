"""Repositório para persistência do grafo de conhecimento e pré-requisitos."""

import json
from uuid import UUID

from backend.domain.models.prerequisite import ConceptNode, KnowledgeGraph, Prerequisite
from backend.infrastructure.database import execute_query


async def save_knowledge_graph(graph: KnowledgeGraph) -> KnowledgeGraph:
    """
    Salva o grafo de conhecimento extraído no banco de dados.

    Args:
        graph: Instância do KnowledgeGraph preenchida.

    Returns:
        KnowledgeGraph: O grafo salvo com IDs e timestamps atualizados.
    """
    query = """
        INSERT INTO prerequisites_graph (id, pdf_id, main_concepts, prerequisites)
        VALUES ($1, $2, $3, $4)
        ON CONFLICT (pdf_id) DO UPDATE
        SET main_concepts = EXCLUDED.main_concepts,
            prerequisites = EXCLUDED.prerequisites,
            updated_at = NOW()
        RETURNING id, created_at, updated_at
    """

    # Serialização manual para JSON para garantir compatibilidade JSONB
    main_concepts_json = [c.model_dump() for c in graph.main_concepts]
    prerequisites_json = [p.model_dump() for p in graph.prerequisites]

    result = await execute_query(
        query,
        graph.id,
        UUID(graph.pdf_id) if isinstance(graph.pdf_id, str) else graph.pdf_id,
        json.dumps(main_concepts_json),
        json.dumps(prerequisites_json),
    )

    if result:
        row = result[0]
        graph.id = row["id"]
        graph.created_at = row["created_at"]
        graph.updated_at = row["updated_at"]

    return graph


async def get_knowledge_graph_by_pdf_id(pdf_id: UUID) -> KnowledgeGraph | None:
    """
    Busca o grafo de conhecimento associado a um PDF.

    Args:
        pdf_id: UUID do PDF.

    Returns:
        Optional[KnowledgeGraph]: O grafo encontrado ou None.
    """
    query = "SELECT * FROM prerequisites_graph WHERE pdf_id = $1"
    result = await execute_query(query, pdf_id)

    if not result:
        return None

    row = result[0]

    # Reconstrução dos modelos a partir do JSONB (que vem como string ou dict)
    main_concepts_data = row["main_concepts"]
    if isinstance(main_concepts_data, str):
        main_concepts_data = json.loads(main_concepts_data)

    prerequisites_data = row["prerequisites"]
    if isinstance(prerequisites_data, str):
        prerequisites_data = json.loads(prerequisites_data)

    return KnowledgeGraph(
        id=row["id"],
        pdf_id=str(row["pdf_id"]),
        main_concepts=[ConceptNode(**c) for c in main_concepts_data],
        prerequisites=[Prerequisite(**p) for p in prerequisites_data],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )
