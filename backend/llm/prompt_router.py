"""Sistema de roteamento e versionamento de prompts com telemetria."""

import os
from enum import StrEnum

from loguru import logger
from opentelemetry import trace


class PromptUseCase(StrEnum):
    """Casos de uso suportados pelo sistema de prompts."""

    PREREQUISITE_EXTRACTOR = "prerequisite_extractor"
    ASSESSMENT_GENERATOR = "assessment_generator"
    ANSWER_EVALUATOR = "answer_evaluator"
    ANSWER_EVALUATOR_BATCH = "answer_evaluator_batch"
    LEVELING_GENERATOR = "leveling_generator"


class PromptRouter:
    """Gerencia roteamento e versionamento de prompts com telemetria.

    Este sistema permite:
    - Carregar diferentes versões do mesmo prompt (v1, v2, etc.)
    - Rastrear uso de prompts via OpenTelemetry
    - Suportar A/B testing de prompts
    """

    def __init__(self):
        self._tracer = trace.get_tracer(__name__)
        self._prompts_dir = self._get_prompts_dir()

    def _get_prompts_dir(self) -> str:
        """Retorna o diretório onde os prompts estão armazenados."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        prompts_dir = os.path.join(current_dir, "prompts")

        if not os.path.exists(prompts_dir):
            logger.warning(f"Diretório de prompts não encontrado: {prompts_dir}")
            prompts_dir = "backend/llm/prompts"

        return prompts_dir

    def get_prompt(self, use_case: PromptUseCase, version: str = "v1") -> str:
        """Retorna o prompt solicitado com rastreabilidade.

        Args:
            use_case: O caso de uso do prompt.
            version: A versão do prompt (padrão: "v1").

        Returns:
            O conteúdo do prompt como string.

        Raises:
            FileNotFoundError: Se o arquivo do prompt não existir.
        """
        with self._tracer.start_as_current_span("prompt.load") as span:
            span.set_attribute("prompt.use_case", use_case.value)
            span.set_attribute("prompt.version", version)

            experiment_id = os.getenv("PROMPT_EXPERIMENT_ID", "default")
            span.set_attribute("prompt.experiment_id", experiment_id)

            filename = f"{use_case.value}_{version}.txt"
            path = os.path.join(self._prompts_dir, filename)

            logger.debug(f"Carregando prompt: {filename}")

            if not os.path.exists(path):
                error_msg = f"Prompt não encontrado: {path}"
                logger.error(error_msg)
                span.set_attribute("prompt.error", error_msg)
                raise FileNotFoundError(error_msg)

            with open(path, encoding="utf-8") as f:
                content = f.read()

            span.set_attribute("prompt.length", len(content))
            logger.info(f"Prompt carregado: {filename} ({len(content)} caracteres)")

            return content

    def list_versions(self, use_case: PromptUseCase) -> list[str]:
        """Lista todas as versões disponíveis para um caso de uso.

        Args:
            use_case: O caso de uso para listar versões.

        Returns:
            Lista de versões disponíveis (ex: ["v1", "v2"]).
        """
        if not os.path.exists(self._prompts_dir):
            return []

        versions = []
        prefix = f"{use_case.value}_"

        for filename in os.listdir(self._prompts_dir):
            if filename.startswith(prefix) and filename.endswith(".txt"):
                version = filename.replace(prefix, "").replace(".txt", "")
                versions.append(version)

        return sorted(versions)


_router_instance: PromptRouter | None = None


def get_prompt_router() -> PromptRouter:
    """Retorna a instância singleton do PromptRouter."""
    global _router_instance
    if _router_instance is None:
        _router_instance = PromptRouter()
    return _router_instance
