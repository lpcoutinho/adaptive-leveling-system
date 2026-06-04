"""Implementação de mock para provedor de LLM."""

import json
from typing import Any, TypeVar

from pydantic import BaseModel

from backend.llm.base.interface import ILLMProvider

T = TypeVar("T", bound=BaseModel)


class MockProvider(ILLMProvider):
    """Provider de mock para testes e desenvolvimento offline."""

    def __init__(self):
        self._responses: dict[str, Any] = {}

    def set_response(self, prompt_part: str, response: Any):
        """Define uma resposta para um trecho de prompt."""
        self._responses[prompt_part] = response

    async def generate_structured(self, prompt: str, response_model: type[T]) -> T:
        """Retorna uma resposta estruturada de mock."""
        for part, resp in self._responses.items():
            if part in prompt:
                if isinstance(resp, response_model):
                    return resp
                if isinstance(resp, dict):
                    return response_model.model_validate(resp)
                if isinstance(resp, str):
                    return response_model.model_validate_json(resp)

        # Lógica especial para avaliação de quiz se for Mock
        if "results" in response_model.model_fields and "questions_json" in prompt:
            # Tenta extrair IDs do prompt para gerar um mock minimamente útil
            try:
                # O prompt contém o JSON das questões
                start = prompt.find("[")
                end = prompt.rfind("]") + 1
                if start != -1 and end > start:
                    questions = json.loads(prompt[start:end])
                    mock_results = []
                    for q in questions:
                        ans = q.get("student_answer", "").strip()
                        score = min(100.0, len(ans) * 5.0) if ans else 0.0
                        mock_results.append(
                            {
                                "question_id": q.get("question_id"),
                                "score": score,
                                "justification": "Avaliada pelo Mock da IA.",
                            }
                        )
                    return response_model.model_validate({"results": mock_results})
            except Exception:  # nosec
                pass

        # Se não houver match, tenta criar uma instância válida com campos obrigatórios vazios
        try:
            return response_model()
        except Exception:
            # Fallback para campos individuais
            kwargs: dict[str, object] = {}
            for name, field in response_model.model_fields.items():
                ann = field.annotation
                if ann is str:
                    kwargs[name] = "placeholder"
                elif ann is float:
                    kwargs[name] = 0.0
                elif ann is int:
                    kwargs[name] = 0
                elif ann is bool:
                    kwargs[name] = False
                elif ann is list or getattr(ann, "__origin__", None) is list:
                    kwargs[name] = []
                elif ann is dict or getattr(ann, "__origin__", None) is dict:
                    kwargs[name] = {}
                else:
                    kwargs[name] = None
            return response_model.model_construct(**kwargs)  # type: ignore[arg-type]

    async def generate_text(self, prompt: str) -> str:
        """Retorna um texto de mock."""
        for part, resp in self._responses.items():
            if part in prompt:
                return str(resp)
        return "Mock response for prompt"

    def get_provider_name(self) -> str:
        """Retorna o nome do provider."""
        return "mock"
