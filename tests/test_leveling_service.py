"""Testes para o serviço de geração de nivelamento."""

from backend.domain.models.leveling import GapExplanation, LevelingPlan, StudyStep
from backend.services.leveling_service import _build_study_order, _load_prompt_template


class TestStudyOrder:
    def test_critical_first(self):
        gaps = [
            GapExplanation(gap_name="A", importance="Important", current_score=50.0),
            GapExplanation(gap_name="B", importance="Critical", current_score=30.0),
            GapExplanation(gap_name="C", importance="Helpful", current_score=80.0),
        ]
        order = _build_study_order(gaps)
        names = [s.gap_name for s in order]
        assert names == ["B", "A", "C"]

    def test_lowest_score_first_same_importance(self):
        gaps = [
            GapExplanation(gap_name="A", importance="Critical", current_score=50.0),
            GapExplanation(gap_name="B", importance="Critical", current_score=30.0),
        ]
        order = _build_study_order(gaps)
        assert order[0].gap_name == "B"
        assert order[1].gap_name == "A"

    def test_empty_gaps(self):
        assert _build_study_order([]) == []

    def test_orders_sequential(self):
        gaps = [
            GapExplanation(gap_name="A", importance="Critical", current_score=40.0),
            GapExplanation(gap_name="B", importance="Important", current_score=60.0),
        ]
        order = _build_study_order(gaps)
        for i, s in enumerate(order):
            assert s.order == i + 1

    def test_completed_default_false(self):
        gaps = [GapExplanation(gap_name="A", importance="Critical", current_score=40.0)]
        order = _build_study_order(gaps)
        assert order[0].completed is False


class TestPromptTemplate:
    def test_prompt_loads(self):
        template = _load_prompt_template()
        assert template is not None
        assert len(template) > 50

    def test_prompt_contains_structure_keywords(self):
        template = _load_prompt_template()
        assert "why_important" in template
        assert "explanation" in template
        assert "calculus_example" in template
        assert "exercise" in template
        assert "exercise_answer" in template

    def test_prompt_contains_gap_placeholder(self):
        template = _load_prompt_template()
        assert "{gap_name}" in template
        assert "{importance}" in template

    def test_fallback_prompt_if_file_missing(self):
        from backend.services.leveling_service import _fallback_prompt

        fallback = _fallback_prompt()
        assert "{gap_name}" in fallback
        assert "{importance}" in fallback


class TestLevelingPlanModel:
    def test_plan_creation(self):
        from uuid import uuid4

        plan = LevelingPlan(
            readiness_id=uuid4(),
            explanations=[
                GapExplanation(gap_name="Derivadas", importance="Critical", current_score=45.0)
            ],
            study_order=[StudyStep(order=1, gap_name="Derivadas")],
            total_gaps=1,
        )
        assert plan.total_gaps == 1
        assert plan.explanations[0].gap_name == "Derivadas"

    def test_plan_defaults(self):
        from uuid import uuid4

        plan = LevelingPlan(readiness_id=uuid4())
        assert plan.total_gaps == 0
        assert plan.total_completed == 0
        assert plan.student_id == "anonymous"
        assert plan.explanations == []
        assert plan.study_order == []

    def test_gap_explanation_defaults(self):
        expl = GapExplanation(gap_name="Teste")
        assert expl.why_important == ""
        assert expl.explanation == ""
        assert expl.calculus_example == ""
        assert expl.exercise == ""
        assert expl.exercise_answer == ""
        assert expl.importance == "Helpful"
        assert expl.current_score == 0.0
