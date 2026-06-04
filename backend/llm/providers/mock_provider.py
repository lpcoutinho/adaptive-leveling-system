"""Implementação de mock para provedor de LLM."""

import contextlib
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
            try:
                start = prompt.find("[")
                end = prompt.rfind("]") + 1
                if start != -1 and end > start:
                    questions = json.loads(prompt[start:end])
                    mock_results = []
                    for q in questions:
                        ans = q.get("student_answer", "").strip()
                        expected = q.get("expected_answer", "").strip()

                        # Determina score baseado na similaridade
                        if not ans:
                            score = 0.0
                            justification = (
                                f"Resposta em branco. A resposta correta é: {expected}. "
                                "Para resolver, leia atentamente a questão e aplique os conceitos."
                            )
                        elif len(ans) < 10:
                            score = 25.0
                            justification = (
                                f"Resposta muito breve. Você respondeu: '{ans}'. "
                                f"A resposta esperada seria mais completa: {expected}. "
                                "Tente elaborar mais incluindo a justificativa."
                            )
                        elif expected and expected.lower() in ans.lower():
                            score = 100.0
                            justification = (
                                f"Correto! A resposta '{ans}' está de acordo com o gabarito."
                            )
                        elif len(ans) > len(expected) * 0.5:
                            score = 75.0
                            justification = (
                                f"Parcialmente correto. Você respondeu: '{ans}'. "
                                f"A resposta correta completa é: {expected}. "
                                "Você está no caminho certo, mas precisa ser mais preciso."
                            )
                        else:
                            score = 50.0
                            justification = (
                                f"Incorreto. Você respondeu: '{ans}', "
                                f"mas a resposta correta é: {expected}. "
                                "Revise o conceito e tente novamente."
                            )

                        mock_results.append(
                            {
                                "question_id": q.get("question_id"),
                                "score": score,
                                "justification": justification,
                            }
                        )
                    return response_model.model_validate({"results": mock_results})
            except Exception:  # nosec
                pass

        # Lógica especial para GapExplanation (leveling)
        if response_model.__name__ == "GapExplanation" or (
            hasattr(response_model, "__name__") and "GapExplanation" in str(response_model)
        ):
            # Extrair informações do prompt se disponível
            gap_name = "Conceito Básico"
            importance = "Important"
            current_score = 50.0

            # Tentar extrair valores do prompt
            if "**Conceito**:" in prompt or "- **Conceito**:" in prompt:
                for line in prompt.split("\n"):
                    if "Conceito" in line and ":" in line:
                        gap_name = line.split(":")[-1].strip().strip("*")
                        break
            if "Importância" in prompt and ":" in prompt:
                for line in prompt.split("\n"):
                    if "Importância" in line and ":" in line:
                        importance = line.split(":")[-1].strip().strip("() ")
                        break
            if "Nível atual do aluno" in prompt and ":" in prompt:
                for line in prompt.split("\n"):
                    if "Nível atual do aluno" in line and ":" in line:
                        with contextlib.suppress(ValueError):
                            current_score = float(line.split(":")[-1].strip().rstrip("%"))
                        break

            return response_model.model_validate(
                {
                    "gap_name": gap_name,
                    "importance": importance,
                    "current_score": current_score,
                    "why_important": f"{gap_name} é fundamental para entender os conceitos "
                    f"avançados desta disciplina. Sem este conhecimento, você terá dificuldade "
                    f"em tópicos futuros que dependem diretamente deste conceito.",
                    "explanation": f"O conceito de {gap_name} envolve compreender como "
                    f"aplicar técnicas e fórmulas específicas. É importante praticar "
                    f"regularmente para consolidar o entendimento. Comece com problemas "
                    f"simples e aumente a complexidade gradualmente.",
                    "discipline_example": f"Na disciplina, {gap_name} é usado para resolver "
                    f"problemas práticos de alta complexidade. Por exemplo, ao analisar "
                    f"um caso real, aplicamos os fundamentos de {gap_name} para extrair "
                    f"conclusões precisas.",
                    "exercise": f"Resolva o seguinte problema prático de {gap_name}: "
                    f"Dada uma situação onde {gap_name} deve ser aplicado para "
                    f"encontrar um valor ótimo, calcule o resultado final considerando "
                    f"os parâmetros padrão do tema.",
                    "exercise_answer": f"Resolução do exercício de {gap_name}: "
                    f"1) Identificamos que a variável principal segue a regra de {gap_name}. "
                    f"2) Aplicamos a transformação necessária. "
                    f"3) O resultado final satisfaz as condições iniciais de {gap_name}. "
                    f"Resposta: O valor foi calculado com sucesso via princípios de {gap_name}.",
                }
            )

        try:
            return response_model()
        except Exception:
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

    @property
    def model(self) -> str:
        """Retorna o modelo usado."""
        return "mock"
