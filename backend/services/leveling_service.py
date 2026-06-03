"""Serviço de geração de conteúdo de nivelamento."""

from uuid import UUID

from backend.domain.models.leveling import GapExplanation, LevelingPlan, StudyStep
from backend.infrastructure.repository.leveling_repository import (
    get_plan_by_readiness,
    save_leveling_plan,
)
from backend.infrastructure.repository.readiness_repository import (
    get_readiness_by_id,
    get_readiness_by_session,
)
from backend.llm.base.interface import ILLMProvider

IMPORTANCE_WEIGHTS = {"Critical": 3.0, "Important": 2.0, "Helpful": 1.0}


def _load_prompt_template() -> str:
    path = "backend/llm/prompts/leveling_generator_v1.txt"
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError:
        return _fallback_prompt()


def _fallback_prompt() -> str:
    return (
        "Gere uma explicação educacional para o gap '{gap_name}' "
        "(importância: {importance}, score atual: {current_score}%). "
        "Inclua: why_important, explanation, calculus_example, exercise, exercise_answer."
    )


def _build_study_order(
    gaps: list[GapExplanation],
) -> list[StudyStep]:
    weight_map = IMPORTANCE_WEIGHTS
    sorted_gaps = sorted(
        gaps,
        key=lambda g: (
            -(weight_map.get(g.importance, 1)),
            g.current_score,
        ),
    )
    return [StudyStep(order=i + 1, gap_name=g.gap_name) for i, g in enumerate(sorted_gaps)]


async def generate_leveling_plan(
    session_id: UUID,
    readiness_id: UUID,
    llm: ILLMProvider,
) -> LevelingPlan:
    existing = await get_plan_by_readiness(readiness_id)
    if existing:
        return existing

    result = await get_readiness_by_id(readiness_id)
    if not result:
        result = await get_readiness_by_session(session_id)
    if not result:
        raise ValueError("Resultado de prontidão não encontrado.")

    gaps = result.gaps
    strengths_names = [s.prerequisite_name for s in result.strengths]
    strengths_str = ", ".join(strengths_names) if strengths_names else "Nenhuma força identificada"
    template = _load_prompt_template()

    explanations: list[GapExplanation] = []
    for gap in gaps:
        try:
            prompt = template.format(
                gap_name=gap.prerequisite_name,
                importance=gap.importance,
                current_score=gap.score,
                strengths=strengths_str,
            )
            expl = await llm.generate_structured(prompt, GapExplanation)
            explanations.append(expl)
        except Exception:
            explanations.append(
                GapExplanation(
                    gap_name=gap.prerequisite_name,
                    importance=gap.importance,
                    current_score=gap.score,
                    why_important="Conceito fundamental para Cálculo I.",
                    explanation=(
                        f"{gap.prerequisite_name} é um conceito básico que precisa ser revisado."
                    ),
                    calculus_example="Consulte seu material didático.",
                    exercise="Pratique com exercícios do seu livro texto.",
                    exercise_answer="Verifique com seu professor.",
                )
            )

    study_order = _build_study_order(explanations)
    plan = LevelingPlan(
        readiness_id=readiness_id,
        explanations=explanations,
        study_order=study_order,
        total_gaps=len(explanations),
    )
    return await save_leveling_plan(plan)
