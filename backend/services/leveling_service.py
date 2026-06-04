"""Serviço de geração de conteúdo de nivelamento."""

from uuid import UUID

from loguru import logger

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
from backend.llm.prompt_router import PromptUseCase, get_prompt_router

IMPORTANCE_WEIGHTS = {"Critical": 3.0, "Important": 2.0, "Helpful": 1.0}


def _load_prompt_template() -> str:
    """Carrega o template do prompt de geração de nivelamento."""
    router = get_prompt_router()
    return router.get_prompt(PromptUseCase.LEVELING_GENERATOR)


def _fallback_prompt() -> str:
    return (
        "Gere uma explicação educacional para o gap '{gap_name}' "
        "(importância: {importance}, score atual: {current_score}%). "
        "Inclua: why_important, explanation, discipline_example, exercise, exercise_answer."
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
    force_regenerate: bool = False,
) -> LevelingPlan:
    logger.info(
        f"Iniciando geração de plano de nivelamento para sessão {session_id}, "
        f"readiness {readiness_id}..."
    )
    existing = await get_plan_by_readiness(readiness_id)
    if existing and not force_regenerate:
        logger.info(
            f"Plano de nivelamento existente encontrado para readiness {readiness_id}. "
            "Reutilizando..."
        )
        return existing

    result = await get_readiness_by_id(readiness_id)
    if not result:
        result = await get_readiness_by_session(session_id)
    if not result:
        logger.error(
            f"Resultado de prontidão não encontrado para sessão {session_id}, "
            f"readiness {readiness_id}."
        )
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
        except Exception as e:
            logger.error(
                f"Erro ao gerar explicação para gap '{gap.prerequisite_name}': {e}. "
                f"Provider: {llm.get_provider_name()}, Model: {llm.model}"
            )
            # Fallback melhorado com explicação mais útil
            explanations.append(
                GapExplanation(
                    gap_name=gap.prerequisite_name,
                    importance=gap.importance,
                    current_score=gap.score,
                    why_important=f"{gap.prerequisite_name} é fundamental para entender "
                    f"conceitos avançados desta disciplina.",
                    explanation=f"O conceito de {gap.prerequisite_name} envolve compreender "
                    f"técnicas essenciais. Revise os fundamentos e pratique com exercícios.",
                    discipline_example=f"Na disciplina, {gap.prerequisite_name} é aplicado "
                    f"para resolver problemas práticos e análises de casos reais.",
                    exercise=f"Como a IA encontrou uma instabilidade temporária, "
                    f"solicitamos que você revise um exercício base de {gap.prerequisite_name} "
                    f"em seu material de apoio para consolidar este ponto.",
                    exercise_answer=(
                        f"O gabarito detalhado para {gap.prerequisite_name} pode ser encontrado "
                        f"nos anexos da aula ou consultando o tutor. Foque em entender "
                        f"a aplicação prática do conceito."
                    ),
                )
            )

    study_order = _build_study_order(explanations)
    plan = LevelingPlan(
        readiness_id=readiness_id,
        explanations=explanations,
        study_order=study_order,
        total_gaps=len(explanations),
    )
    logger.success(f"Plano de nivelamento gerado com sucesso para readiness {readiness_id}.")
    return await save_leveling_plan(plan)
