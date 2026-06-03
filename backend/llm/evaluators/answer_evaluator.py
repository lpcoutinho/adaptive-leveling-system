"""Avaliador de respostas usando LLM-as-a-Judge."""

import os

from pydantic import BaseModel, Field

from backend.llm.factory import LLMFactory


class EvaluationResult(BaseModel):
    score: float = Field(ge=0.0, le=100.0)
    justification: str


class AnswerEvaluator:
    """Avalia respostas abertas (SA/Calc) usando LLM."""

    def __init__(self):
        self._prompt_template = self._load_prompt()

    def _load_prompt(self) -> str:
        path = os.path.join(os.path.dirname(__file__), "..", "prompts", "answer_evaluator_v1.txt")
        with open(path, encoding="utf-8") as f:
            return f.read()

    async def evaluate(
        self,
        question_text: str,
        question_type: str,
        expected_answer: str,
        student_answer: str,
    ) -> EvaluationResult:
        prompt = (
            self._prompt_template.replace("{{question_text}}", question_text)
            .replace("{{question_type}}", question_type)
            .replace("{{expected_answer}}", expected_answer)
            .replace("{{student_answer}}", student_answer)
        )
        llm = LLMFactory.get_provider()
        return await llm.generate_structured(prompt, response_model=EvaluationResult)

    @staticmethod
    def evaluate_mcq(student_answer: str, correct_answer: str) -> EvaluationResult:
        """Avaliação determinística para múltipla escolha."""
        correct = student_answer.strip().lower() == correct_answer.strip().lower()
        return EvaluationResult(
            score=100.0 if correct else 0.0,
            justification="Resposta correta!" if correct else "Resposta incorreta.",
        )
