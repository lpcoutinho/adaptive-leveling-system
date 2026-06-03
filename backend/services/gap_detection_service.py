from uuid import UUID

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
    get_readiness_by_session,
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
    question_to_prereq: dict[str, str] | None = None,
) -> dict[str, dict]:
    scores: dict[str, dict] = {}
    for prereq in knowledge_graph.prerequisites:
        scores[prereq.name] = {
            "importance": prereq.importance,
            "scores": [],
            "count": 0,
        }
    for answer in answers:
        qid = str(answer.question_id)
        prereq_name = question_to_prereq.get(qid, qid) if question_to_prereq else qid
        if prereq_name not in scores:
            scores[prereq_name] = {"importance": "Helpful", "scores": [], "count": 0}
        scores[prereq_name]["scores"].append(answer.score)
        scores[prereq_name]["count"] += 1
    result = {}
    for name, data in scores.items():
        avg = sum(data["scores"]) / len(data["scores"]) if data["scores"] else 0.0
        result[name] = {"score": avg, "importance": data["importance"]}
    return result


def _weighted_overall_score(
    per_prereq: dict[str, dict],
) -> float:
    total_weight = 0.0
    weighted_sum = 0.0
    for data in per_prereq.values():
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
    existing = await get_readiness_by_session(session_id)
    if existing:
        return existing

    session = await get_quiz_session(session_id)
    if not session:
        raise ValueError("Sessão de quiz não encontrada.")

    knowledge_graph = await get_knowledge_graph_by_pdf_id(pdf_id)
    if not knowledge_graph:
        raise ValueError("Grafo de conhecimento não encontrado para o PDF.")

    answers = session.answers
    assessment = await get_assessment_by_id(UUID(session.assessment_id))
    mapping = {}
    if assessment:
        for q in assessment.questions:
            mapping[str(q.id)] = q.topic
    per_prereq = _calculate_per_prerequisite_scores(answers, knowledge_graph, mapping)
    overall_score = _weighted_overall_score(per_prereq)
    level = _classify_readiness(overall_score)
    gaps, strengths = _identify_gaps_and_strengths(per_prereq)
    prioritized_gaps = _prioritize_gaps(gaps)
    total_prerequisites = len(knowledge_graph.prerequisites)

    result = ReadinessResult(
        session_id=session_id,
        pdf_id=pdf_id,
        overall_score=overall_score,
        level=level,
        gaps=prioritized_gaps,
        strengths=strengths,
        total_prerequisites=total_prerequisites,
        total_gaps=len(prioritized_gaps),
        total_strengths=len(strengths),
    )

    return await save_readiness_result(result)
