"""Testes para o avaliador de respostas via LLM."""

from backend.llm.evaluators.answer_evaluator import AnswerEvaluator, EvaluationResult


class TestMcqEvaluation:
    def test_correct_answer(self):
        # Aceita 'correto' ou 'correta'
        result = AnswerEvaluator.evaluate_mcq("A", "a")
        assert result.score == 100.0
        assert "corret" in result.justification.lower()

    def test_wrong_answer(self):
        # Aceita 'incorreto' ou 'incorreta'
        result = AnswerEvaluator.evaluate_mcq("A", "B")
        assert result.score == 0.0
        assert "incorret" in result.justification.lower()

    def test_case_insensitive(self):
        result = AnswerEvaluator.evaluate_mcq("opcao a", "OPCAO A")
        assert result.score == 100.0


def test_answer_evaluator_loads_prompt():
    evaluator = AnswerEvaluator()
    assert evaluator._single_prompt_template is not None
    assert "{{student_answer}}" in evaluator._single_prompt_template
    assert evaluator._batch_prompt_template is not None
    assert "{{questions_json}}" in evaluator._batch_prompt_template


def test_evaluation_result_model():
    res = EvaluationResult(score=85.0, justification="Muito bom")
    assert res.score == 85.0
    assert res.justification == "Muito bom"
