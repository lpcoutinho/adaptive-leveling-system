"""Módulo de métricas para monitoramento de prompts e chamadas LLM."""

from loguru import logger
from opentelemetry import metrics

meter = metrics.get_meter(__name__)

prompt_usage_counter = meter.create_counter(
    "prompt.usage",
    description="Número de vezes que cada versão de prompt foi usada",
)

llm_latency_histogram = meter.create_histogram(
    "llm.latency",
    description="Latência das chamadas LLM em milissegundos",
    unit="ms",
)

llm_success_counter = meter.create_counter(
    "llm.success",
    description="Número de chamadas LLM bem-sucedidas",
)

llm_failure_counter = meter.create_counter(
    "llm.failure",
    description="Número de chamadas LLM que falharam",
)

token_usage_counter = meter.create_counter(
    "llm.tokens",
    description="Número de tokens usados (input, output, total)",
    unit="tokens",
)

hallucination_counter = meter.create_counter(
    "llm.hallucination",
    description="Número de alucinações detectadas",
)


def record_prompt_use(
    use_case: str,
    version: str,
    experiment_id: str | None = None,
) -> None:
    """Registra o uso de um prompt."""
    attributes = {
        "prompt.use_case": use_case,
        "prompt.version": version,
    }
    if experiment_id:
        attributes["prompt.experiment_id"] = experiment_id
    prompt_usage_counter.add(1, attributes)
    logger.debug(f"Métrica registrada: prompt.usage {attributes}")


def record_llm_call(
    use_case: str,
    provider: str,
    model: str,
    latency_ms: float,
    success: bool,
    prompt_length: int = 0,
    response_length: int = 0,
) -> None:
    """Registra métricas de uma chamada LLM."""
    attributes = {
        "llm.use_case": use_case,
        "llm.provider": provider,
        "llm.model": model,
    }
    llm_latency_histogram.record(latency_ms, attributes)
    if success:
        llm_success_counter.add(1, attributes)
    else:
        llm_failure_counter.add(1, attributes)
    logger.debug(
        f"Métrica registrada: llm.call "
        f"(provider={provider}, model={model}, latency={latency_ms}ms, success={success})"
    )


def record_token_usage(
    use_case: str,
    prompt_tokens: int,
    completion_tokens: int,
    total_tokens: int,
    provider: str,
    model: str,
) -> None:
    """Registra o uso de tokens em uma chamada LLM."""
    base_attributes = {
        "llm.use_case": use_case,
        "llm.provider": provider,
        "llm.model": model,
    }
    token_usage_counter.add(prompt_tokens, {**base_attributes, "token.type": "input"})
    token_usage_counter.add(completion_tokens, {**base_attributes, "token.type": "output"})
    token_usage_counter.add(total_tokens, {**base_attributes, "token.type": "total"})
    logger.debug(
        f"Métrica registrada: llm.tokens "
        f"(input={prompt_tokens}, output={completion_tokens}, total={total_tokens})"
    )


def record_hallucination(
    use_case: str,
    provider: str,
    model: str,
    detected: bool,
    confidence: float = 0.0,
) -> None:
    """Registra a detecção de alucinação."""
    attributes = {
        "llm.use_case": use_case,
        "llm.provider": provider,
        "llm.model": model,
    }
    if detected:
        hallucination_counter.add(1, attributes)
        logger.warning(
            f"Alucinação detectada: use_case={use_case}, provider={provider}, "
            f"model={model}, confidence={confidence}"
        )
