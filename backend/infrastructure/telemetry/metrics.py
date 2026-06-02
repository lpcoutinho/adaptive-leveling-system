"""Configuração de métricas customizadas."""

# Placeholder para métricas (prom-client ou similar futuramente)
from backend.infrastructure.telemetry.logger import log


def record_llm_latency(provider: str, latency: float):
    """Registra latência de chamadas LLM."""
    log.debug(f"LLM Latency | Provider: {provider} | Duration: {latency:.2f}s")


def record_workflow_completion(status: str):
    """Registra conclusão de workflows."""
    log.info(f"Workflow Status: {status}")
