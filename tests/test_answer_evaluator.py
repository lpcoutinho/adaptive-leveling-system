"""Testes para o avaliador de respostas LLM."""

import pytest

from backend.llm.evaluators.answer_evaluator import AnswerEvaluator, EvaluationResult


class TestMcqEvaluation:
    """Testes para avaliação determinística de múltipla escolha."""

    def test_correct_answer(self):
        result = AnswerEvaluator.evaluate_mcq("a", "a")
        assert result.score == 100.0
        assert "correta" in result.justification.lower()

    def test_wrong_answer(self):
        result = AnswerEvaluator.evaluate_mcq("a", "b")
        assert result.score == 0.0
        assert "incorreta" in result.justification.lower()

    def test_case_insensitive(self):
        result = AnswerEvaluator.evaluate_mcq("Option A", "OPTION A")
        assert result.score == 100.0


@pytest.mark.asyncio
async def test_answer_evaluator_loads_prompt():
    """Testa que o avaliador carrega os templates corretamente."""
    evaluator = AnswerEvaluator()
    assert "{{question_text}}" in evaluator._single_prompt_template
    assert "{{questions_json}}" in evaluator._batch_prompt_template


def test_evaluation_result_model():
    """Valida o modelo de resultado de avaliação."""
    res = EvaluationResult(score=85.5, justification="Bom raciocínio")
    assert res.score == 85.5
    assert res.justification == "Bom raciocínio"
