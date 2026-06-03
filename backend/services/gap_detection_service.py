from uuid import UUID

from loguru import logger

from backend.domain.models.prerequisite import KnowledgeGraph
from backend.domain.models.quiz import QuizAnswer
from backend.domain.models.readiness import (
    GapAnalysis,
    ReadinessLevel,
    ReadinessResult,
)
from backend.infrastructure.repository.assessment_repository import get_assessment_by_id
from backend.infrastructure.repository.prerequisite_repository import get_knowledge_graph_by_pdf_id
from backend.infrastructure.repository.readiness_repository import (
    save_readiness_result,
)
from backend.infrastructure.repository.student_repository import get_quiz_session

IMPORTANCE_WEIGHTS = {"Critical": 3.0, "Important": 2.0, "Helpful": 1.0}
GAP_THRESHOLD = 60.0
STRENGTH_THRESHOLD = 80.0
READY_THRESHOLD = 80.0
NOT_READY_THRESHOLD = 50.0


def _calculate_per_prerequisite_scores(
    answers: list[QuizAnswer],
    knowledge_graph: KnowledgeGraph,
    question_to_prereq: dict[str, str],
) -> dict[str, dict]:
    """Calcula o score de domínio para cada pré-requisito baseado nas respostas."""
    scores: dict[str, dict] = {}

    # 1. Mapeia todos os pré-requisitos conhecidos
    for prereq in knowledge_graph.prerequisites:
        scores[prereq.name] = {"importance": prereq.importance, "scores": [], "tested": False}

    # 2. Atribui os scores das respostas aos respectivos pré-requisitos
    for answer in answers:
        qid = str(answer.question_id)
        prereq_name = question_to_prereq.get(qid)

        if prereq_name and prereq_name in scores:
            scores[prereq_name]["scores"].append(answer.score)
            scores[prereq_name]["tested"] = True

    result = {}
    for name, data in scores.items():
        # Se o tópico foi testado, tira a média.
        # Para ser justo, vamos considerar apenas o que foi testado para o score.
        if data["tested"]:
            avg = sum(data["scores"]) / len(data["scores"])
            result[name] = {"score": avg, "importance": data["importance"], "evaluated": True}
        else:
            # Tópicos não testados não devem penalizar o aluno na média geral
            result[name] = {"score": 0.0, "importance": data["importance"], "evaluated": False}

    return result


def _weighted_overall_score(
    per_prereq: dict[str, dict],
) -> float:
    """Calcula a nota geral ponderada apenas sobre os tópicos avaliados."""
    total_weight = 0.0
    weighted_sum = 0.0

    for data in per_prereq.values():
        if not data["evaluated"]:
            continue

        weight = IMPORTANCE_WEIGHTS.get(data["importance"], 1.0)
        weighted_sum += data["score"] * weight
        total_weight += weight

    if total_weight == 0:
        return 0.0

    return round(weighted_sum / total_weight, 2)


def _classify_readiness(overall_score: float) -> ReadinessLevel:
    if overall_score >= READY_THRESHOLD:
        return ReadinessLevel.READY
    if overall_score >= NOT_READY_THRESHOLD:
        return ReadinessLevel.NEEDS_REVIEW
    return ReadinessLevel.NOT_READY


def _identify_gaps_and_strengths(
    per_prereq: dict[str, dict],
) -> tuple[list[GapAnalysis], list[GapAnalysis]]:
    gaps: list[GapAnalysis] = []
    strengths: list[GapAnalysis] = []

    for name, data in per_prereq.items():
        if not data["evaluated"]:
            continue

        score = data["score"]
        importance = data["importance"]
        is_gap = score < GAP_THRESHOLD
        is_strength = score >= STRENGTH_THRESHOLD

        analysis = GapAnalysis(
            prerequisite_name=name,
            score=round(score, 2),
            importance=importance,
            is_gap=is_gap,
            is_strength=is_strength,
        )

        if is_gap:
            gaps.append(analysis)
        if is_strength:
            strengths.append(analysis)

    return gaps, strengths


def _prioritize_gaps(gaps: list[GapAnalysis]) -> list[GapAnalysis]:
    weight_map = IMPORTANCE_WEIGHTS
    return sorted(
        gaps,
        key=lambda g: (
            -(weight_map.get(g.importance, 1)),
            g.score,
        ),
    )


async def analyze_gaps(session_id: UUID, pdf_id: UUID) -> ReadinessResult:
    session = await get_quiz_session(session_id)
    if not session:
        raise ValueError("Sessão de quiz não encontrada.")

    knowledge_graph = await get_knowledge_graph_by_pdf_id(pdf_id)
    if not knowledge_graph:
        raise ValueError("Grafo de conhecimento não encontrado para o PDF.")

    answers = session.answers
    assessment = await get_assessment_by_id(UUID(session.assessment_id))

    mapping: dict[str, str] = {}
    if assessment:
        for q in assessment.questions:
            # Garante que o mapeamento de tópico esteja limpo
            mapping[str(q.id)] = q.topic.strip()

    per_prereq = _calculate_per_prerequisite_scores(answers, knowledge_graph, mapping)
    overall_score = _weighted_overall_score(per_prereq)
    level = _classify_readiness(overall_score)
    gaps, strengths = _identify_gaps_and_strengths(per_prereq)
    prioritized_gaps = _prioritize_gaps(gaps)

    # Apenas pré-requisitos avaliados contam para o resumo
    evaluated_prereqs = [name for name, data in per_prereq.items() if data["evaluated"]]

    result = ReadinessResult(
        session_id=session_id,
        pdf_id=pdf_id,
        overall_score=overall_score,
        level=level,
        gaps=prioritized_gaps,
        strengths=strengths,
        total_prerequisites=len(evaluated_prereqs),
        total_gaps=len(prioritized_gaps),
        total_strengths=len(strengths),
    )

    logger.success(
        f"Análise concluída para sessão {session_id}: "
        f"{len(prioritized_gaps)} gaps, {len(strengths)} forças."
    )
    return await save_readiness_result(result)
