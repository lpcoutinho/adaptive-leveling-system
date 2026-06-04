"""Avaliador de respostas usando LLM-as-a-Judge."""

import json
import os

from pydantic import BaseModel, Field

from backend.llm.factory import LLMFactory


class EvaluationResult(BaseModel):
    """Resultado de uma única avaliação."""

    score: float = Field(ge=0.0, le=100.0)
    justification: str


class BatchEvaluationItem(BaseModel):
    """Item de resultado em uma avaliação em lote."""

    question_id: str
    score: float = Field(ge=0.0, le=100.0)
    justification: str


class BatchEvaluationResult(BaseModel):
    """Resultado completo de uma avaliação em lote."""

    results: list[BatchEvaluationItem]


class AnswerEvaluator:
    """Avalia respostas abertas (SA/Calc) usando LLM."""

    def __init__(self):
        self._single_prompt_template = self._load_prompt("answer_evaluator_v1.txt")
        self._batch_prompt_template = self._load_prompt("answer_evaluator_batch_v1.txt")

    def _load_prompt(self, filename: str) -> str:
        path = os.path.join(os.path.dirname(__file__), "..", "prompts", filename)
        with open(path, encoding="utf-8") as f:
            return f.read()

    async def evaluate(
        self,
        question_text: str,
        question_type: str,
        expected_answer: str,
        student_answer: str,
    ) -> EvaluationResult:
        """Avalia uma única resposta discursiva."""
        prompt = (
            self._single_prompt_template.replace("{{question_text}}", question_text)
            .replace("{{question_type}}", question_type)
            .replace("{{expected_answer}}", expected_answer)
            .replace("{{student_answer}}", student_answer)
        )
        llm = LLMFactory.get_provider()
        return await llm.generate_structured(prompt, response_model=EvaluationResult)

    async def evaluate_batch(self, questions_data: list[dict]) -> BatchEvaluationResult:
        """Avalia múltiplas respostas discursivas em um único prompt."""
        prompt = self._batch_prompt_template.replace(
            "{{questions_json}}", json.dumps(questions_data, indent=2, ensure_ascii=False)
        )
        llm = LLMFactory.get_provider()
        return await llm.generate_structured(prompt, response_model=BatchEvaluationResult)

    @staticmethod
    def evaluate_mcq(student_answer: str, correct_answer: str) -> EvaluationResult:
        """Avaliação determinística para múltipla escolha."""
        correct = student_answer.strip().lower() == correct_answer.strip().lower()
        return EvaluationResult(
            score=100.0 if correct else 0.0,
            justification="Resposta correta!" if correct else "Resposta incorreta.",
        )
