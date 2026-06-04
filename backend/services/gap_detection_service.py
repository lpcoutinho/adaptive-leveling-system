"""Serviço de detecção de gaps de conhecimento e análise de prontidão.

Responsável por processar as respostas do quiz, calcular scores por
pré-requisito, identificar gaps e forças, e gerar o resultado de prontidão.
Este serviço é puramente determinístico (sem chamadas LLM).
"""

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

# Pesos para cada nível de importância no cálculo da nota ponderada
IMPORTANCE_WEIGHTS = {"Critical": 3.0, "Important": 2.0, "Helpful": 1.0}
# Abaixo deste score, o tópico é considerado um gap
GAP_THRESHOLD = 60.0
# Acima deste score, o tópico é considerado uma força
STRENGTH_THRESHOLD = 80.0
# Score mínimo para considerar o aluno pronto para a disciplina
READY_THRESHOLD = 80.0
# Score mínimo para considerar que precisa de revisão
NOT_READY_THRESHOLD = 50.0


def _normalize(text: str) -> str:
    """Normaliza texto para comparação (lowercase, sem espaços extras)."""
    return " ".join(text.lower().split())


def _calculate_per_prerequisite_scores(
    answers: list[QuizAnswer],
    knowledge_graph: KnowledgeGraph,
    question_to_prereq: dict[str, str],
) -> dict[str, dict]:
    """
    Calcula o score de domínio para cada pré-requisito baseado nas respostas.

    O matching entre perguntas e pré-requisitos é feito pelo nome do tópico,
    com normalização de texto para tolerar diferenças de capitalização e espaços.

    Args:
        answers: Lista de respostas do aluno.
        knowledge_graph: Grafo de conhecimento com pré-requisitos esperados.
        question_to_prereq: Mapeamento de question_id → nome do pré-requisito.

    Returns:
        Dict com nome do pré-requisito → {score, importance, evaluated}.
    """
    scores: dict[str, dict] = {}

    # 1. Mapeia todos os pré-requisitos conhecidos (usando nome normalizado como chave)
    norm_to_real_name = {}
    for prereq in knowledge_graph.prerequisites:
        norm_name = _normalize(prereq.name)
        norm_to_real_name[norm_name] = prereq.name
        scores[prereq.name] = {"importance": prereq.importance, "scores": [], "tested": False}

    # 2. Atribui os scores das respostas aos respectivos pré-requisitos
    for answer in answers:
        qid = str(answer.question_id)
        topic_name = question_to_prereq.get(qid, "")
        norm_topic = _normalize(topic_name)

        # Tenta match exato ou match normalizado
        target_name = None
        if topic_name in scores:
            target_name = topic_name
        elif norm_topic in norm_to_real_name:
            target_name = norm_to_real_name[norm_topic]

        if target_name:
            scores[target_name]["scores"].append(answer.score)
            scores[target_name]["tested"] = True

    # 3. Converte para formato final: média dos scores ou 0 se não testado
    result = {}
    for name, data in scores.items():
        if data["tested"]:
            avg = sum(data["scores"]) / len(data["scores"])
            result[name] = {"score": avg, "importance": data["importance"], "evaluated": True}
        else:
            result[name] = {"score": 0.0, "importance": data["importance"], "evaluated": False}

    return result


def _weighted_overall_score(
    per_prereq: dict[str, dict],
) -> float:
    """Calcula a nota geral ponderada apenas sobre os tópicos avaliados.

    Pré-requisitos com importância maior (Critical) têm peso maior no cálculo.
    Tópicos não avaliados são ignorados para não distorcer a média.

    Args:
        per_prereq: Dict com scores por pré-requisito.

    Returns:
        Score ponderado entre 0 e 100.
    """
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
    """Classifica o nível de prontidão do aluno com base no score geral."""
    if overall_score >= READY_THRESHOLD:
        return ReadinessLevel.READY
    if overall_score >= NOT_READY_THRESHOLD:
        return ReadinessLevel.NEEDS_REVIEW
    return ReadinessLevel.NOT_READY


def _identify_gaps_and_strengths(
    per_prereq: dict[str, dict],
) -> tuple[list[GapAnalysis], list[GapAnalysis]]:
    """
    Identifica gaps (score < threshold) e forças (score >= threshold).

    Args:
        per_prereq: Dict com scores por pré-requisito.

    Returns:
        Tupla (gaps, strengths) com listas de GapAnalysis.
    """
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
    """
    Ordena gaps por importância (Critical primeiro) e depois por score (menor primeiro).

    Args:
        gaps: Lista de gaps não ordenada.

    Returns:
        Lista ordenada: Critical → Important → Helpful, e menor score primeiro.
    """
    weight_map = IMPORTANCE_WEIGHTS
    return sorted(
        gaps,
        key=lambda g: (
            -(weight_map.get(g.importance, 1)),
            g.score,
        ),
    )


async def analyze_gaps(session_id: UUID, pdf_id: UUID) -> ReadinessResult:
    """
    Analisa as respostas do quiz e gera um diagnóstico completo de prontidão.

    Fluxo:
    1. Busca a sessão do quiz e o grafo de conhecimento
    2. Mapeia perguntas para pré-requisitos
    3. Calcula scores por pré-requisito
    4. Classifica nível de prontidão
    5. Identifica gaps e forças
    6. Prioriza gaps por importância
    7. Persiste e retorna o resultado

    Args:
        session_id: ID da sessão do quiz.
        pdf_id: ID do PDF original.

    Returns:
        ReadinessResult: Diagnóstico completo de prontidão.

    Raises:
        ValueError: Se sessão ou grafo de conhecimento não forem encontrados.
    """
    session = await get_quiz_session(session_id)
    if not session:
        raise ValueError("Sessão de quiz não encontrada.")

    knowledge_graph = await get_knowledge_graph_by_pdf_id(pdf_id)
    if not knowledge_graph:
        raise ValueError("Grafo de conhecimento não encontrado para o PDF.")

    answers = session.answers
    assessment = await get_assessment_by_id(UUID(session.assessment_id))

    # 1. Monta mapeamento: question_id → nome do tópico (pré-requisito)
    mapping: dict[str, str] = {}
    if assessment:
        for q in assessment.questions:
            mapping[str(q.id)] = q.topic.strip()

    # 2. Calcula scores por pré-requisito
    per_prereq = _calculate_per_prerequisite_scores(answers, knowledge_graph, mapping)
    overall_score = _weighted_overall_score(per_prereq)
    level = _classify_readiness(overall_score)
    gaps, strengths = _identify_gaps_and_strengths(per_prereq)
    prioritized_gaps = _prioritize_gaps(gaps)

    # 3. Apenas pré-requisitos avaliados contam para o resumo
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
