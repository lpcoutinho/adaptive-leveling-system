"""Testes para o avaliador de respostas."""

import pytest

from backend.llm.evaluators.answer_evaluator import AnswerEvaluator, EvaluationResult


class TestMcqEvaluation:
    """Testes para avaliação determinística de múltipla escolha."""

    def test_correct_answer(self):
        result = AnswerEvaluator.evaluate_mcq("2x", "2x")
        assert result.score == 100.0
        assert "correta" in result.justification.lower()

    def test_wrong_answer(self):
        result = AnswerEvaluator.evaluate_mcq("3x", "2x")
        assert result.score == 0.0
        assert (
            "incorreta" in result.justification.lower()
            or "incorreta" in result.justification.lower()
        )

    def test_case_insensitive(self):
        result = AnswerEvaluator.evaluate_mcq(" 2X ", "2x")
        assert result.score == 100.0


@pytest.mark.asyncio
async def test_answer_evaluator_loads_prompt():
    """Testa que o evaluador carrega o template corretamente."""
    evaluator = AnswerEvaluator()
    assert "{{question_text}}" in evaluator._prompt_template
    assert "{{expected_answer}}" in evaluator._prompt_template
    assert "{{student_answer}}" in evaluator._prompt_template


@pytest.mark.asyncio
async def test_evaluation_result_model():
    """Testa validação do modelo EvaluationResult."""
    r = EvaluationResult(score=75.0, justification="Bom trabalho")
    assert r.score == 75.0
    assert r.justification == "Bom trabalho"

    with pytest.raises(ValueError):
        EvaluationResult(score=150.0, justification="Invalido")
