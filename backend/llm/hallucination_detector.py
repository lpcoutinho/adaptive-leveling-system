"""Detector de alucinações com múltiplas estratégias de validação."""

from typing import Any

from loguru import logger
from pydantic import BaseModel, ValidationError


class HallucinationResult(BaseModel):
    """Resultado da detecção de alucinação."""

    is_hallucination: bool
    confidence: float
    reasons: list[str]
    validated_fields: dict[str, bool]
    strategy_results: dict[str, dict]


class HallucinationDetector:
    """Detector de alucinações com múltiplas estratégias.

    Estratégias:
    1. Estrutural: Valida formato e campos obrigatórios
    2. Auto-avaliação: LLM avalia sua própria resposta
    3. Consistência: Verifica contradições internas
    4. Contextual: Valida se resposta tem suporte no contexto (RAG-style)
    """

    def __init__(self, llm_provider=None):
        self._llm = llm_provider

    async def detect(
        self,
        response: Any,
        expected_model: type | None = None,
        original_prompt: str = "",
        context: str | None = None,
    ) -> HallucinationResult:
        """Executa todas as estratégias de detecção."""
        strategy_results: dict[str, dict[str, Any]] = {}

        strategy_results["structural"] = self._validate_structure(response, expected_model)

        self_eval: dict[str, Any] = {"is_hallucination": False, "confidence": 0.0, "reasons": []}
        if self._llm and original_prompt:
            try:
                self_eval = await self._self_evaluation(response, original_prompt)
            except Exception as e:
                logger.warning(f"Auto-avaliação falhou: {e}")
                self_eval = {
                    "is_hallucination": False,
                    "confidence": 0.0,
                    "reasons": ["Auto-avaliação falhou"],
                    "error": str(e),
                }
        strategy_results["self_evaluation"] = self_eval

        strategy_results["consistency"] = self._check_consistency(response)

        contextual: dict[str, Any] = {"is_hallucination": False, "confidence": 0.0, "reasons": []}
        if context and self._llm:
            try:
                contextual = await self._validate_context(response, context)
            except Exception as e:
                logger.warning(f"Validação contextual falhou: {e}")
                contextual = {
                    "is_hallucination": False,
                    "confidence": 0.0,
                    "reasons": ["Validação contextual falhou"],
                    "error": str(e),
                }
        strategy_results["contextual"] = contextual

        return self._aggregate_results(strategy_results)

    def _validate_structure(
        self, response: Any, expected_model: type | None = None
    ) -> dict[str, Any]:
        """Valida estrutura e campos obrigatórios da resposta."""
        result: dict[str, Any] = {
            "is_hallucination": False,
            "confidence": 0.0,
            "reasons": [],
            "validated_fields": {},
        }
        try:
            if expected_model is not None:
                try:
                    if isinstance(response, dict):
                        expected_model(**response)
                    elif not isinstance(response, expected_model):
                        if hasattr(response, "model_dump"):
                            expected_model(**response.model_dump())
                        else:
                            expected_model(**response)
                except (ValidationError, TypeError) as e:
                    result["is_hallucination"] = True
                    result["confidence"] = 1.0
                    result["reasons"].append(f"Erro de validação estrutural: {str(e)}")

            if hasattr(response, "model_fields"):
                for field_name, field_info in response.model_fields.items():
                    value = getattr(response, field_name, None)
                    is_required = field_info.is_required()
                    result["validated_fields"][field_name] = True
                    if is_required and value is None:
                        result["is_hallucination"] = True
                        result["reasons"].append(f"Campo obrigatório vazio: {field_name}")
                    if (
                        isinstance(field_info.annotation, type)
                        and issubclass(field_info.annotation, list)
                        and value == []
                    ):
                        result["is_hallucination"] = True
                        result["reasons"].append(f"Lista vazia: {field_name}")
        except Exception as e:
            result["is_hallucination"] = True
            result["confidence"] = 1.0
            result["reasons"].append(f"Erro na validação estrutural: {str(e)}")

        if not result["is_hallucination"]:
            result["confidence"] = 1.0
            result["reasons"].append("Estrutura válida")

        return result

    async def _self_evaluation(self, response: Any, prompt: str) -> dict[str, Any]:
        """Auto-avaliação: LLM analisa se sua resposta contém alucinações."""
        logger.debug("Auto-avaliação: implementação simplificada")
        return {
            "is_hallucination": False,
            "confidence": 0.5,
            "reasons": ["Auto-avaliação não implementada"],
        }

    def _check_consistency(self, response: Any) -> dict[str, Any]:
        """Verifica consistência interna: duplicatas e valores fora de faixa."""
        result: dict[str, Any] = {
            "is_hallucination": False,
            "confidence": 0.0,
            "reasons": [],
        }
        try:
            if hasattr(response, "model_dump"):
                data = response.model_dump()
            elif isinstance(response, dict):
                data = response
            else:
                return result

            for key, value in data.items():
                if isinstance(value, list) and len(value) > 1:
                    seen = set()
                    duplicates = []
                    for item in value:
                        item_str = str(item)
                        if item_str in seen:
                            duplicates.append(item_str)
                        seen.add(item_str)
                    if duplicates:
                        result["is_hallucination"] = True
                        result["reasons"].append(
                            f"Duplicatas encontradas em {key}: {duplicates[:3]}"
                        )

                is_score_field = key.endswith("_score") or key.endswith("_percentage")
                if is_score_field and isinstance(value, int | float) and (value < 0 or value > 100):
                    result["is_hallucination"] = True
                    result["reasons"].append(f"Valor fora de faixa em {key}: {value}")
        except Exception as e:
            logger.debug(f"Erro na verificação de consistência: {e}")

        if not result["is_hallucination"]:
            result["confidence"] = 1.0
            result["reasons"].append("Consistente")

        return result

    async def _validate_context(self, response: Any, context: str) -> dict[str, Any]:
        """Verifica se resposta tem suporte no contexto (RAG-style)."""
        logger.debug("Validação contextual: implementação simplificada")
        return {
            "is_hallucination": False,
            "confidence": 0.5,
            "reasons": ["Validação contextual não implementada"],
        }

    def _aggregate_results(self, strategy_results: dict[str, dict]) -> HallucinationResult:
        """Agrega resultados de todas as estratégias de detecção."""
        all_reasons = []
        hallucination_votes = 0
        total_confidence = 0.0
        validated_fields = {}

        for strategy, result in strategy_results.items():
            if result.get("is_hallucination"):
                hallucination_votes += 1
                all_reasons.extend([f"[{strategy}] {r}" for r in result.get("reasons", [])])
            total_confidence += result.get("confidence", 0.0)
            for field, is_valid in result.get("validated_fields", {}).items():
                validated_fields[field] = is_valid

        avg_confidence = total_confidence / len(strategy_results) if strategy_results else 0.0
        is_hallucination = hallucination_votes >= len(strategy_results) / 2 or avg_confidence > 0.8
        if not all_reasons:
            all_reasons.append("Nenhuma alucinação detectada")

        return HallucinationResult(
            is_hallucination=is_hallucination,
            confidence=avg_confidence,
            reasons=all_reasons,
            validated_fields=validated_fields,
            strategy_results=strategy_results,
        )

    def _format_response(self, response: Any) -> str:
        """Formata a resposta como string para avaliação."""
        import json

        if hasattr(response, "model_dump_json"):
            content = response.model_dump_json(indent=2)
            assert isinstance(content, str)
            return content
        elif isinstance(response, dict):
            return json.dumps(response, indent=2, ensure_ascii=False)
        else:
            return str(response)
